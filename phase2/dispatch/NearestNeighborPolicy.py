from __future__ import annotations

from phase2.Driver import Driver, DriverStatus
from phase2.Request import Request, RequestStatus
from phase2.dispatch.DispatchPolicy import DispatchPolicy


class NearestNeighborPolicy(DispatchPolicy):
    def assign(self, drivers: list[Driver], requests: list[Request], time: int, run_id: str) -> list[
        tuple[Driver, Request]]:
        """
        repeatedly match the closest idle driver to the closest waiting request,
        avoiding reuse of drivers and requests
        """
        # Get list of idle drivers and waiting requests
        idle_drivers = [driver for driver in drivers if driver.status.value == DriverStatus.IDLE.value]
        waiting_requests = [request for request in requests if request.status.value == RequestStatus.WAITING.value]

        # return empty list if no pairs
        if len(idle_drivers) == 0 or len(waiting_requests) == 0:
            return []

        # Initialize list for holding matched pairs
        pairs = []
        # Initialize set for quick look-up speed for already assigned requests
        assigned_requests = set()

        # Repeatedly find the closest (driver, request) pair and remove them from the pool
        for driver in idle_drivers:
            current_request = None
            current_distance = float("inf") # arbitrarily high number

            # Find the closest pair among remaining idle drivers and waiting requests
            for request in waiting_requests:
                    if request.id not in assigned_requests:
                        distance = driver.position.distance_to(request.pickup)
                        if distance < current_distance:
                            current_distance = distance
                            current_request = request

            # Append new pair if it exists
            if current_request is not None:
                assigned_requests.add(current_request.id)
                pairs.append((driver, current_request))

        return pairs
