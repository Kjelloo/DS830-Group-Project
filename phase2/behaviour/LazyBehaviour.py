from __future__ import annotations

from typing import TYPE_CHECKING

from DriverBehaviour import DriverBehaviour

if TYPE_CHECKING:
    from phase2.Driver import Driver
    from phase2.Offer import Offer


class LazyBehaviour(DriverBehaviour):
    def decide(self, driver: Driver, offer: Offer, time: int) -> bool:
        """
        Accept only if the request is close and the driver has been idle for longer than
        a configurable number of ticks.
        """
        pass
