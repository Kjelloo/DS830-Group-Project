from dataclasses import dataclass

from Driver import Driver
from Request import Request


@dataclass
class Offer:
    driver: Driver
    request: Request
    estimated_travel_time: float
    estimated_reward: float
