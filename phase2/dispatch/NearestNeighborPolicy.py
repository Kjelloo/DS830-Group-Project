from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from phase2.Driver import Driver
    from phase2.Request import Request
    from phase2.dispatch.DispatchPolicy import DispatchPolicy


class NearestNeighborPolicy(DispatchPolicy):
    def assign(self, drivers: list[Driver], requests: list[Request], time: int, run_id: str) -> list[
        tuple[Driver, Request]]:
        """
        Repeatedly match the closest idle driver to the closest waiting request.
        """
        pass
