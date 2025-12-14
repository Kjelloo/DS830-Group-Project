from __future__ import annotations

from random import choice

from phase2.Driver import Driver
from phase2.Request import RequestStatus
from phase2.behaviour.EarningsMaxBehaviour import EarningsMaxBehaviour
from phase2.behaviour.GreedyDistanceBehaviour import GreedyDistanceBehaviour
from phase2.metrics.Event import Event, EventType
from phase2.metrics.EventManager import EventManager


class MutationRule:
    def __init__(self, n_trips: int, threshold: float, run_id: str) -> None:
        if not isinstance(n_trips, int):
            raise TypeError("n_trips must be an integer")
        if not isinstance(threshold, float):
            raise TypeError("threshold must be an float")
        if not isinstance(run_id, str):
            raise TypeError("run_id must be a string")

        self.n_trips = n_trips
        self.threshold = threshold
        self.run_id = run_id

    def __str__(self) -> str:
        return f"MutationRule(n_trips={self.n_trips}, threshold={self.threshold})"

    def __repr__(self) -> str:
        return self.__str__()

    def maybe_mutate(self, driver: Driver, time: int) -> None:
        """
         Inspect a driver (and possibly global statistics) and decide whether to update its behaviour or behaviour parameters.

         Args:
            driver (Driver): The driver to inspect and possibly mutate.
            time (int): The current simulation time, used for event logging.
        """

        if len(driver.history) < self.n_trips:
            pass

        # Performance based: if some percentage (threshold) of the last n trip did not deliver on time, change behaviour
        last_n_trips = driver.history[-self.n_trips:]
        expired_trips = [trips for trips in last_n_trips if trips.status == RequestStatus.EXPIRED]

        if len(expired_trips) / self.n_trips >= self.threshold:
            self.__mutate_driver(driver, time)

    def __mutate_driver(self, driver: Driver, time: int) -> None:
        """
        Mutate the driver's behaviour parameters.
        """
        eventManager = EventManager(self.run_id)

        # TODO: Add LazyBehaviour once implemented
        behaviour_classes = [EarningsMaxBehaviour, GreedyDistanceBehaviour]
        current_type = type(driver.behaviour)
        candidates = [b for b in behaviour_classes if b is not current_type]

        if not candidates:
            candidates = behaviour_classes

        new_behaviour_cls = choice(candidates)
        driver.behaviour = new_behaviour_cls()
        driver.history.clear()  # Reset history after mutation

        # Log change with behaviour name for downstream metrics
        eventManager.add_event(Event(time, EventType.BEHAVIOUR_CHANGED, driver.id, None, None,
                                     behaviour_name=type(driver.behaviour).__name__))
