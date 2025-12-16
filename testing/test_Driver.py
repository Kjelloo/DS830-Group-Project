import unittest
from unittest.mock import MagicMock

from phase2.Point import Point
from phase2.Driver import Driver, DriverStatus
from phase2.Request import Request, RequestStatus
from phase2.behaviour.DriverBehaviour import DriverBehaviour
from phase2.behaviour.GreedyDistanceBehaviour import GreedyDistanceBehaviour


class DummyBehaviour(DriverBehaviour):
    def decide(self):
        pass


class TestDriver(unittest.TestCase):

    def test_init_valid(self):
        b = DummyBehaviour()
        r = Request(0, Point(0, 0), Point(10, 10),0,
                    RequestStatus.WAITING, 0, 0, run_id="test_run")
        d = Driver(1, Point(0, 0), 10.0,
                   DriverStatus.IDLE, r, b, [], run_id="test_run")
        self.assertEqual(d.id, 1)
        self.assertEqual(d.position, Point(0, 0))
        self.assertEqual(d.speed, 10.0)
        self.assertEqual(d.status, DriverStatus.IDLE)
        self.assertEqual(d.current_request, r)
        self.assertEqual(d.behaviour, b)
        self.assertEqual(d.history, [])

    def test_init_invalid_types(self):
        behaviour = DummyBehaviour()
        with self.assertRaises(TypeError):
            Driver("x", Point(0, 0), 10.0, DriverStatus.IDLE,
                   None, behaviour, [], run_id="test_run")

        with self.assertRaises(TypeError):
            Driver(1, "not point", 10.0, DriverStatus.IDLE,
                   None, behaviour, [], run_id="test_run")

        with self.assertRaises(TypeError):
            Driver(1, Point(0, 0), "fast", DriverStatus.IDLE,
                   None, behaviour, [], run_id="test_run")

        with self.assertRaises(TypeError):
            Driver(1, Point(0, 0), 10.0, "idle",
                   None, behaviour, [], run_id="test_run")

        with self.assertRaises(TypeError):
            Driver(1, Point(0, 0), 10.0, DriverStatus.IDLE,
                   123, behaviour, [], run_id="test_run")

        with self.assertRaises(TypeError):
            Driver(1, Point(0, 0), 10.0, DriverStatus.IDLE,
                   None, "behave", [], run_id="test_run")

        with self.assertRaises(TypeError):
            Driver(1, Point(0, 0), 10.0, DriverStatus.IDLE,
                   None, behaviour, "not list", run_id="test_run")

    def test_target_point_idle(self):
        b = DummyBehaviour()
        r = None
        d = Driver(1, Point(0, 0), 10.0,
                   DriverStatus.IDLE, r, b, [], run_id="test_run")
        self.assertIsNone(d.target_point())

    def test_target_point_pickup(self):
        b = DummyBehaviour()
        r = Request(0, Point(0, 0), Point(10, 10),
                    0, RequestStatus.WAITING, 0, 0, "test_run")
        d = Driver(1, Point(0, 0), 10.0,
                   DriverStatus.TO_PICKUP, r, b, [], run_id="test_run")
        self.assertEqual(d.target_point(), r.pickup)

    def test_target_point_dropoff(self):
        b = DummyBehaviour()
        r = Request(0, Point(0, 0), Point(10, 10), 0,
                    RequestStatus.WAITING, 0, 0, run_id="test_run")
        d = Driver(1, Point(0, 0), 10.0, DriverStatus.TO_DROPOFF, r,
                   b, [], run_id="test_run_id")
        self.assertEqual(d.target_point(), r.dropoff)

    def test_target_point_dropoff_wrong_driver_status(self):
        b = DummyBehaviour()
        r = Request(0, Point(0, 0), Point(10, 10), 0,
                    RequestStatus.WAITING, 0, 0, run_id="test_run")
        d = Driver(1, Point(0, 0), 10.0,
                   DriverStatus.IDLE, r, b, [], run_id="test_run")
        with self.assertRaises(AssertionError):
            self.assertEqual(d.target_point(), r.dropoff)

    def test_compute_direction_vector_valid(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(10, 10), 0,
                    RequestStatus.WAITING, 0, 0, run_id="test_run")
        d = Driver(1, Point(0, 0), 10.0,
                   DriverStatus.TO_PICKUP, r, b, [], run_id="test_run")

        d.compute_direction_vector()

        # vector from (0,0) to (3,4) normalized → (0.6, 0.8)
        self.assertAlmostEqual(d.dir_vector.x, 0.6)
        self.assertAlmostEqual(d.dir_vector.y, 0.8)

    def test_compute_direction_vector_idle(self):
        b = DummyBehaviour()
        r = None
        d = Driver(1, Point(0, 0), 10.0,
                   DriverStatus.TO_DROPOFF, r, b, [], run_id="test_run")

        d.compute_direction_vector()
        self.assertIsNone(d.dir_vector)

    def test_assign_request_valid(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(10, 10), 0,
                    RequestStatus.WAITING, 0, 0, run_id="test_run")
        d = Driver(1, Point(0, 0), 10.0,
                   DriverStatus.IDLE, None, b, [], run_id="test_run")
        d.assign_request(r, 10)

        self.assertEqual(d.status, DriverStatus.TO_PICKUP)
        self.assertEqual(d.current_request, r)
        self.assertIsNotNone(d.dir_vector)

    def test_assign_request_invalid(self):
        b = DummyBehaviour()
        r = None
        d = Driver(1, Point(0, 0), 10.0,
                   DriverStatus.IDLE, None, b, [], run_id="test_run")

        with self.assertRaises(TypeError):
            d.assign_request("not req", 5)

        with self.assertRaises(TypeError):
            d.assign_request(r, "time")


    def test_step_valid(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(10, 10), 0,
                    RequestStatus.WAITING, 0, 0, run_id="test_run")
        d = Driver(1, Point(0, 0), 5.0,
                   DriverStatus.TO_PICKUP, r, b, [], run_id="test_run")
        d.compute_direction_vector()

        # direction is (0.6, 0.8), speed=5, dt=1
        d.step(1)

        self.assertAlmostEqual(d.position.x, 3)
        self.assertAlmostEqual(d.position.y, 4)


    def test_step_invalid_dt(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(10, 10), 0,
                    RequestStatus.WAITING, 0, 0, run_id="test_run")
        d = Driver(1, Point(0, 0), 5.0,
                   DriverStatus.TO_PICKUP, r, b, [], run_id="test_run")
        with self.assertRaises(TypeError):
            d.step("1.2")       # dt must be int/float

    def test_complete_pickup_valid(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(10, 10), 1,
                    RequestStatus.WAITING, 0, 0, run_id="test_run")
        d = Driver(1, Point(3, 4), 5.0,
                   DriverStatus.TO_PICKUP, r, b, [], run_id="test_run")
        d.complete_pickup(1)

        self.assertEqual(d.status, DriverStatus.TO_DROPOFF)
        self.assertEqual(d.target_point(), r.dropoff)
        self.assertEqual(d.current_request.status, RequestStatus.PICKED)

    def test_complete_pickup_invalid(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(10, 10), 1,
                    RequestStatus.WAITING, 0, 0, run_id="test_run")
        d = Driver(1, Point(3, 4), 5.0,
                   DriverStatus.TO_PICKUP, r, b, [], run_id="test_run")

        with self.assertRaises(TypeError):
            d.complete_pickup("bad")

    def test_complete_dropoff_valid(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(10, 10), 1,
                    RequestStatus.WAITING, 0, 0, run_id="test_run")
        d = Driver(1, Point(10, 10), 5.0,
                   DriverStatus.TO_PICKUP, r, b, [], run_id="test_run")
        d.complete_dropoff(15)

        self.assertEqual(d.status, DriverStatus.IDLE)
        self.assertEqual(d.target_point(), None)
        self.assertEqual(d.current_request, None)

    def test_complete_dropoff_invalid(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(10, 10), 1,
                    RequestStatus.WAITING, 0, 0, run_id="test_run")
        d = Driver(1, Point(10, 10), 5.0,
                   DriverStatus.TO_PICKUP, r, b, [], run_id="test_run")
        with self.assertRaises(TypeError):
            d.complete_dropoff([])

    def test_calc_estimated_total_dist_valid(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(7, 7), 1,
                    RequestStatus.WAITING, 0, 0, run_id="test_run")
        d = Driver(1, Point(0, 0), 5.0,
                   DriverStatus.TO_PICKUP, r, b, [], run_id="test_run")
        # distance (0,0)->(3,4)=5, (3,4)->(7,7)=5 → total=10
        expected = 10

        t = d.calc_estimated_total_dist_to_delivery(r)
        self.assertAlmostEqual(t, expected)

    def test_calc_estimated_total_dist_invalid(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(7, 7), 1,
                    RequestStatus.WAITING, 0, 0, run_id="test_run")
        d = Driver(1, Point(0, 0), 5.0,
                   DriverStatus.TO_PICKUP, r, b, [], run_id="test_run")
        with self.assertRaises(TypeError):
            d.calc_estimated_total_dist_to_delivery("bad")

    def test_calc_estimated_reward_valid(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(7, 7), 1,
                    RequestStatus.WAITING, 0, 0, run_id="test_run")
        d = Driver(1, Point(0, 0), 5,
                   DriverStatus.TO_PICKUP, r, b, [], run_id="test_run")

        travel_dist = 10
        expected = 15 + 0.7 * travel_dist

        actual_reward = d.calc_estimated_delivery_reward(r)
        self.assertAlmostEqual(actual_reward, expected)

    def test_calc_estimated_reward_invalid(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(7, 7), 1,
                    RequestStatus.WAITING, 0, 0, run_id="test_run")
        d = Driver(1, Point(0, 0), 0,
                   DriverStatus.TO_PICKUP, r, b, [], run_id="test_run")

        with self.assertRaises(TypeError):
            d.calc_estimated_delivery_reward([])

    # Testing of newly added method expire_current_request
    def setUp(self):
        self.driver = Driver(
            id=1,
            position=Point(1,1),  # can be mocked
            speed=1.0,
            status=DriverStatus.IDLE,
            current_request=None,
            behaviour=GreedyDistanceBehaviour(),
            history=[],
            run_id="test_run")

    def test_expire_current_request_with_active_request(self):
        mock_request = MagicMock(spec=Request)
        self.driver.current_request = mock_request
        self.driver.status = DriverStatus.TO_PICKUP
        self.driver.compute_direction_vector = MagicMock()

        time = 10

        self.driver.expire_current_request(time)

        mock_request.mark_expired.assert_called_once_with(time)

        self.assertIn(mock_request, self.driver.history)

        self.assertIsNone(self.driver.current_request)

        self.assertEqual(self.driver.status, DriverStatus.IDLE)

        self.driver.compute_direction_vector.assert_called_once()

    def test_expire_current_request_with_no_active_request(self):
        self.driver.current_request = None
        self.driver.compute_direction_vector = MagicMock()
        original_history = list(self.driver.history)
        original_status = self.driver.status

        self.driver.expire_current_request(time=10)

        self.assertEqual(self.driver.history, original_history)

        self.assertEqual(self.driver.status, original_status)

        self.driver.compute_direction_vector.assert_not_called()

if __name__ == "__main__":
    unittest.main()
