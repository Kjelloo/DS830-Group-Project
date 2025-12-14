from __future__ import annotations

import datetime

from phase2.Point import Point
from phase2.Driver import Driver, DriverStatus
from phase2.MutationRule import MutationRule
from phase2.Request import Request, RequestStatus
from phase2.dispatch.DispatchPolicy import DispatchPolicy
from phase2.RequestGenerator import RequestGenerator
from phase2.Offer import Offer
from phase2.behaviour.GreedyDistanceBehaviour import GreedyDistanceBehaviour
from phase2.behaviour.EarningsMaxBehaviour import EarningsMaxBehaviour
from phase2.dispatch.GlobalGreedyPolicy import GlobalGreedyPolicy
from phase2.metrics.Event import Event, EventType
from phase2.metrics.EventManager import EventManager


class DeliverySimulation:
    def __init__(self,
                 time: int,
                 width: int,
                 height: int,
                 drivers: list[Driver],
                 requests: list[Request],
                 request_generator: RequestGenerator,
                 dispatch_policy: DispatchPolicy,
                 mutation_rule: MutationRule,
                 timeout: int,
                 statistics: dict,
                 run_id: str) -> None:
        self.time = time
        self.width = width
        self.height = height
        self.drivers = drivers
        self.requests = requests
        self.dispatch_policy = dispatch_policy
        self.mutation_rule = mutation_rule
        self.timeout = timeout
        self.statistics = statistics
        self.request_generator = request_generator

        # Unique run identifier used for the EventManager
        self.run_id = run_id
        self.event_manager = EventManager(run_id)

    def __str__(self):
        return (f"DeliverySimulation(time={self.time}, "
                f"drivers={self.drivers}, "
                f"requests={self.requests}, "
                f"dispatch_policy={self.dispatch_policy}, "
                f"mutation_rule={self.mutation_rule}, "
                f"timeout={self.timeout}, "
                f"statistics={self.statistics})")

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

        # Generate new requests
        self.requests.extend(self.request_generator.maybe_generate(self.time))

        # Update waiting times and mark expired requests
        self._update_req_wait_times()

        # Compute proposed assignments via dispatch_policy
        proposals = self.dispatch_policy.assign(drivers=self.drivers, requests=self.requests, time=self.time, run_id=self.run_id)

        # Make offers and get driver responses
        offers = self._create_offers(proposals)

        # Resolve conflicts and finalise assignments
        self._resolve_offers(offers)

        # Move drivers and handle pickup/dropoff events
        self._move_drivers(self.drivers, dt=1.0)

        # Apply mutation_rule to each driver
        self._mutate_drivers(self.drivers, self.time)

        # Increment time
        self.time += 1

    def get_snapshot(self) -> dict:
        """
        Returns: Dictionary containing:
        - list of driver positions and headings,
        - list of pickup positions (for WAITING/ASSIGNED requests),
        - list of dropoff positions (for PICKED requests),
        - statistics (served, expired, average waiting time).

        Used by the GUI adapter.
        """
        driver_states = [{'id': driver.id,
                          'position': (driver.position.x, driver.position.y),
                          'status': driver.status.name} for driver in self.drivers]

        pickup_positions = [(req.pickup.x, req.pickup.y) for req in self.requests if req.status in {RequestStatus.WAITING, RequestStatus.ASSIGNED}]

        dropoff_positions = [(req.dropoff.x, req.dropoff.y) for req in self.requests if req.status == RequestStatus.PICKED]

        snapshot = {
            'drivers': driver_states,
            'pickups': pickup_positions,
            'dropoffs': dropoff_positions,
            'statistics': self.statistics
        }

        return snapshot

    def _update_req_wait_times(self) -> None:
        """
        Update waiting times for all WAITING requests and mark expired ones.
        """
        if len(self.requests) == 0:
            return

        for req in self.requests:
            if req.status == RequestStatus.DELIVERED or req.status == RequestStatus.EXPIRED:
                continue

            req.wait_time += 1

            # if request has not reached timeout yet, continue
            if req.wait_time < self.timeout:
                continue

            # Handle expiration different if request is assigned to a driver or not
            if req.assigned_driver is not None:
                # Find the assigned driver and expire the current request
                assigned_driver = next((driver for driver in self.drivers if driver.id == req.assigned_driver), None)
                if assigned_driver is not None:
                    assigned_driver.expire_current_request(self.time)
                else:
                    # This should not happen, but just in case
                    req.mark_expired(self.time)
            else:
                req.mark_expired(self.time)

    @staticmethod
    def _create_offers(proposals: list[tuple[Driver, Request]]) -> list[Offer]:
        """
        Create offers based on proposals.
        """
        offers = []
        for driver, request in proposals:
            estimated_travel = driver.calc_delivery_estimated_travel_time(request)
            estimated_reward = driver.calc_delivery_estimated_reward(request)
            offers.append(Offer(driver=driver, request=request, estimated_travel_time=estimated_travel,
                                estimated_reward=estimated_reward))
        return offers

    def _resolve_offers(self, offers: list[Offer]) -> None:
        """
        Resolve offers, finalise assignments based on driver responses.
        """
        accepted = []
        for offer in offers:
            accepted.append(offer.driver.behaviour.decide(driver=offer.driver, offer=offer, time=self.time, run_id=self.run_id))

        if len(accepted) > 0:
            # Sort offers by estimated travel time in descending order
            sorted_offers = sorted(offers, key=lambda off: off.estimated_travel_time, reverse=True)

            accepted_offer = sorted_offers[0]
            sorted_offers[0].driver.assign_request(request=accepted_offer.request, current_time=self.time)

    def _move_drivers(self, drivers: list[Driver], dt: float) -> None:
        """
        Move drivers and handle pickup/dropoff events.
        """

        for driver in drivers:
            # Handle idle drivers
            if driver.status == DriverStatus.IDLE:
                driver.idle_time += 1  # TODO: This should maybe be in relation to dt instead of a fixed increment
                self.event_manager.add_event(Event(timestamp=self.time,
                                                   event_type=EventType.DRIVER_IDLE,
                                                   driver_id=driver.id,
                                                   request_id=None,
                                                   wait_time=driver.idle_time))
                continue

            driver.idle_time = 0 # Reset idle time if driver is not idle

            # Handle pickups
            if driver.status == DriverStatus.TO_PICKUP and driver.within_one_step_of_target():
                driver.position = driver.current_request.pickup
                driver.complete_pickup(self.time)

            # Handle dropoffs
            if driver.status == DriverStatus.TO_DROPOFF and driver.within_one_step_of_target():
                driver.position = driver.current_request.dropoff
                driver.complete_dropoff(self.time)
                continue

            driver.step(dt)

    def _mutate_drivers(self, drivers: list[Driver], time: int) -> None:
        """
        Apply mutation_rule to each driver.
        """
        for driver in drivers:
            self.mutation_rule.maybe_mutate(driver, time)


if __name__ == "__main__":
    run_id_example = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    request_generator_example = RequestGenerator(rate=0.5, width=50, height=30, start_id=1, run_id=run_id_example)
    delivery_simulation = DeliverySimulation(
        time=0,
        drivers=[
            Driver(id=1,
                   position=Point(10, 20),
                   speed=2.0,
                   behaviour=EarningsMaxBehaviour(),
                   status=DriverStatus.IDLE,
                   current_request=None,
                   history=[],
                   run_id=run_id_example),
            Driver(id=2,
                   position=Point(20, 10),
                   speed=2.0,
                   behaviour=GreedyDistanceBehaviour(),
                   status=DriverStatus.IDLE,
                   current_request=None,
                   history=[],
                   run_id=run_id_example),
        ],
        requests=[
            Request(id=1,
                    pickup=Point(15, 25),
                    dropoff=Point(30, 30),
                    creation_time=0,
                    status=RequestStatus.WAITING,
                    assigned_driver=None,
                    wait_time=0,
                    run_id=run_id_example),
        ],
        dispatch_policy=GlobalGreedyPolicy(),
        mutation_rule=MutationRule(n_trips=5, threshold=0.4, run_id=run_id_example),
        timeout=30,
        statistics={},
        run_id=run_id_example,
        request_generator=request_generator_example
    )

    for _ in range(20):
        delivery_simulation.tick()
