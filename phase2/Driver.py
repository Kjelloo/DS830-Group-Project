from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Point import Point
    from Request import Request
    from behaviour.DriverBehaviour import DriverBehaviour
from enum import Enum


class DriverStatus(Enum):
    IDLE = 1,
    TO_PICKUP = 2
    TO_DROPOFF = 3


class Driver:
    def __init__(self, id: int, position: Point, speed: float, status: DriverStatus, current_request: Request | None,
                 behaviour: DriverBehaviour, history: list[Request]) -> None:
        self.id = id
        self.position = position
        self.speed = speed
        self.status = status
        self.current_request = current_request
        self.behaviour = behaviour
        self.history = history
        self.dir_vector = None

    def direction_vector(self) -> None:
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
        self.direction_vector()

    def target_point(self) -> Point | None:
        """
        Returns:
            The next target. Pickup point or dropoff point depending on DriverStatus.
        """
        if self.status == DriverStatus.IDLE:
            return None
        elif self.status == DriverStatus.TO_PICKUP:
            return self.current_request.pick_up
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
        self.direction_vector()

    def complete_dropoff(self, time: int) -> None:
        """
        Updates the internal state and history when the dropoff is reached.
        """
        self.status = DriverStatus.IDLE
        self.current_request.mark_delivered(time)
        self.direction_vector()

    def calc_delivery_estimated_travel_time(self, request: Request) -> float:
        """
        Calculates the estimated travel time for a given request.
        """
        distance_to_pickup = self.position.distance_to(request.pick_up)
        distance_pickup_to_dropoff = request.pick_up.distance_to(request.drop_off)
        total_distance = distance_to_pickup + distance_pickup_to_dropoff
        estimated_travel_time = total_distance / self.speed
        return estimated_travel_time

    def calc_delivery_estimated_reward(self, request: Request) -> float:
        """
        Calculates the estimated reward for a given request.
        """
        base_fare = 5.0  # TODO: Make configurable
        per_step_rate = 2.0  # TODO: Make configurable
        distance_pickup_to_dropoff = self.calc_delivery_estimated_travel_time(request)
        estimated_reward = base_fare + (per_step_rate * distance_pickup_to_dropoff)
        return estimated_reward
