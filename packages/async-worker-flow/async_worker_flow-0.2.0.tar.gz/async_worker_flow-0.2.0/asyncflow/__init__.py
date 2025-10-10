"""
AsyncFlow: Async execution library with concurrent.futures-style API and advanced pipelines.
"""

from ._version import __version__
from .exceptions import (
    AsyncFlowError,
    ExecutorShutdownError,
    PipelineError,
    StageValidationError,
    TaskFailedError,
)
from .executor import AsyncExecutor, AsyncFuture, WaitStrategy
from .pipeline import Pipeline, Stage
from .tracker import StatusEvent, StatusTracker
from .types import (
    OrderedResult,
    PipelineStats,
    StatusType,
    TaskFunc,
)

__all__ = [
    "__version__",
    "AsyncExecutor",
    "AsyncFuture",
    "AsyncFlowError",
    "ExecutorShutdownError",
    "OrderedResult",
    "Pipeline",
    "PipelineError",
    "PipelineStats",
    "Stage",
    "StageValidationError",
    "StatusEvent",
    "StatusTracker",
    "StatusType",
    "TaskFailedError",
    "TaskFunc",
    "WaitStrategy",
]
