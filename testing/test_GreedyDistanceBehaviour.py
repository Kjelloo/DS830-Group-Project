import unittest
from unittest.mock import patch, MagicMock

from phase2.behaviour.GreedyDistanceBehaviour import GreedyDistanceBehaviour
from phase2.metrics.Event import EventType
from phase2.Request import Request, RequestStatus
from phase2.Driver import Driver, DriverStatus
from phase2.Point import Point
from phase2.Offer import Offer


class TestGreedyDistanceBehaviour(unittest.TestCase):

    def setUp(self):
        self.behaviour = GreedyDistanceBehaviour()
        self.request_close = Request(
            id=1,
            pickup=Point(2, 0),
            dropoff=Point(5, 5),
            creation_time=0,
            status=RequestStatus.WAITING,
            assigned_driver=None,
            wait_time=0,
            run_id="test_run"
        )
        self.request_far = Request(
            id=2,
            pickup=Point(20, 0),
            dropoff=Point(25, 25),
            creation_time=0,
            status=RequestStatus.WAITING,
            assigned_driver=None,
            wait_time=0,
            run_id="test_run"
        )
        self.driver = Driver(
            id=1,
            position=Point(0, 0),
            speed=1.0,
            status=DriverStatus.IDLE,
            current_request=None,
            behaviour=self.behaviour,
            history=[],
            run_id="test_run"
        )

    @patch("phase2.behaviour.GreedyDistanceBehaviour.EventManager")
    def test_accepts_offer_when_distance_below_threshold(self, mock_event_manager):
        offer = Offer(self.driver, self.request_close, 0, 0)  # travel times not used

        event_manager_instance = MagicMock()
        mock_event_manager.return_value = event_manager_instance

        result = self.behaviour.decide(
            driver=self.driver,
            offer=offer,
            time=5,
            run_id="test_run"
        )

        self.assertTrue(result)

        mock_event_manager.assert_called_once_with("test_run")
        event_manager_instance.add_event.assert_called_once()
        event = event_manager_instance.add_event.call_args[0][0]
        self.assertEqual(event.event_type, EventType.REQUEST_PROPOSAL_ACCEPTED)
        self.assertEqual(event.driver_id, self.driver.id)
        self.assertEqual(event.request_id, self.request_close.id)

    @patch("phase2.behaviour.GreedyDistanceBehaviour.EventManager")
    def test_denies_offer_when_distance_above_threshold(self, mock_event_manager):
        offer = Offer(self.driver, self.request_far, 0, 0)

        event_manager_instance = MagicMock()
        mock_event_manager.return_value = event_manager_instance

        result = self.behaviour.decide(
            driver=self.driver,
            offer=offer,
            time=5,
            run_id="test_run"
        )

        self.assertFalse(result)

        mock_event_manager.assert_called_once_with("test_run")
        event_manager_instance.add_event.assert_called_once()
        event = event_manager_instance.add_event.call_args[0][0]
        self.assertEqual(event.event_type, EventType.REQUEST_PROPOSAL_DENIED)
        self.assertEqual(event.driver_id, self.driver.id)
        self.assertEqual(event.request_id, self.request_far.id)


if __name__ == "__main__":
    unittest.main()
