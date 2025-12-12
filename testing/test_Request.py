import unittest
from unittest.mock import MagicMock, patch
from phase2.Request import Request, RequestStatus
from phase2.Point import Point
from phase2.metrics.Event import EventType

class TestRequest(unittest.TestCase):
    def setUp(self):
        """Set up a basic request object."""
        self.pickup = Point(0, 0)
        self.dropoff = Point(10, 10)
        self.creation_time = 0
        self.run_id = "test_run"

        # Patch EventManager to prevent CSV writing
        patcher = patch("phase2.Request.EventManager")
        self.addCleanup(patcher.stop)
        self.mock_event_manager_class = patcher.start()
        self.mock_event_manager = MagicMock()
        self.mock_event_manager_class.return_value = self.mock_event_manager

        self.request = Request(
            id=1,
            pickup=self.pickup,
            dropoff=self.dropoff,
            creation_time=self.creation_time,
            status=RequestStatus.WAITING,
            assigned_driver=None,
            wait_time=0,
            run_id=self.run_id
        )

    def test_is_active(self):
        """Test is_active for all statuses dynamically."""
        active_statuses = {RequestStatus.WAITING, RequestStatus.ASSIGNED, RequestStatus.PICKED}
        for status in RequestStatus:
            with self.subTest(status=status):
                self.request.status = status
                expected = status in active_statuses
                self.assertEqual(self.request.is_active(), expected)

    def test_mark_assigned_triggers_event(self):
        driver_id = 7
        time = 5
        self.request.mark_assigned(driver_id, time)

        self.assertEqual(self.request.status, RequestStatus.ASSIGNED)
        self.assertEqual(self.request.assigned_driver, driver_id)
        self.mock_event_manager.add_event.assert_called_once()
        event_arg = self.mock_event_manager.add_event.call_args[0][0]
        self.assertEqual(event_arg.event_type, EventType.REQUEST_ASSIGNED)

    def test_mark_picked_triggers_event(self):
        self.request.assigned_driver = 13
        time = 10
        self.request.mark_picked(time)

        self.assertEqual(self.request.status, RequestStatus.PICKED)
        self.mock_event_manager.add_event.assert_called_once()
        event_arg = self.mock_event_manager.add_event.call_args[0][0]
        self.assertEqual(event_arg.event_type, EventType.REQUEST_PICKED)

    def test_mark_delivered_triggers_event(self):
        self.request.assigned_driver = 4
        time = 15
        self.request.mark_delivered(time)

        self.assertEqual(self.request.status, RequestStatus.DELIVERED)
        self.mock_event_manager.add_event.assert_called_once()
        event_arg = self.mock_event_manager.add_event.call_args[0][0]
        self.assertEqual(event_arg.event_type, EventType.REQUEST_DELIVERED)

    def test_mark_expired_triggers_event(self):
        time = 3
        self.request.mark_expired(time)

        self.assertEqual(self.request.status, RequestStatus.EXPIRED)
        self.mock_event_manager.add_event.assert_called_once()
        event_arg = self.mock_event_manager.add_event.call_args[0][0]
        self.assertEqual(event_arg.event_type, EventType.REQUEST_EXPIRED)

    def test_event_invalid_time(self):
        time = "time"
        self.assertRaises(TypeError, self.request.mark_picked, time)

    def test_update_wait(self):
        current_time = 4
        self.request.update_wait(current_time)
        self.assertEqual(self.request.wait_time, current_time - self.creation_time)

    def test_update_wait_invalid(self):
        current_time = "5"
        self.assertRaises(TypeError, self.request.update_wait, current_time)

    def test_str_and_repr(self):
        s = str(self.request)
        r = repr(self.request)
        self.assertIsInstance(s, str)
        self.assertIsInstance(r, str)
        self.assertEqual(s, r)

if __name__ == "__main__":
    unittest.main()