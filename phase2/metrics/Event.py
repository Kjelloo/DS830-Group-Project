from dataclasses import dataclass
from enum import Enum
from typing import Optional


class EventType(Enum):
    REQUEST_GENERATED = 1
    REQUEST_PROPOSAL = 2
    REQUEST_ASSIGNED = 3
    REQUEST_DENIED = 4
    REQUEST_EXPIRED = 5
    REQUEST_DELIVERED = 6
    BEHAVIOUR_CHANGED = 7
    DRIVER_IDLE = 8


@dataclass
class Event:
    timestamp: int
    event_type: EventType
    driver_id: Optional[int]
    request_id: Optional[int]
    wait_time: Optional[int]

    # Validation upon initialization
    def __post_init__(self):
        if not isinstance(self.event_type, EventType):
            raise TypeError("event_type must be an instance of EventType Enum")

        if not isinstance(self.event_type, EventType):
            raise TypeError("event_type must be EventType")

        for attr in ["driver_id", "request_id", "wait_time"]:
            value = getattr(self, attr)
            if value is not None and not isinstance(value, int):
                raise TypeError(f"{attr} must be int or None")
