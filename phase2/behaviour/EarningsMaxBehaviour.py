from __future__ import annotations

from typing import TYPE_CHECKING

from behaviour.DriverBehaviour import DriverBehaviour

if TYPE_CHECKING:
    from Driver import Driver
    from Offer import Offer


class EarningsMaxBehaviour(DriverBehaviour):
    def decide(self, driver: Driver, offer: Offer, time: int) -> bool:
        """
        Accept if the ratio estimated reward divided by travel time is above a
        threshold.
        """
        pass
