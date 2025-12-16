from __future__ import annotations

import random

from phase2.Point import Point
from phase2.Request import Request, RequestStatus
from phase2.metrics.Event import Event, EventType
from phase2.metrics.EventManager import EventManager


class RequestGenerator:
    """Generate new Request objects during the simulation."""

    def __init__(self,
                 rate: float,
                 width: int,
                 height: int,
                 start_id: int,
                 run_id: str):
        # rate: expected number of new requests per tick (e.g. 0.5, 1.0, 2.3)
        # width, height: size of the map
        # start_id: first id to use
        if not isinstance(rate, (float, int)):
            raise TypeError("rate must be a number")
        if rate < 0:
            raise ValueError("rate must be non-negative")
        if not isinstance(width, (int, float)) or not isinstance(height, (int, float)):
            raise TypeError("width and height must be a number")
        if width < 0 or height < 0:
            raise ValueError("width and height must be non-negative")
        if not isinstance(start_id, int):
            raise TypeError("start_id must be a number")
        if not isinstance(run_id, str):
            raise TypeError("run_id must be a string")

        self.rate = rate
        self.width = width
        self.height = height
        self.next_id = start_id
        self.run_id = run_id

    def maybe_generate(self, time):
        """
        Create new requests for the current tick, based on rate.

        Args:
            time (int | float): Current simulation time.
        """
        eventManager = EventManager(self.run_id)

        if not isinstance(time, (int, float)):
            raise TypeError("time must be a number")
        if time < 0:
            raise ValueError("time must be non-negative")

        # Decide how many requests to create this tick.
        # Always create floor(rate). With probability equal to the
        # fractional part, create one extra.
        base = int(self.rate)
        frac = self.rate - base

        num = base
        if random.random() < frac:
            num += 1

        new_requests = []

        for _ in range(num):
            # random pick_up and dropoff inside the map
            px = int(min(round(random.uniform(0, self.width)), self.width - 1))
            py = int(min(round(random.uniform(0, self.height)), self.height - 1))
            dx = int(min(round(random.uniform(0, self.width)), self.width - 1))
            dy = int(min(round(random.uniform(0, self.height)), self.height - 1))

            pickup = Point(px, py)
            dropoff = Point(dx, dy)

            req = Request(
                id=self.next_id,
                pickup=pickup,
                dropoff=dropoff,
                creation_time=time,
                status=RequestStatus.WAITING,
                assigned_driver=None,
                wait_time=0,
                run_id=self.run_id,
            )

            eventManager.add_event(Event(time, EventType.REQUEST_GENERATED, None, req.id, None, behaviour_name=None))
            new_requests.append(req)
            self.next_id += 1

        return new_requests
