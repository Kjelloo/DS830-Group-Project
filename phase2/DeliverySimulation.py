from __future__ import annotations

import datetime

from phase2.Driver import Driver, DriverStatus
from phase2.MutationRule import MutationRule
from phase2.Offer import Offer
from phase2.Point import Point
from phase2.Request import Request, RequestStatus
from phase2.RequestGenerator import RequestGenerator
from phase2.behaviour.EarningsMaxBehaviour import EarningsMaxBehaviour
from phase2.behaviour.GreedyDistanceBehaviour import GreedyDistanceBehaviour
from phase2.dispatch.DispatchPolicy import DispatchPolicy
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
        if not isinstance(time, int):
            raise TypeError("time must be int")
        if not isinstance(width, int):
            raise TypeError("width must be int")
        if not isinstance(height, int):
            raise TypeError("height must be int")
        if not isinstance(timeout, int):
            raise TypeError("timeout must be int")
        if not isinstance(run_id, str):
            raise TypeError("run_id must be str")
        if not isinstance(drivers, list) or not all(isinstance(d, Driver) for d in drivers):
            raise TypeError("drivers must be list[Driver]")
        if not isinstance(requests, list) or not all(isinstance(r, Request) for r in requests):
            raise TypeError("requests must be list[Request]")
        if not isinstance(request_generator, RequestGenerator):
            raise TypeError("request_generator must be RequestGenerator")
        if not isinstance(dispatch_policy, DispatchPolicy):
            raise TypeError("dispatch_policy must be DispatchPolicy")
        if not isinstance(mutation_rule, MutationRule):
            raise TypeError("mutation_rule must be MutationRule")
        if not isinstance(statistics, dict):
            raise TypeError("statistics must be dict")

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
        3. Compute proposed assignments via dispatch_policy. (missing)
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
        proposals = self.dispatch_policy.assign(drivers=self.drivers, requests=self.requests, time=self.time,
                                                run_id=self.run_id)

        offers = self._create_offers(proposals)

        # Get driver responses to offers, resolve conflicts and finalize assignments
        self._assign_and_resolve_offers(offers)

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

        pickup_positions = [(req.pickup.x, req.pickup.y) for req in self.requests if
                            req.status in {RequestStatus.WAITING, RequestStatus.ASSIGNED}]

        dropoff_positions = [(req.dropoff.x, req.dropoff.y) for req in self.requests if
                             req.status == RequestStatus.PICKED]

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
                    self.statistics['expired'] += 1
                    assigned_driver.expire_current_request(self.time)
                else:
                    # This should not happen, but just in case
                    self.statistics['expired'] += 1
                    req.mark_expired(self.time)
            else:
                self.statistics['expired'] = self.statistics.get('expired', 0) + 1
                req.mark_expired(self.time)

    @staticmethod
    def _create_offers(proposals: list[tuple[Driver, Request]]) -> list[Offer]:
        """
        Create offers based on proposals.
        Args:
            proposals (list[tuple[Driver, Request]]): Proposed (driver, request) pairs
        Returns:
            list[Offer]: List of created offers
        """
        offers = []

        for driver, request in proposals:
            estimated_total_distance = driver.calc_estimated_total_dist_to_delivery(request)
            estimated_distance_to_pickup = driver.position.distance_to(request.pickup)
            estimated_reward = driver.calc_estimated_delivery_reward(request)

            offers.append(Offer(driver=driver, request=request,
                                estimated_total_distance=estimated_total_distance,
                                estimated_distance_to_pickup=estimated_distance_to_pickup,
                                estimated_reward=estimated_reward))

        return offers

    def _assign_and_resolve_offers(self, offers: list[Offer]) -> None:
        """
        Offer and resolve offers, and finalise assignments based on driver responses

        Args:
            offers (list[Offer]): List of created offers
        Returns:
            None
        """
        # Initialize data structures to keep track of busy drivers and accepted requests
        busy_drivers = set()
        accepted_requests = set()

        # Sort offers by estimated travel time in ascending order
        if len(offers) == 0: return

        # Iteratively offer offers to drivers
        for offer in offers:
            # Make sure offer is not already accepted and driver is not busy
            if offer.driver.id in busy_drivers or offer.request.id in accepted_requests:
                continue

            # As a design choice, we omit the below code in order to mutate based on expired accepted requests.
            """
            # Make sure driver have time to make the delivery. If not, skip offer
            total_time_to_delivery = offer.driver.calc_estimated_total_time_to_delivery(offer.request)
            time_left_before_expiration = self.timeout - offer.request.wait_time
            if total_time_to_delivery > time_left_before_expiration:
                continue
            """

            # Let driver decide whether to accept offer or not
            if offer.driver.behaviour.decide(offer.driver, offer, self.time, self.run_id):
                # Assign request and track decisions if offer is accepted
                offer.driver.assign_request(request=offer.request, current_time=self.time)
                busy_drivers.add(offer.driver.id)
                accepted_requests.add(offer.request.id)

    def _move_drivers(self, drivers: list[Driver], dt: float) -> None:
        """
        Move drivers and handle pickup/dropoff events.

        Args:
            drivers (list[Driver]): List of drivers to move
            dt (float): Time delta for the movement step

        Returns:
            None
        """
        for driver in drivers:
            # Handle idle drivers
            if driver.status == DriverStatus.IDLE:
                driver.idle_time += 1  # TODO: This should maybe be in relation to dt instead of a fixed increment
                self.event_manager.add_event(Event(timestamp=self.time,
                                                   event_type=EventType.DRIVER_IDLE,
                                                   driver_id=driver.id,
                                                   request_id=None,
                                                   wait_time=driver.idle_time,
                                                   behaviour_name=None))
                continue

            driver.idle_time = 0  # Reset idle time if driver is not idle

            # Handle pickups
            if driver.status == DriverStatus.TO_PICKUP and driver.within_one_step_of_target():
                driver.position = driver.current_request.pickup
                driver.complete_pickup(self.time)

            # Handle dropoffs
            if driver.status == DriverStatus.TO_DROPOFF and driver.within_one_step_of_target():
                driver.position = driver.current_request.dropoff
                self.statistics['served'] += 1
                self.statistics['served_waits'].append(driver.current_request.wait_time)
                driver.complete_dropoff(self.time)
                continue

            driver.step(dt)

    def _mutate_drivers(self, drivers: list[Driver], time: int) -> None:
        """
        Apply mutation_rule to each driver.

        Args:
            drivers (list[Driver]): List of drivers to potentially mutate
            time (int): Current time step
        Returns:
            None
        """
        for driver in drivers:
            self.mutation_rule.maybe_mutate(driver, time)
