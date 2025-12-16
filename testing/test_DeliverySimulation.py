import unittest
from unittest.mock import MagicMock, patch

from phase2.Point import Point
from phase2.Driver import Driver, DriverStatus
from phase2.Request import Request, RequestStatus
from phase2.Offer import Offer
from phase2.MutationRule import MutationRule
from phase2.behaviour.GreedyDistanceBehaviour import GreedyDistanceBehaviour
from phase2.dispatch.DispatchPolicy import DispatchPolicy
from phase2.RequestGenerator import RequestGenerator
from phase2.DeliverySimulation import DeliverySimulation

"""
Since every unit that is imported and used in DeliverySimulation has already been used, we
will only test that the methods are called as expected using mocking most of the way.
"""

class TestDeliverySimulation(unittest.TestCase):

    def setUp(self):
        # Arrange: create mock drivers, requests, request generator, policy, mutation_rule
        self.driver = Driver(
            id=1,
            position=Point(0, 0),
            speed=1.0,
            status=DriverStatus.IDLE,
            current_request=None,
            behaviour=GreedyDistanceBehaviour(),
            history=[],
            run_id="test_run"
        )

        self.request = Request(
            id=1,
            pickup=Point(1, 1),
            dropoff=Point(2, 2),
            creation_time=0,
            status=RequestStatus.WAITING,
            assigned_driver=None,
            wait_time=0,
            run_id="test_run"
        )

        self.mock_request_generator = MagicMock(spec=RequestGenerator)
        self.mock_request_generator.maybe_generate.return_value = [self.request]

        self.mock_dispatch_policy = MagicMock(spec=DispatchPolicy)
        self.mock_dispatch_policy.assign.return_value = [(self.driver, self.request)]

        self.mock_mutation_rule = MagicMock(spec=MutationRule)

        self.sim = DeliverySimulation(
            time=0,
            width=10,
            height=10,
            drivers=[self.driver],
            requests=[],
            request_generator=self.mock_request_generator,
            dispatch_policy=self.mock_dispatch_policy,
            mutation_rule=self.mock_mutation_rule,
            timeout=5,
            statistics={'expired': 0, 'served': 0, 'served_waits': []},
            run_id="test_run"
        )

    @patch("phase2.DeliverySimulation.EventManager")
    def test_tick_calls_internal_methods(self, mock_event_manager_class):
        # Arrange
        event_manager_instance = MagicMock()
        mock_event_manager_class.return_value = event_manager_instance

        # Patch internal methods to track calls
        self.sim._update_req_wait_times = MagicMock()
        self.sim._create_offers = MagicMock(return_value=[MagicMock(spec=Offer)])
        self.sim._assign_and_resolve_offers = MagicMock()
        self.sim._move_drivers = MagicMock()
        self.sim._mutate_drivers = MagicMock()

        # Act
        self.sim.tick()

        # Assert
        self.sim._update_req_wait_times.assert_called_once()
        self.sim._create_offers.assert_called_once()
        self.sim._assign_and_resolve_offers.assert_called_once()
        self.sim._move_drivers.assert_called_once()
        self.sim._mutate_drivers.assert_called_once()
        self.assertEqual(self.sim.time, 1)

    def test_update_req_wait_times_increments_wait_time(self):
        # Arrange
        self.sim.requests.append(self.request)
        self.request.wait_time = 0

        # Act
        self.sim._update_req_wait_times()

        # Assert
        self.assertEqual(self.request.wait_time, 1)
        self.assertEqual(self.sim.statistics['expired'], 0)

    def test_update_req_wait_times_expires_request_unassigned(self):
        # Arrange
        self.sim.requests.append(self.request)
        self.request.wait_time = 5  # equal to timeout
        self.request.assigned_driver = None
        self.request.mark_expired = MagicMock()

        # Act
        self.sim._update_req_wait_times()

        # Assert
        self.request.mark_expired.assert_called_once_with(self.sim.time)
        self.assertEqual(self.sim.statistics['expired'], 1)

    def test_update_req_wait_times_expires_request_assigned_driver(self):
        # Arrange
        self.driver.expire_current_request = MagicMock()
        self.sim.drivers.append(self.driver)
        self.request.assigned_driver = self.driver.id
        self.request.wait_time = 5  # equal to timeout
        self.sim.requests.append(self.request)

        # Act
        self.sim._update_req_wait_times()

        # Assert
        self.driver.expire_current_request.assert_called_once_with(self.sim.time)
        self.assertEqual(self.sim.statistics['expired'], 1)

    def test_create_offers_returns_correct_offer_list(self):
        # Arrange
        offer_list = self.sim._create_offers([(self.driver, self.request)])

        # Act & Assert
        self.assertEqual(len(offer_list), 1)
        self.assertIsInstance(offer_list[0], Offer)
        self.assertEqual(offer_list[0].driver, self.driver)
        self.assertEqual(offer_list[0].request, self.request)

    def test_assign_and_resolve_offers_driver_accepts_offer(self):
        # Arrange
        offer = MagicMock(spec=Offer)
        offer.driver = self.driver
        offer.request = self.request
        offer.driver.behaviour.decide = MagicMock(return_value=True)
        offer.driver.assign_request = MagicMock()

        # Act
        self.sim._assign_and_resolve_offers([offer])

        # Assert
        offer.driver.assign_request.assert_called_once_with(request=self.request, current_time=self.sim.time)

    def test_assign_and_resolve_offers_driver_declines_offer(self):
        # Arrange
        offer = MagicMock(spec=Offer)
        offer.driver = self.driver
        offer.request = self.request
        offer.driver.behaviour.decide = MagicMock(return_value=False)
        offer.driver.assign_request = MagicMock()

        # Act
        self.sim._assign_and_resolve_offers([offer])

        # Assert
        offer.driver.assign_request.assert_not_called()

    def test_get_snapshot_returns_correct_structure(self):
        # Arrange
        self.sim.drivers[0].status = DriverStatus.IDLE
        self.sim.requests.append(self.request)
        snapshot = self.sim.get_snapshot()

        # Act & Assert
        self.assertIn('drivers', snapshot)
        self.assertIn('pickups', snapshot)
        self.assertIn('dropoffs', snapshot)
        self.assertIn('statistics', snapshot)
        self.assertEqual(snapshot['drivers'][0]['id'], self.driver.id)
        self.assertEqual(snapshot['pickups'][0], (self.request.pickup.x, self.request.pickup.y))

    def test_mutate_drivers_calls_mutation_rule(self):
        # Act
        self.sim._mutate_drivers([self.driver], self.sim.time)

        # Assert
        self.mock_mutation_rule.maybe_mutate.assert_called_once_with(self.driver, self.sim.time)


if __name__ == "__main__":
    unittest.main()
