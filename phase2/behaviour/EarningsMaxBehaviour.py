from __future__ import annotations

from typing import TYPE_CHECKING

from DriverBehaviour import DriverBehaviour

if TYPE_CHECKING:
    from phase2.Driver import Driver
    from phase2.Offer import Offer


class EarningsMaxBehaviour(DriverBehaviour):
    def decide(self, driver: Driver, offer: Offer, time: int) -> bool:
        """
        Accept if the ratio estimated reward divided by travel time is above a threshold.
        """
        threshold = 1.0  # TODO: Not sure what a good threshold is yet
        ratio = offer.estimated_reward / offer.estimated_travel_time
        return ratio >= threshold
