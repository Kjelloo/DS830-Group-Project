from __future__ import annotations

from phase2.Driver import Driver, DriverStatus
from phase2.Request import Request, RequestStatus
from phase2.dispatch.DispatchPolicy import DispatchPolicy


class NearestNeighborPolicy(DispatchPolicy):
    def assign(self, drivers: list[Driver], requests: list[Request], time: int, run_id: str) -> list[
        tuple[Driver, Request]]:
        """
        Repeatedly match a driver to the closest two requests.
        """
        # Get list of idle drivers and waiting requests
        idle_drivers = [driver for driver in drivers if driver.status.value == DriverStatus.IDLE.value]
        waiting_requests = [request for request in requests if request.status.value == RequestStatus.WAITING.value]

        # return empty list if no pairs
        if len(idle_drivers) == 0 or len(waiting_requests) == 0:
            return []

        # Create empty list to store pairs
        pairs = []
        assigned_requests = set()

        # Iteratively match the next driver to the closest
        for driver in idle_drivers:
            current_request = None
            current_distance = 999 # arbitrarily high number

            for request in waiting_requests:
                    if request.id not in assigned_requests:
                        distance = driver.position.distance_to(request.pickup) + request.pickup.distance_to(request.dropoff)
                        if distance < current_distance:
                            current_distance = distance
                            current_request = request
                            assigned_requests.add(request.id)
            pairs.append((driver, current_request))

        return pairs