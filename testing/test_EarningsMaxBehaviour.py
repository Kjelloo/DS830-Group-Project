import unittest
from unittest.mock import patch, MagicMock

from phase2.behaviour.EarningsMaxBehaviour import EarningsMaxBehaviour
from phase2.metrics.Event import EventType


class FakeRequest:
    def __init__(self, request_id):
        self.id = request_id


class FakeOffer:
    def __init__(self, reward, travel_time, request):
        self.estimated_reward = reward
        self.estimated_travel_time = travel_time
        self.request = request


class FakeDriver:
    def __init__(self, driver_id):
        self.id = driver_id


class TestEarningsMaxBehaviour(unittest.TestCase):

    def setUp(self):
        self.behaviour = EarningsMaxBehaviour()
        self.driver = FakeDriver(driver_id=10)
        self.request = FakeRequest(request_id=99)

    @patch("phase2.behaviour.EarningsMaxBehaviour.EventManager")
    def test_accepts_offer_when_ratio_meets_threshold(self, mock_event_manager):
        offer = FakeOffer(
            reward=10.0,
            travel_time=5.0, # ratio = 2.0 >= 1.0
            request=self.request
        )

        event_manager_instance = MagicMock()
        mock_event_manager.return_value = event_manager_instance

        result = self.behaviour.decide(
            driver=self.driver,
            offer=offer,
            time=7,
            run_id="test_run"
        )

        self.assertTrue(result)

        mock_event_manager.assert_called_once_with("test_run")

        event_manager_instance.add_event.assert_called_once()
        event = event_manager_instance.add_event.call_args[0][0]

        self.assertEqual(event.event_type, EventType.REQUEST_PROPOSAL_ACCEPTED)
        self.assertEqual(event.driver_id, self.driver.id)
        self.assertEqual(event.request_id, self.request.id)

    @patch("phase2.behaviour.EarningsMaxBehaviour.EventManager")
    def test_denies_offer_when_ratio_below_threshold(self, mock_event_manager):
        offer = FakeOffer(
            reward=4.0,
            travel_time=5.0, # ratio = 0.8 < 1.0
            request=self.request
        )

        event_manager_instance = MagicMock()
        mock_event_manager.return_value = event_manager_instance

        result = self.behaviour.decide(
            driver=self.driver,
            offer=offer,
            time=12,
            run_id="test_run"
        )

        self.assertFalse(result)

        mock_event_manager.assert_called_once_with("test_run")

        event_manager_instance.add_event.assert_called_once()
        event = event_manager_instance.add_event.call_args[0][0]

        self.assertEqual(event.event_type, EventType.REQUEST_PROPOSAL_DENIED)
        self.assertEqual(event.driver_id, self.driver.id)
        self.assertEqual(event.request_id, self.request.id)


if __name__ == "__main__":
    unittest.main()
