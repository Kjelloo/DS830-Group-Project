from __future__ import annotations

from random import choice
from random import random

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

        if random() < 0.02:
            self.__mutate_driver(driver, time)  # switch behaviour randomly sometimes
            return

        if len(driver.history) < self.n_trips:  # don't switch behaviour if history is short
            return

        if type(driver.behaviour) == EarningsMaxBehaviour:
            last_n_trips = driver.history[-self.n_trips:]
            expired_trips = [trips for trips in last_n_trips if trips.status == RequestStatus.EXPIRED]

            if len(expired_trips) / self.n_trips >= self.threshold:
                self.__mutate_driver(driver, time)  # switch to a less optimal behaviour
                return
            if random() < 0.05:  # 5% of the time, switch to a less optimal behaviour
                self.__mutate_driver(driver, time)
                return

        if type(driver.behaviour) == GreedyDistanceBehaviour:
            if random() < (1 - self.threshold): self.__mutate_driver(driver, time)  # switch to a more optimal behaviour

    def __mutate_driver(self, driver: Driver, time: int) -> None:
        """
        Mutate the driver's behaviour parameters.

        Args:
            driver (Driver): The driver whose behaviour is to be mutated.
            time (int): The current simulation time, used for event logging.

        Returns:
            None
        """
        eventManager = EventManager(self.run_id)

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
