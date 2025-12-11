from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Driver import Driver
    from Request import Request


@dataclass
class Offer:
    driver: Driver
    request: Request
    estimated_travel_time: float
    estimated_reward: float
