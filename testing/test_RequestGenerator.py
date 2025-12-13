import unittest
from unittest.mock import patch, MagicMock

from phase2.RequestGenerator import RequestGenerator
from phase2.Request import RequestStatus


class TestRequestGeneratorInit(unittest.TestCase):
    @patch("phase2.RequestGenerator")
    def test_valid_initialization(self, mock_request_generator):
        rg = RequestGenerator(
            rate=1.5,
            width=10,
            height=5,
            start_id=100,
            run_id="test_run"
        )
        self.assertEqual(rg.rate, 1.5)
        self.assertEqual(rg.width, 10)
        self.assertEqual(rg.height, 5)
        self.assertEqual(rg.next_id, 100)
        self.assertEqual(rg.run_id, "test_run")

    @patch("phase2.RequestGenerator")
    def test_invalid_rate_type(self, mock_request_generator):
        with self.assertRaises(TypeError):
            RequestGenerator(rate="fast", width=10, height=10, start_id=0, run_id="test_run")

    @patch("phase2.RequestGenerator")
    def test_negative_rate(self, mock_request_generator):
        with self.assertRaises(ValueError):
            RequestGenerator(rate=-1, width=10, height=10, start_id=0, run_id="test_run")

    @patch("phase2.RequestGenerator")
    def test_invalid_width_height_type(self, mock_request_generator):
        with self.assertRaises(TypeError):
            RequestGenerator(rate=1, width="wide", height=10, start_id=0, run_id="test_run")

    @patch("phase2.RequestGenerator")
    def test_negative_width_height(self, mock_request_generator):
        with self.assertRaises(ValueError):
            RequestGenerator(rate=1, width=-1, height=10, start_id=0, run_id="test_run")

    @patch("phase2.RequestGenerator")
    def test_invalid_start_id_type(self, mock_request_generator):
        with self.assertRaises(TypeError):
            RequestGenerator(rate=1, width=10, height=10, start_id="0", run_id="test_run")

    @patch("phase2.RequestGenerator")
    def test_invalid_run_id_type(self, mock_request_generator):
        with self.assertRaises(TypeError):
            RequestGenerator(rate=1, width=10, height=10, start_id=0, run_id=123)


class TestRequestGeneratorMaybeGenerate(unittest.TestCase):

    @patch("phase2.RequestGenerator.EventManager")
    @patch("phase2.RequestGenerator.random.random")
    def test_generate_zero_requests_when_rate_zero(
        self, mock_random, mock_event_manager):
        mock_random.return_value = 0.0

        rg = RequestGenerator(rate=0, width=10, height=10, start_id=0, run_id="test_run")
        result = rg.maybe_generate(time=0)

        self.assertEqual(result, [])
        mock_event_manager.assert_called_once_with("test_run")

    def test_negative_time_raises(self):
        rg = RequestGenerator(rate=1, width=10, height=10, start_id=0, run_id="test_run")
        with self.assertRaises(ValueError):
            rg.maybe_generate(time=-1)

    @patch("phase2.RequestGenerator.random.uniform")
    @patch("phase2.RequestGenerator.random.random")
    def test_generate_exact_base_requests(
        self, mock_random, mock_uniform
    ):
        # rate = 2.0 → always 2 requests
        mock_random.return_value = 0.99
        mock_uniform.side_effect = [1, 1, 2, 2, 3, 3, 4, 4]

        rg = RequestGenerator(rate=2.0, width=10, height=10, start_id=10, run_id="test_run")
        result = rg.maybe_generate(time=5)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].id, 10)
        self.assertEqual(result[1].id, 11)
        self.assertEqual(rg.next_id, 12)

    @patch("phase2.RequestGenerator.random.uniform")
    @patch("phase2.RequestGenerator.random.random")
    def test_fractional_rate_probability_adds_extra_request(
        self, mock_random, mock_uniform
    ):
        # rate = 1.5 → base 1 + 1 extra if random < 0.5
        mock_random.return_value = 0.3
        mock_uniform.side_effect = [1, 1, 2, 2, 3, 3, 4, 4]

        rg = RequestGenerator(rate=1.5, width=10, height=10, start_id=0, run_id="test_run")
        result = rg.maybe_generate(time=1)

        self.assertEqual(len(result), 2)

    @patch("phase2.RequestGenerator.random.uniform")
    @patch("phase2.RequestGenerator.random.random")
    def test_request_fields_are_correct(
        self, mock_random, mock_uniform
    ):
        mock_random.return_value = 0.0
        mock_uniform.side_effect = [5, 6, 7, 8]

        rg = RequestGenerator(rate=1, width=10, height=10, start_id=7, run_id="test_run")
        result = rg.maybe_generate(time=3)

        req = result[0]
        self.assertEqual(req.id, 7)
        self.assertEqual(req.creation_time, 3)
        self.assertEqual(req.status, RequestStatus.WAITING)
        self.assertIsNone(req.assigned_driver)
        self.assertEqual(req.wait_time, 0)
        self.assertEqual(req.run_id, "test_run")

    @patch("phase2.RequestGenerator.EventManager")
    @patch("phase2.RequestGenerator.random.uniform")
    @patch("phase2.RequestGenerator.random.random")
    def test_event_manager_called_for_each_request(
        self, mock_random, mock_uniform, mock_event_manager
    ):
        mock_random.return_value = 0.0
        mock_uniform.side_effect = [1, 1, 2, 2]

        event_manager_instance = MagicMock()
        mock_event_manager.return_value = event_manager_instance

        rg = RequestGenerator(rate=1, width=10, height=10, start_id=0, run_id="test_run")
        rg.maybe_generate(time=7)

        event_manager_instance.add_event.assert_called_once()