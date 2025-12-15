from __future__ import annotations

from phase2.Driver import Driver
from phase2.Offer import Offer
from phase2.behaviour.DriverBehaviour import DriverBehaviour
from phase2.metrics.Event import Event, EventType
from phase2.metrics.EventManager import EventManager


class EarningsMaxBehaviour(DriverBehaviour):
    def decide(self, driver: Driver, offer: Offer, time: int, run_id: str) -> bool:
        """
        Accept if the ratio estimated reward divided by travel distance is above a threshold.
        """
        eventManager = EventManager(run_id)

        # hardcode threshold
        threshold = 1.45 # based on testing

        # compute ratio
        ratio = offer.estimated_reward / offer.estimated_total_distance

        if ratio > threshold:
            eventManager.add_event(Event(time, EventType.REQUEST_PROPOSAL_ACCEPTED, driver.id, offer.request.id, None))
            return True
        else:
            eventManager.add_event(Event(time, EventType.REQUEST_PROPOSAL_DENIED, driver.id, offer.request.id, None))
            return False
