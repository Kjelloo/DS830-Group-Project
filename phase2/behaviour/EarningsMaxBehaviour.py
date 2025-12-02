from phase2.Driver import Driver
from phase2.Offer import Offer

from phase2.behaviour.DriverBehaviour import DriverBehaviour


class EarningsMaxBehaviour(DriverBehaviour):
    def decide(self, driver: Driver, offer: Offer, time: int) -> bool:
        """
        Accept if the ratio estimated reward divided by travel time is above a
        threshold.
        """
        pass
