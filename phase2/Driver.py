from __future__ import annotations

import math
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from phase2.Point import Point
    from phase2.Request import Request
    from phase2.behaviour.DriverBehaviour import DriverBehaviour
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
        self.dir_vector = None

    def compute_direction_vector(self) -> None:
        if self.target_point() is not None:
            x, y = self.position.x - self.target_point().x, self.position.y - self.target_point().y
            magnitude = math.sqrt(x ** 2 + y ** 2)
            x_normalized, y_normalized = (x / magnitude, y / magnitude)
            self.dir_vector = (x_normalized, y_normalized)
        else:
            self.dir_vector = None


    def assign_request(self, request: Request, current_time: int) -> None:
        # Do we need to implement assignment based on behaviour here???
        self.current_request = request
        self.status = DriverStatus.TO_PICKUP
        self.current_request.mark_assigned(self.id)
        self.compute_direction_vector()
        # TO-DO: Implement data collection

    def target_point(self) -> Point | None:
        """
        Returns:
            The next target. Pickup point or dropoff point depending on DriverStatus.
        """
        if self.status == DriverStatus.IDLE:
            return None
        elif self.status == DriverStatus.TO_PICKUP:
            return self.current_request.pickup
        elif self.status == DriverStatus.TO_DROPOFF:
            return self.current_request.drop_off
        return None

    def step(self, dt: float) -> None:
        """
        Moves the driver towards the current target according to speed and time step dt.
        """
        self.position.x += self.dir_vector.x * self.speed * dt
        self.position.y += self.dir_vector.y * self.speed * dt

    def complete_pickup(self, time: int) -> None:
        """
        Updates the internal state when the pickup is reached.
        """
        self.status = DriverStatus.TO_DROPOFF
        self.current_request.mark_picked(time)
        self.compute_direction_vector()
        # TO-DO: Implement data collection

    def complete_dropoff(self, time: int) -> None:
        """
        Updates the internal state and history when the dropoff is reached.
        """
        self.status = DriverStatus.IDLE
        self.current_request.mark_delivered(time)
        self.compute_direction_vector()
        # TO-DO: Implement data collection.

