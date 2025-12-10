from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from DriverBehaviour import DriverBehaviour
    from phase2.Driver import Driver
    from phase2.Offer import Offer


class GreedyDistanceBehaviour(DriverBehaviour):
    def decide(self, driver: Driver, offer: Offer, time: int):
        """
        Accept if the distance to the pickup is below a given threshold.
        """
        pass
