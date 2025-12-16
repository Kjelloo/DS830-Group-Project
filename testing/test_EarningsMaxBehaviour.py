import unittest
from unittest.mock import patch, MagicMock

from phase2.behaviour.EarningsMaxBehaviour import EarningsMaxBehaviour
from phase2.metrics.Event import EventType
from phase2.Request import Request, RequestStatus
from phase2.Driver import Driver, DriverStatus
from phase2.Point import Point
from phase2.Offer import Offer


class TestEarningsMaxBehaviour(unittest.TestCase):

    def setUp(self):
        self.behaviour = EarningsMaxBehaviour()
        self.request = Request(1, Point(2,2), Point(3,3), 7, RequestStatus.WAITING,
                               None, 0, "test_run")
        self.driver = Driver(1, Point(1,1), 5, DriverStatus.IDLE, None,
                             self.behaviour, [], "test_run")


    @patch("phase2.behaviour.EarningsMaxBehaviour.EventManager")
    def test_accepts_offer_when_ratio_meets_threshold(self, mock_event_manager):
        offer = Offer(self.driver, self.request, 5, 10, 15)

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
        offer = Offer(self.driver, self.request, 10, 5, 2)

        event_manager_instance = MagicMock()
        mock_event_manager.return_value = event_manager_instance

        result = self.behaviour.decide(
            driver=self.driver,
            offer=offer,
            time=7,
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
