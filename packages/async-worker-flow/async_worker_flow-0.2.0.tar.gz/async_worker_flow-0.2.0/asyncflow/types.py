from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Literal

TaskFunc = Callable[[Any], Awaitable[Any]]
StatusType = Literal["queued", "in_progress", "completed", "failed"]


@dataclass
class OrderedResult:
    sequence_id: int
    item_id: Any
    value: Any
    error: Exception | None = None

    @property
    def is_success(self) -> bool:
        return self.error is None

    @property
    def is_failure(self) -> bool:
        return self.error is not None


@dataclass
class PipelineStats:
    items_processed: int
    items_failed: int
    items_in_flight: int
    queue_sizes: Dict[str, int]
