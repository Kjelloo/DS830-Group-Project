from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Point import Point
    from metrics.EventManager import EventManager
    from metrics.Event import Event, EventType

eventManager = EventManager(filepath="metrics/events.csv")


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

    def __str__(self) -> str:
        return f"Request(id={self.id}, pick_up={self.pick_up}, drop_off={self.drop_off}, " \
               f"creation_time={self.creation_time}, status={self.status}, " \
               f"assigned_driver={self.assigned_driver}, wait_time={self.wait_time})"

    def is_active(self) -> bool:
        """
        Returns true if the request is still waiting,
        assigned or picked (that is, not delivered or expired).
        """
        if self.status == RequestStatus.DELIVERED or self.status == RequestStatus.EXPIRED:
            return False
        else:
            return True

    def mark_assigned(self, driver_id: int, time: int) -> None:
        """
        Marks the request as assigned.
        """
        self.assigned_driver = driver_id
        self.status = RequestStatus.ASSIGNED

        eventManager.add_event(Event(time, EventType.REQUEST_ASSIGNED, driver_id, self.id, None))

    def mark_picked(self, time: int) -> None:
        self.status = RequestStatus.PICKED

        eventManager.add_event(Event(time, EventType.REQUEST_PICKED, self.id, self.id, None))

    def mark_delivered(self, time: int) -> None:
        self.status = RequestStatus.DELIVERED

        eventManager.add_event(Event(time, EventType.REQUEST_DELIVERED, self.assigned_driver, self.id, None))

    def mark_expired(self, time: int) -> None:
        self.status = RequestStatus.EXPIRED

        eventManager.add_event(Event(time, EventType.REQUEST_EXPIRED, None, self.id, None))

    def update_wait(self, current_time: int) -> None:
        """
        Updates wait_time according to current_time.
        """
        self.wait_time = current_time - self.creation_time
