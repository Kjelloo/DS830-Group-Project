from __future__ import annotations

from phase2.Driver import Driver
from phase2.Offer import Offer
from phase2.behaviour.DriverBehaviour import DriverBehaviour
from phase2.metrics.Event import Event, EventType
from phase2.metrics.EventManager import EventManager


class EarningsMaxBehaviour(DriverBehaviour):
    def decide(self, driver: Driver, offer: Offer, time: int, run_id: str) -> bool:
        """
        Accept if the ratio estimated reward divided by travel time is above a threshold.
        """
        eventManager = EventManager(run_id)

        threshold = 1.0  # TODO: Not sure what a good threshold is yet
        ratio = offer.estimated_reward / offer.estimated_travel_time

        if ratio >= threshold:
            eventManager.add_event(Event(time, EventType.REQUEST_PROPOSAL_ACCEPTED, driver.id, offer.request.id, None))
            return True
        else:
            eventManager.add_event(Event(time, EventType.REQUEST_PROPOSAL_DENIED, driver.id, offer.request.id, None))
            return False
