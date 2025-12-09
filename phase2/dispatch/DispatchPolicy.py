from abc import ABC, abstractmethod

from ..Driver import Driver
from ..Request import Request


class DispatchPolicy(ABC):
    @abstractmethod
    def assign(self, drivers: list[Driver],
               request: list[Request],
               time: int) -> list[tuple[Driver, Request]]:
        """
        Returns:
            Proposed (driver, request) pairs for this tick.
        """
        raise NotImplementedError
