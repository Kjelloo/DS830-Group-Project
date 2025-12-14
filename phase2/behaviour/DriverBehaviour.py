from __future__ import annotations

from abc import ABC, abstractmethod

from phase2.Driver import Driver
from phase2.Offer import Offer


class DriverBehaviour(ABC):
    @abstractmethod
    def decide(self, driver: Driver, offer: Offer, time: int, run_id: str) -> bool:
        """
        Args:
            driver: Driver instance
            offer: Offer on which the driver should decide
            time: Current time step
            run_id: Unique identifier for the simulation run

        Returns:
            True if the driver accepts the offer, False otherwise.
        """
        raise NotImplementedError()

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return self.__str__()
