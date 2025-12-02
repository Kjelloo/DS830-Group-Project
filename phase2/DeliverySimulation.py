from phase2.Driver import Driver
from phase2.MutationRule import MutationRule
from phase2.Request import Request
from phase2.dispatch.DispatchPolicy import DispatchPolicy


class DeliverySimulation:
    def __init__(self,
                 time: int,
                 drivers: list[Driver],
                 requests: list[Request],
                 dispatch_policy: DispatchPolicy,
                 mutation_rule: MutationRule,
                 timeout: int,
                 statistics: dict) -> None:
        self.time = time
        self.drivers = drivers
        self.requests = requests
        self.dispatch_policy = dispatch_policy
        self.mutation_rule = mutation_rule
        self.timeout = timeout
        self.statistics = statistics # Not defined yet.

    def tick(self) -> None:
        """
        Advance the simulation by one time step.

        1. Generate new requests.
        2. Update waiting times and mark expired requests.
        3. Compute proposed assignments via dispatch_policy.
        4. Convert proposals to offers, ask driver behaviours to accept/reject.
        5. Resolve conflicts and finalise assignments.
        6. Move drivers and handle pickup/dropoff events.
        7. Apply mutation_rule to each driver.
        8. Increment time.
        """
        pass

    def get_snapshot(self) -> dict:
        """
        Returns: Dictionary containing:
        - list of driver positions and headings,
        - list of pickup positions (for WAITING/ASSIGNED requests),
        - list of dropoff positions (for PICKED requests),
        - statistics (served, expired, average waiting time).

        Used by the GUI adapter.
        """
        pass
