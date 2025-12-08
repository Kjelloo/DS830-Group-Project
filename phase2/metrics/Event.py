from dataclasses import dataclass
from enum import Enum

class EventType(Enum):
    REQUEST_GENERATED = 1
    REQUEST_PROPOSAL  = 2
    REQUEST_ASSIGNED  = 3
    REQUEST_DENIED    = 4
    REQUEST_EXPIRED   = 5
    REQUEST_DELIVERED = 6
    BEHAVIOUR_CHANGED = 7
    DRIVER_IDLE       = 8

@dataclass
class Event:
    timestamp: int
    event_type: EventType
    driver_id: int | None
    request_id: int | None
    wait_time: int | None