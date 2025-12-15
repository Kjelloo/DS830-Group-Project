from __future__ import annotations
from abc import ABC, abstractmethod

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
        self._check_types(drivers, requests, time, run_id)

        raise NotImplementedError

    @staticmethod
    def _check_types(drivers, requests, time, run_id):
        if not isinstance(drivers, list):
            raise TypeError(f"drivers must be a list, got {type(drivers).__name__}")
        if not all(isinstance(d, Driver) for d in drivers):
            raise TypeError("All items in drivers must be Driver instances")

        if not isinstance(requests, list):
            raise TypeError(f"requests must be a list, got {type(requests).__name__}")
        if not all(isinstance(r, Request) for r in requests):
            raise TypeError("All items in requests must be Request instances")

        if not isinstance(time, int):
            raise TypeError(f"time must be int, got {type(time).__name__}")
        if not isinstance(run_id, str):
            raise TypeError(f"run_id must be str, got {type(run_id).__name__}")

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return self.__str__()
