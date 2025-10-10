"""Local testing provider implementation."""

import logging
import subprocess
import time
import uuid
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from flow.adapters.providers.interfaces import IProviderInit

from flow.adapters.providers.adapter import ProviderAdapter
from flow.adapters.providers.base import PricingModel, ProviderCapabilities
from flow.adapters.providers.builtin.local.config import LocalTestConfig
from flow.adapters.providers.builtin.local.executor import (
    ContainerTaskExecutor,
    ProcessTaskExecutor,
    TaskExecutor,
)
from flow.adapters.providers.builtin.local.logs import LocalLogManager
from flow.adapters.providers.builtin.local.storage import LocalStorage
from flow.application.config.config import Config

# Legacy interfaces removed - now using ProviderAdapter
from flow.errors import TaskNotFoundError, VolumeError
from flow.sdk.models import AvailableInstance, Task, TaskConfig, TaskStatus, Volume

logger = logging.getLogger(__name__)


class LocalProvider(ProviderAdapter):
    """Local provider for testing Flow SDK functionality without cloud infrastructure.

    Provides high-fidelity simulation of Mithril behavior using Docker containers
    or local processes. Enables sub-second test iterations while maintaining
    behavioral accuracy.
    """

    def __init__(self, config: Config):
        """Initialize local provider.

        Args:
            config: SDK configuration object
        """
        if config.provider != "local":
            raise ValueError(f"LocalProvider requires 'local' provider, got: {config.provider}")

        # Define local provider capabilities
        capabilities = ProviderCapabilities(
            supports_spot_instances=False,
            supports_on_demand=True,
            supports_multi_node=False,  # Local provider is single-node only
            supports_attached_storage=True,
            supports_shared_storage=True,  # Local filesystem is shared
            storage_types=["volume", "directory"],
            requires_ssh_keys=False,  # Local execution doesn't need SSH
            supports_console_access=True,  # Direct local access
            pricing_model=PricingModel.FIXED,  # No cost for local
            supports_reservations=False,
            supported_regions=["local"],
            max_instances_per_task=1,  # Local provider runs one task at a time
            max_storage_per_instance_gb=None,  # Limited by local disk
            supports_custom_images=True,  # Docker support
            supports_gpu_passthrough=True,  # If Docker has GPU access
            supports_live_migration=False,
        )

        # Initialize parent class
        super().__init__(name="local", capabilities=capabilities)

        self.config = config

        # Extract local-specific configuration from provider_config
        # For now, use defaults - could be extended to read from config.provider_config
        self.local_config = LocalTestConfig.default()
        self.tasks: dict[str, Task] = {}
        self.storage = LocalStorage(self.local_config.storage_dir)
        self.log_manager = LocalLogManager(self.local_config.storage_dir)

        # Choose executor based on config and availability
        if self.local_config.use_docker:
            try:
                # Try to create Docker executor
                self.executor: TaskExecutor = ContainerTaskExecutor(self.local_config)
                logger.info("Using Docker executor for local tasks")
            except Exception as e:  # noqa: BLE001
                # Fall back to process executor if Docker is not available
                logger.warning(f"Docker not available ({e}), falling back to process executor")
                self.local_config.use_docker = False
                self.executor = ProcessTaskExecutor(self.local_config)
        else:
            self.executor = ProcessTaskExecutor(self.local_config)

        # Initialize provider
        self._initialize()

    @classmethod
    def from_config(cls, config: Config) -> "LocalProvider":
        """Create LocalProvider from config.

        This is the standard factory method used by the SDK.

        Args:
            config: SDK configuration

        Returns:
            Initialized LocalProvider instance
        """
        return cls(config)

    def _initialize(self):
        """Initialize local provider environment."""
        # Create storage directories
        self.storage.initialize()

        # Verify Docker if needed
        if self.local_config.use_docker:
            try:
                subprocess.run(["docker", "version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                # Fall back to process executor if Docker is not available
                logger.warning("Docker not available (%s), falling back to process executor", e)
                self.local_config.use_docker = False
                self.executor = ProcessTaskExecutor(self.local_config)

        logger.info(f"LocalProvider initialized with executor: {type(self.executor).__name__}")

    def submit_task(
        self,
        instance_type: str,
        config: TaskConfig,
        volume_ids: list[str] | None = None,
    ) -> Task:
        """Submit a task for local execution.

        Args:
            instance_type: Instance type (e.g., "a100", "h100")
            config: Task configuration
            volume_ids: Optional volume IDs to attach

        Returns:
            Task object with local execution details
        """
        # Generate task ID
        task_id = f"local-{uuid.uuid4().hex[:8]}"

        # Map instance type to local resources
        resources = self.local_config.get_instance_mapping(config.instance_type)

        # Create task object
        task = Task(
            task_id=task_id,
            name=config.name,
            status=TaskStatus.PENDING,
            config=config,
            created_at=datetime.now(timezone.utc),
            instance_type=config.instance_type,
            num_instances=config.num_instances,
            region="local",
            cost_per_hour="$0.00",  # Local execution is free
            ssh_host="localhost",
            ssh_port=22000 + len(self.tasks),  # Unique port per task
            ssh_user="flow",
        )
        # Set provider after creation (PrivateAttr in Pydantic)
        task._provider = self

        # Store task
        self.tasks[task_id] = task

        # Start execution asynchronously
        self._start_task_execution(task, resources)

        return task

    def _start_task_execution(self, task: Task, resources: dict):
        """Start task execution in background."""
        try:
            # Update status and store the updated task
            updated_task = task.copy_with_updates(
                status=TaskStatus.RUNNING, started_at=datetime.now(timezone.utc)
            )
            self.tasks[task.task_id] = updated_task

            # Start log capture
            self.log_manager.start_log_capture(task.task_id)

            # Execute task
            execution = self.executor.execute_task(
                task_id=task.task_id,
                config=updated_task.config,
                resources=resources,
                log_callback=lambda line: self.log_manager.append_log(task.task_id, line),
            )

            # Store execution reference and update stored task
            final_task = updated_task.copy_with_updates(
                instances=[execution.container_id or execution.process_id]
            )
            self.tasks[task.task_id] = final_task

            # Monitor task in background
            import threading

            monitor_thread = threading.Thread(
                target=self._monitor_task, args=(final_task, execution), daemon=True
            )
            monitor_thread.start()

        except Exception as e:  # noqa: BLE001
            # Update stored task with failure status
            failed_task = task.copy_with_updates(status=TaskStatus.FAILED, message=str(e))
            self.tasks[task.task_id] = failed_task
            logger.error(f"Failed to start task {task.task_id}: {e}")

    def _monitor_task(self, task: Task, execution):
        """Monitor task execution and update status."""
        try:
            # Wait for completion
            exit_code = execution.wait()

            # Give log streaming a moment to catch up
            time.sleep(0.5)

            # Prepare completion updates
            completed_at = datetime.now(timezone.utc)
            duration_hours = (
                (completed_at - task.started_at).total_seconds() / 3600 if task.started_at else 0
            )
            hourly_rate = 0.10  # Mock rate for local testing

            # Update task status based on exit code
            if exit_code == 0:
                completed_task = task.copy_with_updates(
                    status=TaskStatus.COMPLETED,
                    completed_at=completed_at,
                    total_cost=f"${duration_hours * hourly_rate:.2f}",
                )
            else:
                completed_task = task.copy_with_updates(
                    status=TaskStatus.FAILED,
                    message=f"Task exited with code {exit_code}",
                    completed_at=completed_at,
                    total_cost=f"${duration_hours * hourly_rate:.2f}",
                )

            # Store the completed task
            self.tasks[task.task_id] = completed_task

            # Stop log capture
            self.log_manager.stop_log_capture(task.task_id)

        except Exception as e:  # noqa: BLE001
            # Update stored task with monitor failure
            failed_task = task.copy_with_updates(
                status=TaskStatus.FAILED,
                message=f"Monitor error: {e!s}",
                completed_at=datetime.now(timezone.utc),
            )
            self.tasks[task.task_id] = failed_task
            logger.error(f"Error monitoring task {task.task_id}: {e}")

    def get_task(self, task_id: str) -> Task:
        """Get task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task object

        Raises:
            TaskNotFoundError: If task doesn't exist
        """
        if task_id not in self.tasks:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return self.tasks[task_id]

    def list_tasks(
        self,
        status: TaskStatus | list[TaskStatus] | str | None = None,
        limit: int = 100,
        force_refresh: bool = False,
    ) -> list[Task]:
        """List tasks with optional filtering.

        Args:
            status: Filter by status (TaskStatus, list of TaskStatus, or string)
            limit: Maximum tasks to return
            force_refresh: Whether to force refresh (ignored for local provider)

        Returns:
            List of tasks
        """
        tasks = list(self.tasks.values())

        # Normalize status filter to a set of strings for flexible input types
        allowed_values: set[str] | None = None
        if status is not None:
            try:
                if isinstance(status, list):
                    allowed_values = {getattr(s, "value", str(s)) for s in status}
                else:
                    allowed_values = {getattr(status, "value", str(status))}
            except Exception:  # noqa: BLE001
                allowed_values = None

        if allowed_values:
            tasks = [
                t
                for t in tasks
                if getattr(getattr(t, "status", None), "value", None) in allowed_values
            ]

        # Sort by creation time (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)

        return tasks[:limit]

    def stop_task(self, task_id: str) -> bool:
        """Stop a running task.

        Args:
            task_id: Task to stop

        Returns:
            True if task was stopped successfully
        """
        try:
            task = self.get_task(task_id)

            if task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                return True  # Already stopped

            # Stop execution
            self.executor.stop_task(task_id)

            # Update stored task with cancellation status
            cancelled_task = task.copy_with_updates(
                status=TaskStatus.CANCELLED,
                completed_at=datetime.now(timezone.utc),
                message="Cancelled by user",
            )
            self.tasks[task_id] = cancelled_task
            return True
        except Exception as e:  # noqa: BLE001
            logger.error(f"Error stopping task {task_id}: {e}")
            return False

    def pause_task(self, task_id: str) -> bool:
        """Pause a running task.

        Note: Local provider does not support true pause/resume.
        This method returns False to indicate the operation is not supported.

        Args:
            task_id: Task to pause

        Returns:
            False (pause not supported for local provider)
        """
        logger.warning(f"Pause operation not supported for local provider (task {task_id})")
        return False

    def unpause_task(self, task_id: str) -> bool:
        """Unpause a paused task.

        Note: Local provider does not support true pause/resume.
        This method returns False to indicate the operation is not supported.

        Args:
            task_id: Task to unpause

        Returns:
            False (unpause not supported for local provider)
        """
        logger.warning(f"Unpause operation not supported for local provider (task {task_id})")
        return False

    def get_task_logs(self, task_id: str, tail: int = 100, log_type: str = "stdout") -> str:
        """Get task logs.

        Args:
            task_id: Task identifier
            tail: Number of lines to return from end
            log_type: Type of logs (stdout/stderr)

        Returns:
            Log content as string
        """
        task = self.get_task(task_id)

        if task.status == TaskStatus.PENDING:
            return "Task pending - no logs available yet"

        return self.log_manager.get_logs(task_id, tail=tail, log_type=log_type)

    def stream_task_logs(self, task_id: str, log_type: str = "stdout") -> Iterator[str]:
        """Stream task logs in real-time.

        Args:
            task_id: Task identifier
            log_type: Type of logs (stdout/stderr)

        Yields:
            Log lines as they become available
        """
        task = self.get_task(task_id)

        if task.status == TaskStatus.PENDING:
            yield "Task pending - waiting for execution to start..."
            # Wait for task to start
            for _ in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                if task.status != TaskStatus.PENDING:
                    break
            else:
                yield "Task failed to start"
                return

        # Stream logs
        for line in self.log_manager.stream_logs(task_id, log_type=log_type):
            yield line

            # Check if task completed
            task = self.get_task(task_id)
            if task.is_terminal:
                # Yield any final logs
                final_logs = self.log_manager.get_logs(task_id, tail=10, log_type=log_type)
                for line in final_logs.splitlines()[-5:]:
                    if not self.log_manager.has_streamed_line(task_id, line):
                        yield line
                break

    def create_volume(
        self,
        size_gb: int,
        name: str | None = None,
        interface: str = "block",
        region: str | None = None,
    ) -> Volume:
        """Create a local volume matching IStorageProvider signature."""
        volume_id = f"local-vol-{uuid.uuid4().hex[:8]}"
        volume_path = self.storage.create_volume(volume_id, size_gb)

        from flow.sdk.models import StorageInterface

        iface = StorageInterface.BLOCK if interface == "block" else StorageInterface.FILE

        return Volume(
            volume_id=volume_id,
            name=name or volume_id,
            size_gb=size_gb,
            region=region or "local",
            interface=iface,
            created_at=datetime.now(timezone.utc),
            provider_data={"path": str(volume_path)},
        )

    def delete_volume(self, volume_id: str) -> bool:
        """Delete a volume and return operation status."""
        try:
            self.storage.delete_volume(volume_id)
            return True
        except Exception:  # noqa: BLE001
            return False

    def resize_volume(self, volume_id: str, new_size_gb: int) -> None:
        """Resize a volume.

        Args:
            volume_id: Volume to resize
            new_size_gb: New size in GB
        """
        # For local testing, just update metadata
        logger.info(f"Mock resizing volume {volume_id} to {new_size_gb}GB")

    def get_volume(self, volume_id: str) -> Volume:
        """Get volume details.

        Args:
            volume_id: Volume identifier

        Returns:
            Volume object
        """
        volume_info = self.storage.get_volume_info(volume_id)
        if not volume_info:
            raise VolumeError(
                f"Volume {volume_id} not found",
                suggestions=[
                    "Check the volume ID is correct",
                    "Use 'flow volume list' to see available volumes",
                    "Ensure the volume wasn't deleted",
                ],
                error_code="VOLUME_001",
            )

        from flow.sdk.models import StorageInterface

        return Volume(
            volume_id=volume_id,
            name=volume_info.get("name", volume_id),
            size_gb=volume_info["size_gb"],
            region="local",
            interface=StorageInterface.BLOCK,
            created_at=datetime.fromisoformat(volume_info["created_at"]),
            provider_data=volume_info,
        )

    def list_volumes(self, limit: int = 100) -> list[Volume]:
        """List all volumes.

        Args:
            limit: Maximum volumes to return

        Returns:
            List of volumes
        """
        volumes = []
        for volume_id in self.storage.list_volumes()[:limit]:
            try:
                volumes.append(self.get_volume(volume_id))
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Error loading volume {volume_id}: {e}")

        return volumes

    # ---- File transfer helpers for local volumes ----

    def upload_file(
        self, volume_id: str, local_path: "Path", remote_path: str | None = None
    ) -> bool:
        try:
            vol = self.get_volume(volume_id)
            target = Path(vol.provider_data.get("path", "")) / (
                remote_path or Path(local_path).name
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            from shutil import copy2

            copy2(local_path, target)
            return True
        except Exception:  # noqa: BLE001
            return False

    def upload_directory(
        self, volume_id: str, local_path: "Path", remote_path: str | None = None
    ) -> bool:
        try:
            vol = self.get_volume(volume_id)
            base = Path(vol.provider_data.get("path", "")) / (remote_path or "")
            base.mkdir(parents=True, exist_ok=True)
            from shutil import copy2

            for f in Path(local_path).rglob("*"):
                if f.is_file():
                    rel = f.relative_to(local_path)
                    dst = base / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    copy2(f, dst)
            return True
        except Exception:  # noqa: BLE001
            return False

    def download_file(self, volume_id: str, remote_path: str, local_path: "Path") -> bool:
        try:
            vol = self.get_volume(volume_id)
            src = Path(vol.provider_data.get("path", "")) / remote_path
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            from shutil import copy2

            copy2(src, local_path)
            return True
        except Exception:  # noqa: BLE001
            return False

    def download_directory(self, volume_id: str, remote_path: str, local_path: "Path") -> bool:
        try:
            vol = self.get_volume(volume_id)
            src_base = Path(vol.provider_data.get("path", "")) / (remote_path or "")
            Path(local_path).mkdir(parents=True, exist_ok=True)
            from shutil import copy2

            for f in src_base.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(src_base)
                    dst = Path(local_path) / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    copy2(f, dst)
            return True
        except Exception:  # noqa: BLE001
            return False

    def is_volume_id(self, identifier: str) -> bool:
        return identifier.startswith("local-vol-")

    def cleanup(self):
        """Clean up all local resources."""
        # Stop all running tasks
        for task_id, task in self.tasks.items():
            if task.status == TaskStatus.RUNNING:
                try:
                    self.stop_task(task_id)
                except Exception as e:  # noqa: BLE001
                    logger.error(f"Error stopping task {task_id} during cleanup: {e}")

        # Clean up executor
        self.executor.cleanup()

        # Optionally clean storage
        if self.local_config.clean_on_exit:
            self.storage.cleanup()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()

    def prepare_task_config(self, config: TaskConfig) -> TaskConfig:
        """Prepare task configuration with local provider defaults.

        For local provider, we don't need to modify much since everything
        runs locally. Just ensure the config is valid.

        Args:
            config: The user-provided task configuration

        Returns:
            The same task configuration (no modifications needed for local)
        """
        # LocalProvider doesn't need SSH keys or regions
        # Just return the config as-is
        return config

    def find_instances(
        self,
        requirements: dict[str, Any],
        limit: int = 10,
    ) -> list["AvailableInstance"]:
        """Find available instances matching requirements.

        For local provider, we always have one "instance" available - the local machine.

        Args:
            requirements: Dictionary of requirements (instance_type, etc.)
            limit: Maximum number of instances to return

        Returns:
            List containing a single mock instance representing local execution
        """
        from flow.sdk.models import AvailableInstance

        # Get requested instance type or default to cpu.small
        instance_type = requirements.get("instance_type", "cpu.small")

        # For local provider, we always have availability
        return [
            AvailableInstance(
                allocation_id="local-instance",
                instance_type=instance_type,
                region="local",
                price_per_hour=0.0,  # Local execution is free
                status="available",
                available_quantity=1,  # One local machine
            )
        ]

    # ---- Missing ProviderPort methods ----

    def get_task_status(self, task_id: str) -> TaskStatus:
        """Get current task status.

        Args:
            task_id: Task identifier

        Returns:
            Current task status
        """
        task = self.get_task(task_id)
        return task.status

    def cancel_task(self, task_id: str) -> None:
        """Cancel a task.

        Args:
            task_id: Task identifier
        """
        self.stop_task(task_id)

    def mount_volume(self, task_id: str, volume_id: str, mount_path: str = "/mnt/volume") -> bool:
        """Mount a volume to a task.

        Args:
            task_id: Task identifier
            volume_id: Volume identifier
            mount_path: Mount path in container

        Returns:
            True if mounted successfully
        """
        try:
            # For local provider, this would involve bind mounting
            # For now, just log the operation
            self.log_operation(
                "mount_volume", task_id=task_id, volume_id=volume_id, mount_path=mount_path
            )
            return True
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to mount volume {volume_id} to task {task_id}: {e}")
            return False

    def get_init_interface(self) -> "IProviderInit":
        """Get provider initialization interface.

        Returns:
            IProviderInit implementation for local provider
        """
        from flow.adapters.providers.builtin.local.init import LocalInit

        return LocalInit()
