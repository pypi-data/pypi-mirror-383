"""Flow Intermediate Representation (IR).

This module defines the canonical task representation that serves as the
platform contract between frontends and providers.
"""

from flow.domain.ir.schema import (
    generate_compact_schema,
    generate_task_schema,
    validate_ir_version,
)
from flow.domain.ir.spec import (
    MountSpec,
    ResourceSpec,
    RunParams,
    TaskSpec,
)

__all__ = [
    "MountSpec",
    "ResourceSpec",
    "RunParams",
    # Core IR models
    "TaskSpec",
    "generate_compact_schema",
    # Schema utilities
    "generate_task_schema",
    "validate_ir_version",
]
