from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Point import Point
    from Request import Request
    from behaviour.DriverBehaviour import DriverBehaviour
from enum import Enum


class DriverStatus(Enum):
    IDLE = 1
    TO_PICKUP = 2
    TO_DROPOFF = 3


class Driver:
    def __init__(self,
                 id: int,
                 position: Point,
                 speed: float,
                 status: DriverStatus,
                 current_request: Request | None,
                 behaviour: DriverBehaviour,
                 history: list[Request],
                 run_id: str) -> None:
        self.id = id
        self.position = position
        self.speed = speed
        self.status = status
        self.current_request = current_request
        self.behaviour = behaviour
        self.history = history
        self.run_id = run_id
        self.dir_vector = None

    def __str__(self):
        return f"Driver(id={self.id}, position={self.position}, speed={self.speed}, status={self.status}, " \
               f"current_request={self.current_request}, behaviour={self.behaviour}, history={self.history})"

    def __repr__(self) -> str:
        return self.__str__()

    def compute_direction_vector(self) -> None:
        target = self.target_point()
        if target is not None:
            dx = target.x - self.position.x
            dy = target.y - self.position.y
            magnitude = math.hypot(dx, dy)
            if magnitude > 0:
                self.dir_vector = (dx / magnitude, dy / magnitude)
            else:
                self.dir_vector = (0.0, 0.0)
        else:
            self.dir_vector = None

    def assign_request(self, request: Request, current_time: int) -> None:
        self.current_request = request
        self.status = DriverStatus.TO_PICKUP
        self.current_request.mark_assigned(self.id, current_time)
        self.compute_direction_vector()

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
            return self.current_request.dropoff
        return None

    def step(self, dt: float) -> None:
        """
        Moves the driver towards the current target according to speed and time step dt.
        """
        self.position.x += self.dir_vector[0] * self.speed * dt
        self.position.y += self.dir_vector[1] * self.speed * dt

    def within_one_step_of_target(self) -> bool:
        """
        Checks if the driver is within one step of the target point.
        """
        if self.target_point() is None:
            return False
        distance_to_target = self.position.distance_to(self.target_point())
        return distance_to_target <= self.speed

    def expire_current_request(self, time: int) -> None:
        """
        Expires the current request.
        """
        if self.current_request is not None:
            self.current_request.mark_expired(time)
            self.history.append(self.current_request)
            self.current_request = None
            self.status = DriverStatus.IDLE
            self.compute_direction_vector()

    def complete_pickup(self, time: int) -> None:
        """
        Updates the internal state when the pickup is reached.
        """
        self.status = DriverStatus.TO_DROPOFF
        self.current_request.mark_picked(time)
        self.compute_direction_vector()

    def complete_dropoff(self, time: int) -> None:
        """
        Updates the internal state and history when the dropoff is reached.
        """
        self.status = DriverStatus.IDLE
        self.current_request.mark_delivered(time)
        self.history.append(self.current_request)
        self.current_request = None
        self.compute_direction_vector()

    def calc_delivery_estimated_travel_time(self, request: Request) -> float:
        """
        Calculates the estimated travel time for a given request.
        """
        distance_to_pickup = self.position.distance_to(request.pickup)
        distance_pickup_to_dropoff = request.pickup.distance_to(request.dropoff)
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
