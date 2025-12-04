from enum import Enum

from Point import Point


class RequestStatus(Enum):
    WAITING = 1
    ASSIGNED = 2
    PICKED = 3
    DELIVERED = 4
    EXPIRED = 5


class Request:
    def __init__(self, id: int, pickup: Point, dropoff: Point, creation_time: int, status: RequestStatus,
                 assigned_driver: int | None, wait_time: int) -> None:
        self.id = id
        self.pickup = pickup
        self.dropoff = dropoff
        self.creation_time = creation_time
        self.status = status
        self.assigned_driver = assigned_driver
        self.wait_time = wait_time

    def is_active(self) -> bool:
        """
        Returns true if the request is still waiting,
        assigned or picked (that is, not delivered or expired).
        """
        pass

    def mark_assigned(self, driver_id: int) -> None:
        pass

    def mark_picked(self, time: int) -> None:
        pass

    def mark_expired(self, time: int) -> None:
        pass

    def update_wait(self, current_time: int) -> None:
        pass

    def update_status(self, status: str) -> None:
        """
        Updates wait_time according to current_time.
        """
        pass
