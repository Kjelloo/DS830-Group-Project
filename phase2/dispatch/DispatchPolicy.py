from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from phase2.Driver import Driver
    from phase2.Request import Request


class DispatchPolicy(ABC):
    @abstractmethod
    def assign(self, drivers: list[Driver],
               requests: list[Request],
               time: int,
               run_id: str) -> list[tuple[Driver, Request]]:
        """
        Returns:
            Proposed (driver, request) pairs for this tick.
        """
        raise NotImplementedError

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return self.__str__()