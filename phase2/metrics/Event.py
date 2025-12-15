from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class EventType(Enum):
    REQUEST_GENERATED = 1
    REQUEST_ASSIGNED = 2
    REQUEST_PROPOSAL_ACCEPTED = 3
    REQUEST_PROPOSAL_DENIED = 4
    REQUEST_EXPIRED = 5
    REQUEST_PICKED = 6
    REQUEST_DELIVERED = 7
    BEHAVIOUR_CHANGED = 8 # Behaviour when a driver changes behaviour
    DRIVER_IDLE = 9
    DRIVER_GENERATED_BEHAVIOUR = 10 # Behaviour when a driver is generated


@dataclass
class Event:
    timestamp: int
    event_type: EventType
    driver_id: Optional[int]
    request_id: Optional[int]
    wait_time: Optional[int]
    behaviour_name: Optional[str] = None

    # Validation upon initialization
    def __post_init__(self):
        if not isinstance(self.event_type, EventType):
            raise TypeError("event_type must be an instance of EventType Enum")

        if not isinstance(self.event_type, EventType):
            raise TypeError("event_type must be EventType")

        if not isinstance(self.timestamp, int):
            raise TypeError("timestamp must be int")

        for attr in ["driver_id", "request_id", "wait_time"]:
            value = getattr(self, attr)
            if value is not None and not isinstance(value, int):
                raise TypeError(f"{attr} must be int or None")
        if self.behaviour_name is not None and not isinstance(self.behaviour_name, str):
            raise TypeError("behaviour_name must be str or None")
