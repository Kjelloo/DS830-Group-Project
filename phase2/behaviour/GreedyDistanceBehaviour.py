from __future__ import annotations

from phase2.Driver import Driver
from phase2.Offer import Offer
from phase2.behaviour.DriverBehaviour import DriverBehaviour
from phase2.metrics.Event import Event, EventType
from phase2.metrics.EventManager import EventManager


class GreedyDistanceBehaviour(DriverBehaviour):
    def decide(self, driver: Driver, offer: Offer, time: int, run_id: str) -> bool:
        """
        Accept if the distance to the pickup is below a given threshold.
        Args:
            driver (Driver): Driver instance
            offer (Offer): Offer on which the driver should decide
            time (int): Current time step
            run_id (str): Unique identifier for the simulation run

        Returns:
            True if the driver accepts the offer, False otherwise.
        """
        eventManager = EventManager(run_id)

        # hardcode distance to pickup threshold
        threshold = 21.2  # ~ avg dist between two points in 50x30 grid
        threshold *= 0.9  # scalar found by testing with varying parameters

        if offer.estimated_distance_to_pickup < threshold:
            eventManager.add_event(
                Event(time, EventType.REQUEST_PROPOSAL_ACCEPTED, driver.id, offer.request.id, None, None))
            return True
        else:
            eventManager.add_event(
                Event(time, EventType.REQUEST_PROPOSAL_DENIED, driver.id, offer.request.id, None, None))
            return False
