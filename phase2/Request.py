from __future__ import annotations
from phase2.Point import Point
from enum import Enum

class RequestStatus(Enum):
    WAITING = 1
    ASSIGNED = 2
    PICKED = 3
    DELIVERED = 4
    EXPIRED = 5

class Request:
    def __init__(self, id: int, pick_up: Point, drop_off: Point, creation_time: int, status: RequestStatus,
                 assigned_driver: int | None, wait_time: int) -> None:
        self.id = id
        self.pick_up = pick_up
        self.drop_off = drop_off
        self.creation_time = creation_time
        self.status = status
        self.assigned_driver = assigned_driver
        self.wait_time = wait_time

    def is_active(self) -> bool:
        """
        Returns true if the request is still waiting,
        assigned or picked (that is, not delivered or expired).
        """
        if self.status == "DELIVERED" or self.status == "EXPIRED":
            return False
        else:
            return True

    def mark_assigned(self, driver_id: int) -> None:
        """
        Marks the request as assigned.
        """
        self.assigned_driver = driver_id
        self.status = "ASSIGNED"
        # TO-DO: Implement collection of data

    def mark_picked(self, time: int) -> None:
        self.status = "PICKED"
        # TO-DO: Implement collection of data

    def mark_expired(self, time: int) -> None:
        self.status = "EXPIRED"
        # TO-DO: Implement collection of data

    def update_wait(self, current_time: int) -> None:
        """
        Updates wait_time according to current_time.
        """
        self.wait_time = current_time - self.creation_time