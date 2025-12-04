from dataclasses import dataclass
from enum import Enum

from Point import Point
from Request import Request
from behaviour.DriverBehaviour import DriverBehaviour


class DriverStatus(Enum):
    IDLE = 1,
    TO_PICKUP = 2
    TO_DROPOFF = 3


@dataclass
class DriverHistoryEntry:
    request: Request
    pickup_time: int
    dropoff_time: int


class Driver:
    def __init__(self, id: int, position: Point, speed: float, status: DriverStatus, current_request: Request | None,
                 behaviour: DriverBehaviour, history: list[DriverHistoryEntry]) -> None:
        self.id = id
        self.position = position
        self.speed = speed
        self.status = status
        self.current_request = current_request
        self.behaviour = behaviour
        self.history = history

    def assign_request(self, request: Request, current_time: int) -> None:
        pass

    def target_point(self) -> Point | None:
        """
        Returns:
            The next target. Pickup point or dropoff point depending on DriverStatus.
        """
        pass

    def step(self, dt: float) -> None:
        """
        Moves the driver towards the current target according to speed and time step dt.
        """
        pass

    def complete_pickup(self, time: int) -> None:
        """
        Updates the internal state when the pickup is reached.
        """
        pass

    def complete_dropoff(self, time: int) -> None:
        """
        Updates the internal state and history when the dropoff is reached.
        """
        pass
