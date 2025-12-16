import unittest
from unittest.mock import patch, MagicMock

from phase2.behaviour.GreedyDistanceBehaviour import GreedyDistanceBehaviour
from phase2.metrics.Event import EventType
from phase2.Driver import Driver, DriverStatus
from phase2.Point import Point


class TestGreedyDistanceBehaviour(unittest.TestCase):

    def setUp(self):
        self.behaviour = GreedyDistanceBehaviour()

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
        # Arrange
        offer = MagicMock()
        offer.estimated_distance_to_pickup = 5.0  # below threshold
        offer.request.id = 1

        event_manager_instance = MagicMock()
        mock_event_manager.return_value = event_manager_instance

        # Act
        result = self.behaviour.decide(
            driver=self.driver,
            offer=offer,
            time=5,
            run_id="test_run"
        )

        # Assert
        self.assertTrue(result)

        mock_event_manager.assert_called_once_with("test_run")
        event_manager_instance.add_event.assert_called_once()

        event = event_manager_instance.add_event.call_args[0][0]
        self.assertEqual(event.event_type, EventType.REQUEST_PROPOSAL_ACCEPTED)
        self.assertEqual(event.driver_id, self.driver.id)
        self.assertEqual(event.request_id, offer.request.id)

    @patch("phase2.behaviour.GreedyDistanceBehaviour.EventManager")
    def test_denies_offer_when_distance_above_threshold(self, mock_event_manager):
        # Arrange
        offer = MagicMock()
        offer.estimated_distance_to_pickup = 100.0  # above threshold
        offer.request.id = 2

        event_manager_instance = MagicMock()
        mock_event_manager.return_value = event_manager_instance

        # Act
        result = self.behaviour.decide(
            driver=self.driver,
            offer=offer,
            time=5,
            run_id="test_run"
        )

        # Assert
        self.assertFalse(result)

        mock_event_manager.assert_called_once_with("test_run")
        event_manager_instance.add_event.assert_called_once()

        event = event_manager_instance.add_event.call_args[0][0]
        self.assertEqual(event.event_type, EventType.REQUEST_PROPOSAL_DENIED)
        self.assertEqual(event.driver_id, self.driver.id)
        self.assertEqual(event.request_id, offer.request.id)


if __name__ == "__main__":
    unittest.main()
