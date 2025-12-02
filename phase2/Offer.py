from dataclasses import dataclass

from phase2.Driver import Driver
from phase2.Request import Request


@dataclass
class Offer:
    driver: Driver
    request: Request
    estimated_travel_time: float
    # If we chose a reward based model:
    # estimated_reward: float
