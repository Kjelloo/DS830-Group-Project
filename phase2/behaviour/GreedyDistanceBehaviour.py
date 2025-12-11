from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from DriverBehaviour import DriverBehaviour
    from phase2.Driver import Driver
    from phase2.Offer import Offer


class GreedyDistanceBehaviour(DriverBehaviour):
    def decide(self, driver: Driver, offer: Offer, time: int) -> bool:
        """
        Accept if the distance to the pickup is below a given threshold.
        """

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
            return True
        else:
            return False
