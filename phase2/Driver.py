from phase2.Point import Point
from phase2.Request import Request
from phase2.behaviour.DriverBehaviour import DriverBehaviour
from enum import Enum

class DriverStatus(Enum):
    IDLE = 1,
    TO_PICKUP = 2
    FROM_DROPOFF = 3

class Driver:
    def __init__(self, id: int, position: Point, speed: float, status: DriverStatus, current_request: Request | None,
                 behaviour: DriverBehaviour, history: list) -> None:
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

