import unittest
from phase2.metrics.Event import Event, EventType

class TestEvent(unittest.TestCase):

    def test_create_event_all_fields(self):
        event = Event(
            timestamp=5,
            event_type=EventType.REQUEST_GENERATED,
            driver_id=1,
            request_id=2,
            wait_time=10
        )

        self.assertEqual(event.timestamp, 5)
        self.assertEqual(event.event_type, EventType.REQUEST_GENERATED)
        self.assertEqual(event.driver_id, 1)
        self.assertEqual(event.request_id, 2)
        self.assertEqual(event.wait_time, 10)

    def test_create_event_optional_none(self):
        event = Event(
            timestamp=0,
            event_type=EventType.DRIVER_IDLE,
            driver_id=None,
            request_id=None,
            wait_time=None
        )

        self.assertIsNone(event.driver_id)
        self.assertIsNone(event.request_id)
        self.assertIsNone(event.wait_time)

    def test_invalid_timestamp_type(self):
        with self.assertRaises(TypeError):
            Event(
                timestamp="not int",
                event_type=EventType.REQUEST_GENERATED,
                driver_id=1,
                request_id=2,
                wait_time=10
            )

    def test_invalid_event_type(self):
        with self.assertRaises(TypeError):
            Event(
                timestamp=0,
                event_type="not an EventType",
                driver_id=1,
                request_id=2,
                wait_time=10
            )

    def test_invalid_driver_id_type(self):
        with self.assertRaises(TypeError):
            Event(
                timestamp=0,
                event_type=EventType.REQUEST_GENERATED,
                driver_id="1",  # should be int or None
                request_id=2,
                wait_time=10
            )

    def test_invalid_request_id_type(self):
        with self.assertRaises(TypeError):
            Event(
                timestamp=0,
                event_type=EventType.REQUEST_GENERATED,
                driver_id=1,
                request_id="2",  # should be int or None
                wait_time=10
            )

    def test_invalid_wait_time_type(self):
        with self.assertRaises(TypeError):
            Event(
                timestamp=0,
                event_type=EventType.REQUEST_GENERATED,
                driver_id=1,
                request_id=2,
                wait_time="10"  # should be int or None
            )

    def test_event_type_enum_values(self):
        # Ensure all EventType members exist and have correct values
        expected_values = {
            "REQUEST_GENERATED": 1,
            "REQUEST_ASSIGNED": 2,
            "REQUEST_PROPOSAL_ACCEPTED": 3,
            "REQUEST_PROPOSAL_DENIED": 4,
            "REQUEST_EXPIRED": 5,
            "REQUEST_PICKED": 6,
            "REQUEST_DELIVERED": 7,
            "BEHAVIOUR_CHANGED": 8,
            "DRIVER_IDLE": 9
        }
        for name, value in expected_values.items():
            self.assertEqual(EventType[name].value, value)


if __name__ == "__main__":
    unittest.main()
