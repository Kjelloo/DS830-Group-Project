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
        """
        eventManager = EventManager(run_id)

        # Set the threshold for the quotient of distance to the pickup point / total
        # distance the driver can travel in x ticks. If the quotient is larger than
        # that, return False, else return True.
        threshold = 0.33

        # Fix x: the amount of ticks the quotient will be based on.
        x = 30

        # Get distance driver can travel in x ticks.
        traversable_distance = driver.speed * x

        # Get distance to pickup point.
        dist_to_pickup = driver.position.distance_to(offer.request.pickup)

        if (dist_to_pickup / traversable_distance) < threshold:
            eventManager.add_event(Event(time, EventType.REQUEST_PROPOSAL_ACCEPTED, driver.id, offer.request.id, None))
            return True
        else:
            eventManager.add_event(Event(time, EventType.REQUEST_PROPOSAL_DENIED, driver.id, offer.request.id, None))
            return False
