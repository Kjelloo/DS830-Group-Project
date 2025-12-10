from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from phase2.Driver import Driver
    from phase2.Request import Request
    from phase2.dispatch.DispatchPolicy import DispatchPolicy


class GlobalGreedyPolicy(DispatchPolicy):
    def assign(self, drivers: list[Driver], request: list[Request], time: int) -> list[tuple[Driver, Request]]:
        """
        build all (idle driver, waiting request) pairs, sort by distance, and match greedily while avoiding reuse of drivers and requests
        """
        pass
