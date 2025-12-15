from __future__ import annotations
import math
from enum import Enum

from phase2.Point import Point
from phase2.Request import Request
from phase2.behaviour.DriverBehaviour import DriverBehaviour


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

        if not isinstance(id, int):
            raise TypeError(f"id must be int, got {type(id).__name__}")
        if not isinstance(position, Point):
            raise TypeError(f"position must be Point, got {type(position).__name__}")
        if not isinstance(speed, (int, float)):
            raise TypeError(f"speed must be int or float, got {type(speed).__name__}")
        if not isinstance(status, DriverStatus):
            raise TypeError(f"status must be DriverStatus, got {type(status).__name__}")
        if current_request is not None and not isinstance(current_request, Request):
            raise TypeError(f"current_request must be Request, got {type(current_request).__name__}")
        if not isinstance(behaviour, DriverBehaviour):
            raise TypeError(f"behaviour must be DriverBehaviour, got {type(behaviour).__name__}")
        if not isinstance(history, list):
            raise TypeError(f"history must be list, got {type(history).__name__}")
        for h in history:
            if not isinstance(h, Request):
                raise TypeError("history list must contain only Request objects")
        if not isinstance(run_id, str):
            raise TypeError(f"run_id must be string, got {type(run_id).__name__}")

        self.id = id
        self.position = position
        self.speed = speed
        self.status = status
        self.current_request = current_request
        self.behaviour = behaviour
        self.history = history
        self.run_id = run_id
        self.idle_time = 0
        self.dir_vector: Point | None = None

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
                self.dir_vector = Point(dx / magnitude, dy / magnitude)
            else:
                self.dir_vector = Point(0.0, 0.0)
        else:
            self.dir_vector = None
            return

    def assign_request(self, request: Request, current_time: int) -> None:
        if not isinstance(request, Request):
            raise TypeError(f"request must be Request, got {type(request).__name__}")
        if not isinstance(current_time, int):
            raise TypeError(f"current_time must be int, got {type(current_time).__name__}")

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
        if self.current_request is None:
            return None
        if self.status == DriverStatus.TO_PICKUP:
            return self.current_request.pickup
        if self.status == DriverStatus.TO_DROPOFF:
            return self.current_request.dropoff
        return None

    def step(self, dt: float | int) -> None:
        """
        Moves the driver towards the current target according to speed and time step dt.
        """
        if not isinstance(dt, (float, int)):
            raise TypeError(f"dt must be int/float, got {type(dt).__name__}")

        if self.dir_vector is None:
            return

        self.position.x += self.dir_vector.x * self.speed * dt
        self.position.y += self.dir_vector.y * self.speed * dt

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
        if not isinstance(time, int):
            raise TypeError(f"time must be int, got {type(time).__name__}")

        self.status = DriverStatus.TO_DROPOFF
        self.current_request.mark_picked(time)
        self.compute_direction_vector()

    def complete_dropoff(self, time: int) -> None:
        """
        Updates the internal state and history when the dropoff is reached.
        """
        if not isinstance(time, int):
            raise TypeError(f"time must be int, got {type(time).__name__}")

        self.status = DriverStatus.IDLE
        self.current_request.mark_delivered(time)
        self.history.append(self.current_request)
        self.current_request = None
        self.compute_direction_vector()

    def calc_estimated_total_dist_to_delivery(self, request: Request) -> float:
        """
        Calculates the estimated travel time tics for a given request.
        """
        if not isinstance(request, Request):
            raise TypeError(f"request must be Request, got {type(request).__name__}")

        d1 = self.position.distance_to(request.pickup) # distance to pickup
        d2 = request.pickup.distance_to(request.dropoff) # distance from pickup to dropoff
        return d1 + d2

    def calc_estimated_delivery_reward(self, request: Request) -> float:
        if not isinstance(request, Request):
                raise TypeError(f"request must be Request, got {type(request).__name__}")

        base_reward = 15
        reward_per_distance = 0.7

        return base_reward + (reward_per_distance * self.calc_estimated_total_dist_to_delivery(request))