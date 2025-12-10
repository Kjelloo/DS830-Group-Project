from random import choice
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Driver import Driver
    from Request import RequestStatus
    from behaviour.EarningsMaxBehaviour import EarningsMaxBehaviour
    from behaviour.GreedyDistanceBehaviour import GreedyDistanceBehaviour
    from behaviour.LazyBehaviour import LazyBehaviour

    from metrics.EventManager import EventManager
    from metrics.Event import Event, EventType

eventManager = EventManager(filepath="metrics/events.csv")


class MutationRule:
    def __init__(self, n_trips: int, threshold: float) -> None:
        self.n_trips = n_trips
        self.threshold = threshold

    def maybe_mutate(self, driver: Driver, time: int) -> None:
        """
         Inspect a driver (and possibly global statistics) and decide whether to update its behaviour or behaviour parameters.

         Args:
            driver (Driver): The driver to inspect and possibly mutate.
        """

        if len(driver.history) < self.n_trips:
            pass

        # Performance based: if some percentage (threshold) of the last n trip did not deliver on time, change behaviour
        last_n_trips = driver.history[-self.n_trips:]
        expired_trips = [trips for trips in last_n_trips if trips.status == RequestStatus.EXPIRED]

        if len(expired_trips) / self.n_trips >= self.threshold:
            self.__mutate_driver(driver)

    def __mutate_driver(self, driver: Driver, time: int) -> None:
        """
        Mutate the driver's behaviour parameters.
        """
        behaviour_classes = [EarningsMaxBehaviour, GreedyDistanceBehaviour, LazyBehaviour]
        current_type = type(driver.behaviour)
        candidates = [b for b in behaviour_classes if b is not current_type]

        if not candidates:
            candidates = behaviour_classes

        new_behaviour_cls = choice(candidates)
        driver.behaviour = new_behaviour_cls

        eventManager.add_event(Event(time, EventType.BEHAVIOUR_CHANGED, driver.id, None, None))
