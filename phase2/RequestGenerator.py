from Request import Request


class RequestGenerator:
    def __init__(self,
                 rate: float,
                 rng: float,
                 next_id: int
                 ):
        self.rate = rate
        self.rng = rng  # random number generator
        self.next_id = next_id

    def maybe_generate(self, time: int) -> list[Request]:
        """
        Called once per tick. Draws, according to a user's defined rule, and returns N new R
        objects whose creation_time is 'time' and whose pickup/dropoff points
        are valid positions in the map.
        """
        pass
