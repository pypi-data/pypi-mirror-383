"""Public API for the Flow SDK.

Exports the primary client and essential models for GPU workload orchestration.
This is the stable public API - everything else is internal.
"""

# Primary client and legacy Flow class
# Decorators for convenience
from flow.sdk import decorators
from flow.sdk.client import Client, Flow

# Essential models
from flow.sdk.models import (
    AvailableInstance,
    Instance,
    Task,
    TaskConfig,
    TaskStatus,
    User,
    Volume,
    VolumeSpec,
)

try:
    from flow.sdk.models import Resources  # type: ignore[attr-defined]
except Exception:  # noqa: BLE001

    class Resources:  # pragma: no cover - placeholder for legacy import paths
        pass


try:
    from flow.sdk.models import RunParams  # type: ignore[attr-defined]
except Exception:  # noqa: BLE001
    try:
        from flow.sdk.models.run_params import (
            RunParameters as RunParams,  # type: ignore[assignment]
        )
    except Exception:  # noqa: BLE001

        class RunParams:  # pragma: no cover - placeholder for legacy import paths
            pass


try:
    from flow.sdk.models import TaskSpec  # type: ignore[attr-defined]
except Exception:  # noqa: BLE001
    try:
        from flow.domain.ir.spec import TaskSpec  # type: ignore[no-redef]
    except Exception:  # noqa: BLE001

        class TaskSpec:  # pragma: no cover - placeholder for legacy import paths
            pass


__all__ = [
    "AvailableInstance",
    # Primary client (new)
    "Client",
    # Legacy client (deprecated but maintained)
    "Flow",
    # Instance types
    "Instance",
    "Resources",
    "RunParams",
    # Core models
    "Task",
    "TaskConfig",
    "TaskSpec",
    "TaskStatus",
    # User
    "User",
    # Storage
    "Volume",
    "VolumeSpec",
    # Utilities
    "decorators",
]
