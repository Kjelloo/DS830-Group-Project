from phase2.Driver import Driver
from phase2.Request import Request
from phase2.dispatch.DispatchPolicy import DispatchPolicy


class NearestNeighborPolicy(DispatchPolicy):
    def assign(self, drivers: list[Driver], request: list[Request], time: int) -> list[tuple[Driver, Request]]:
        """
        Repeatedly match the closest idle driver to the closest waiting request.
        """
        pass