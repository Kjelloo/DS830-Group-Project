from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from phase2.Driver import Driver
    from phase2.Offer import Offer


class DriverBehaviour(ABC):
    @abstractmethod
    def decide(self, driver: Driver, offer: Offer, time: int) -> bool:
        """
        Args:
            driver: Driver instance
            offer: Offer on which the driver should decide
            time: Current time step

        Returns:
            True if the driver accepts the offer, False otherwise.
        """
        raise NotImplementedError()
