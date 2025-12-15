import unittest
from unittest.mock import patch, mock_open
from phase2.metrics.EventManager import EventManager
from phase2.metrics.Event import Event, EventType


class TestEventManager(unittest.TestCase):

    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_init_creates_directory_and_file(self, mock_file, mock_makedirs, mock_exists):
        # File does not exist, directory does not exist
        mock_exists.side_effect = [False, False]  # First for directory, second for file

        manager = EventManager("non_test")
        mock_makedirs.assert_called_once()
        mock_file.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    def test_init_skips_test_run(self, mock_file):
        manager = EventManager("test_run")
        # Should not open any files
        mock_file.assert_not_called()

    @patch("builtins.open", new_callable=mock_open)
    def test_add_event_writes_to_file(self, mock_file):
        manager = EventManager("test_run")
        manager.filepath = "dummy.csv"

        mock_file().write.reset_mock()

        event = Event(timestamp=5,
                      event_type=EventType.REQUEST_GENERATED,
                      driver_id=1,
                      request_id=2,
                      wait_time=10)

        manager.add_event(event)

        mock_file.assert_called_with("dummy.csv", 'a')
        handle = mock_file()
        handle.write.assert_called_once_with(
            "5, 1, 1, 2, 10\n"
        )

    @patch("builtins.open", new_callable=mock_open,
           read_data="timestamp, event_type, driver_id, request_id, wait_time\n5, 1, 1, 2, 10\n")
    def test_get_events_reads_file(self, mock_file):
        manager = EventManager("test_run")
        manager.filepath = "dummy.csv"

        events = manager.get_events()
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event.timestamp, 5)
        self.assertEqual(event.event_type, EventType.REQUEST_GENERATED)
        self.assertEqual(event.driver_id, 1)
        self.assertEqual(event.request_id, 2)
        self.assertEqual(event.wait_time, 10)

    @patch("builtins.open", new_callable=mock_open, read_data=
           "timestamp, event_type, driver_id, request_id, wait_time\n"
           "5, 1, 1, 2, 10\n"
           "6, 3, 2, 3, 15\n"
           "7, 4, None, None, None\n")
    def test_get_event_by_type_filters(self, mock_file):
        manager = EventManager("test_run")
        manager.filepath = "dummy.csv"

        events = manager.get_event_by_type(EventType.REQUEST_PROPOSAL_ACCEPTED)
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event.timestamp, 6)
        self.assertEqual(event.event_type, EventType.REQUEST_PROPOSAL_ACCEPTED)
        self.assertEqual(event.driver_id, 2)
        self.assertEqual(event.request_id, 3)
        self.assertEqual(event.wait_time, 15)

    @patch("builtins.open", new_callable=mock_open)
    def test_add_event_skips_test_run(self, mock_file):
        manager = EventManager("test_run")
        event = Event(1, EventType.REQUEST_GENERATED, 1, 2, 3)
        manager.add_event(event)
        mock_file.assert_not_called()


if __name__ == "__main__":
    unittest.main()
