from phase2.Driver import Driver, DriverStatus
from phase2.Request import Request, RequestStatus
from phase2.dispatch.DispatchPolicy import DispatchPolicy


class GlobalGreedyPolicy(DispatchPolicy):
    def assign(self, drivers: list[Driver], requests: list[Request], time: int, run_id: str) -> list[
        tuple[Driver, Request]]:
        """
        build all (idle driver, waiting request) pairs, sort by distance, and match greedily while avoiding reuse of drivers and requests
        """
        # Get lists of idle drivers and waiting requests
        idle_drivers = [driver for driver in drivers if driver.status.value == DriverStatus.IDLE.value]
        waiting_requests = [request for request in requests if request.status.value == RequestStatus.WAITING.value]

        # Initialize list to keep all pairs and their respective distance (driver, request, distance)
        all_pairs = []

        # Iteratively build all pairs
        for driver in idle_drivers:
            for request in waiting_requests:
                distance = driver.position.distance_to(request.pickup) + request.pickup.distance_to(request.dropoff)
                all_pairs.append((driver, request, distance))

        # Sort pairs based on distance
        all_pairs.sort(key=lambda x: x[2])

        # Initialize sets to keep track of used drivers/requests and a list for holding matched pairs.
        assigned_drivers = set()
        assigned_requests = set()
        matched_pairs = []

        # Iteratively match drivers to requests based on distance making sure no driver/request is reused.
        for driver, request, distance in all_pairs:
            if driver.id not in assigned_drivers and request.id not in assigned_requests:
                matched_pairs.append((driver, request))
                assigned_drivers.add(driver.id)
                assigned_requests.add(request.id)

        return matched_pairs
