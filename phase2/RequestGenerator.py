import random
from Point import Point
from Request import Request, RequestStatus


class RequestGenerator:
    """Generate new Request objects during the simulation."""

    def __init__(self, rate, width, height, start_id=0):
        # rate: expected number of new requests per tick (e.g. 0.5, 1.0, 2.3)
        # width, height: size of the map
        # start_id: first id to use
        if rate < 0:
            raise ValueError("rate must be non-negative")
        if width < 0 or height < 0:
            raise ValueError("width and height must be non-negative")

        self.rate = rate
        self.width = width
        self.height = height
        self.next_id = start_id

    def __str__(self):
        return (f"RequestGenerator(rate={self.rate}, "
                f"width={self.width}, height={self.height}, "
                f"next_id={self.next_id})")

    def maybe_generate(self, time):
        """
        Called once per tick.

        Returns a list of new Request objects whose creation_time == time.
        The number of new requests is based on self.rate.
        """
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
            px = random.uniform(0, self.width)
            py = random.uniform(0, self.height)
            dx = random.uniform(0, self.width)
            dy = random.uniform(0, self.height)

            pickup = Point(px, py)      # Point class should exist in the same file
            dropoff = Point(dx, dy)

            # Request class should also exist in the same file
            req = Request(
                id=self.next_id,
                pick_up=pickup,
                drop_off=dropoff,
                creation_time=time,
                status=RequestStatus.WAITING,
                assigned_driver=None,
                wait_time=0
            )

            new_requests.append(req)
            self.next_id += 1

        return new_requests

if __name__ == "__main__":
    rg = RequestGenerator(rate=1.5, width=10, height=5, start_id=0)

    for t in range(5):
        new_reqs = rg.maybe_generate(t)
        for req in new_reqs:
            print(f"time {t}: {str(req)}")