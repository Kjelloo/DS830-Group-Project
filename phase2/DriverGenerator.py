import random
from random import choice

from phase2.Driver import Driver, DriverStatus
from phase2.Point import Point
from phase2.behaviour.EarningsMaxBehaviour import EarningsMaxBehaviour
from phase2.behaviour.GreedyDistanceBehaviour import GreedyDistanceBehaviour


class DriverGenerator:
    def __init__(self, run_id: str) -> None:
        self.run_id = run_id

    def generate(self, amount: int, width: int, height: int, speed: float, start_id: int) -> list[Driver]:
        """
        Generate a list of Driver objects with random positions within the map.
        """
        drivers = []
        for _ in range(amount):
            x = int(min(round(random.uniform(0, width)), width - 1))
            y = int(min(round(random.uniform(0, height)), height - 1))
            position = Point(x, y)

            driver = Driver(
                id=start_id,
                position=position,
                speed=speed,
                behaviour=choice([EarningsMaxBehaviour(), GreedyDistanceBehaviour()]),
                status=DriverStatus.IDLE,
                current_request=None,
                history=[],
                run_id=self.run_id
            )
            drivers.append(driver)
            start_id += 1

        return drivers
