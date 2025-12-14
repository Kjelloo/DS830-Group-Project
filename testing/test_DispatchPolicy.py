import unittest
from phase2.dispatch.DispatchPolicy import DispatchPolicy
from phase2.Driver import Driver, DriverStatus
from phase2.Request import Request, RequestStatus
from phase2.Point import Point
from phase2.behaviour.DriverBehaviour import DriverBehaviour

class DummyBehaviour(DriverBehaviour):
    def decide(self):
        return True

class DummyDispatchPolicy(DispatchPolicy):
    def assign(self, drivers, requests, time, run_id):
        return []


class TestDispatchPolicy(unittest.TestCase):

    def setUp(self):
        self.policy = DummyDispatchPolicy()
        self.driver = Driver(
            id=1,
            position=Point(0, 0),
            speed=1.0,
            status=DriverStatus.IDLE,
            current_request=None,
            behaviour=DummyBehaviour(),
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

    def test_assign_returns_empty_list(self):
        result = self.policy.assign([self.driver], [self.request], 5, "test_run")
        self.assertEqual(result, [])

    def test_str_and_repr(self):
        self.assertEqual(str(self.policy), "DummyDispatchPolicy")
        self.assertEqual(repr(self.policy), "DummyDispatchPolicy")

    def test_type_check_valid_inputs(self):
        try:
            self.policy._check_types([self.driver], [self.request], 0, "run1")
        except TypeError:
            self.fail("_check_types raised TypeError unexpectedly with valid input")

    def test_type_check_invalid_drivers_type(self):
        with self.assertRaises(TypeError):
            self.policy._check_types("not a list", [self.request], 0, "run1")

    def test_type_check_invalid_driver_elements(self):
        with self.assertRaises(TypeError):
            self.policy._check_types([123], [self.request], 0, "run1")

    def test_type_check_invalid_requests_type(self):
        with self.assertRaises(TypeError):
            self.policy._check_types([self.driver], "not a list", 0, "run1")

    def test_type_check_invalid_request_elements(self):
        with self.assertRaises(TypeError):
            self.policy._check_types([self.driver], [123], 0, "run1")

    def test_type_check_invalid_time(self):
        with self.assertRaises(TypeError):
            self.policy._check_types([self.driver], [self.request], "not int", "run1")

    def test_type_check_invalid_run_id(self):
        with self.assertRaises(TypeError):
            self.policy._check_types([self.driver], [self.request], 0, 123)


if __name__ == "__main__":
    unittest.main()
