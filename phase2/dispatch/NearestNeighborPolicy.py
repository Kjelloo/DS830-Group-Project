from phase2.Driver import Driver, DriverStatus
from phase2.Request import Request, RequestStatus
from phase2.dispatch.DispatchPolicy import DispatchPolicy


class NearestNeighborPolicy(DispatchPolicy):
    def assign(self, drivers: list[Driver], requests: list[Request], time: int, run_id: str) -> list[
        tuple[Driver, Request]]:
        """
        repeatedly match the closest idle driver to the closest waiting request, avoiding reuse of drivers and requests
        """
        # Get lists of idle drivers and waiting requests
        idle_drivers = [driver for driver in drivers if driver.status.value == DriverStatus.IDLE.value]
        waiting_requests = [
            request for request in requests
            if request.status.value == RequestStatus.WAITING.value and request.is_active()
        ]

        # Initialize list for holding matched pairs.
        matched_pairs = []

        # Repeatedly find the closest (driver, request) pair and remove them from the pool
        while len(idle_drivers) > 0 and len(waiting_requests) > 0:
            best_driver = None
            best_request = None
            best_distance = float("inf")

            # Find the closest pair among remaining idle drivers and waiting requests
            for driver in idle_drivers:
                for request in waiting_requests:
                    distance = driver.position.distance_to(request.pickup)
                    if distance < best_distance:
                        best_distance = distance
                        best_driver = driver
                        best_request = request

            # If no match was found, stop
            if best_driver is None or best_request is None:
                break

            # Save match and remove them so they cannot be reused this tick
            matched_pairs.append((best_driver, best_request))
            idle_drivers.remove(best_driver)
            waiting_requests.remove(best_request)

        return matched_pairs
