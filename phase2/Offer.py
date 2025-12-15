from __future__ import annotations

from dataclasses import dataclass

from phase2.Driver import Driver
from phase2.Request import Request


@dataclass
class Offer:
    driver: Driver
    request: Request
    estimated_total_distance: float
    estimated_distance_to_pickup: float
    estimated_reward: float

    def __post_init__(self):
        if not isinstance(self.driver, Driver):
            raise TypeError("driver must be a Driver")
        if not isinstance(self.request, Request):
            raise TypeError("request must be a Request")
        if not isinstance(self.estimated_total_distance, (int,float)):
            raise TypeError("estimated_total_travel_time must be a float")
        if not isinstance(self.estimated_distance_to_pickup, (int, float)):
            raise TypeError("estimated_travel_time must be a number")
        if not isinstance(self.estimated_reward, (int, float)):
            raise TypeError("estimated_reward must be a number")