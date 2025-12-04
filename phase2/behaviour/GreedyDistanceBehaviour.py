from __future__ import annotations

from typing import TYPE_CHECKING

from behaviour.DriverBehaviour import DriverBehaviour

if TYPE_CHECKING:
    from Driver import Driver
    from Offer import Offer


class GreedyDistanceBehaviour(DriverBehaviour):
    def decide(self, driver: Driver, offer: Offer, time: int):
        """
        Accept if the distance to the pickup is below a given threshold.
        """
        pass
