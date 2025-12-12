import unittest
from phase2.Point import Point
from phase2.Driver import Driver, DriverStatus
from phase2.Request import Request, RequestStatus
from phase2.behaviour.DriverBehaviour import DriverBehaviour

class DummyBehaviour(DriverBehaviour):
    def decide(self):
        pass


"""
Methods
    calc_delivery_estimated_travel_time
        right and wrong input
    calc_delivery_estimated_reward
        right and wrong input
"""

class TestDriver(unittest.TestCase):


    def test_init_valid(self):
        b = DummyBehaviour()
        r = Request(0, Point(0, 0), Point(10, 10), 0, RequestStatus.WAITING, 0, 0)
        d = Driver(1, Point(0, 0), 10.0, DriverStatus.IDLE, r, b, [])
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
            Driver("x", Point(0, 0), 10.0, DriverStatus.IDLE, None, behaviour, [])

        with self.assertRaises(TypeError):
            Driver(1, "not point", 10.0, DriverStatus.IDLE, None, behaviour, [])

        with self.assertRaises(TypeError):
            Driver(1, Point(0, 0), "fast", DriverStatus.IDLE, None, behaviour, [])

        with self.assertRaises(TypeError):
            Driver(1, Point(0, 0), 10.0, "idle", None, behaviour, [])

        with self.assertRaises(TypeError):
            Driver(1, Point(0, 0), 10.0, DriverStatus.IDLE, 123, behaviour, [])

        with self.assertRaises(TypeError):
            Driver(1, Point(0, 0), 10.0, DriverStatus.IDLE, None, "behave", [])

        with self.assertRaises(TypeError):
            Driver(1, Point(0, 0), 10.0, DriverStatus.IDLE, None, behaviour, "not list")

    # ----------------------------------------------------------------------
    # target_point
    # ----------------------------------------------------------------------
    def test_target_point_idle(self):
        b = DummyBehaviour()
        r = None
        d = Driver(1, Point(0, 0), 10.0, DriverStatus.IDLE, r, b, [])
        self.assertIsNone(d.target_point())

    def test_target_point_pickup(self):
        b = DummyBehaviour()
        r = Request(0, Point(0, 0), Point(10, 10), 0, RequestStatus.WAITING, 0, 0)
        d = Driver(1, Point(0, 0), 10.0, DriverStatus.TO_PICKUP, r, b, [])
        self.assertEqual(d.target_point(), r.pickup)

    def test_target_point_dropoff(self):
        b = DummyBehaviour()
        r = Request(0, Point(0, 0), Point(10, 10), 0, RequestStatus.WAITING, 0, 0)
        d = Driver(1, Point(0, 0), 10.0, DriverStatus.TO_DROPOFF, r, b, [])
        self.assertEqual(d.target_point(), r.dropoff)

    def test_target_point_dropoff_wrong_driver_status(self):
        b = DummyBehaviour()
        r = Request(0, Point(0, 0), Point(10, 10), 0, RequestStatus.WAITING, 0, 0)
        d = Driver(1, Point(0, 0), 10.0, DriverStatus.IDLE, r, b, [])
        with self.assertRaises(AssertionError):
            self.assertEqual(d.target_point(), r.dropoff)


    # ----------------------------------------------------------------------
    # compute_direction_vector
    # ----------------------------------------------------------------------
    def test_compute_direction_vector_valid(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(10, 10), 0, RequestStatus.WAITING, 0, 0)
        d = Driver(1, Point(0, 0), 10.0, DriverStatus.TO_PICKUP, r, b, [])

        d.compute_direction_vector()

        # vector from (0,0) to (3,4) normalized → (0.6, 0.8)
        self.assertAlmostEqual(d.dir_vector.x, 0.6)
        self.assertAlmostEqual(d.dir_vector.y, 0.8)

    def test_compute_direction_vector_idle(self):
        b = DummyBehaviour()
        r = None
        d = Driver(1, Point(0, 0), 10.0, DriverStatus.TO_DROPOFF, r, b, [])

        d.compute_direction_vector()
        self.assertIsNone(d.dir_vector)

    # ----------------------------------------------------------------------
    # assign_request
    # ----------------------------------------------------------------------
    def test_assign_request_valid(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(10, 10), 0, RequestStatus.WAITING, 0, 0)
        d = Driver(1, Point(0, 0), 10.0, DriverStatus.IDLE, None, b, [])
        d.assign_request(r, 10)

        self.assertEqual(d.status, DriverStatus.TO_PICKUP)
        self.assertEqual(d.current_request, r)
        self.assertIsNotNone(d.dir_vector)

    def test_assign_request_invalid(self):
        b = DummyBehaviour()
        r = None
        d = Driver(1, Point(0, 0), 10.0, DriverStatus.IDLE, None, b, [])

        with self.assertRaises(TypeError):
            d.assign_request("not req", 5)

        with self.assertRaises(TypeError):
            d.assign_request(r, "time")

    # ----------------------------------------------------------------------
    # step
    # ----------------------------------------------------------------------
    def test_step_valid(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(10, 10), 0, RequestStatus.WAITING, 0, 0)
        d = Driver(1, Point(0, 0), 5.0, DriverStatus.TO_PICKUP, r, b, [])
        d.compute_direction_vector()

        # direction is (0.6, 0.8), speed=5, dt=1
        d.step(1)

        self.assertAlmostEqual(d.position.x, 3)
        self.assertAlmostEqual(d.position.y, 4)


    def test_step_invalid_dt(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(10, 10), 0, RequestStatus.WAITING, 0, 0)
        d = Driver(1, Point(0, 0), 5.0, DriverStatus.TO_PICKUP, r, b, [])
        with self.assertRaises(TypeError):
            d.step("1.2")       # dt must be int/float

    # ----------------------------------------------------------------------
    # complete_pickup
    # ----------------------------------------------------------------------
    def test_complete_pickup_valid(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(10, 10), 1, RequestStatus.WAITING, 0, 0)
        d = Driver(1, Point(3, 4), 5.0, DriverStatus.TO_PICKUP, r, b, [])
        d.complete_pickup(1)

        self.assertEqual(d.status, DriverStatus.TO_DROPOFF)
        self.assertEqual(d.target_point(), r.dropoff)
        self.assertEqual(d.current_request.status, RequestStatus.PICKED)

    def test_complete_pickup_invalid(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(10, 10), 1, RequestStatus.WAITING, 0, 0)
        d = Driver(1, Point(3, 4), 5.0, DriverStatus.TO_PICKUP, r, b, [])

        with self.assertRaises(TypeError):
            d.complete_pickup("bad")

    # ----------------------------------------------------------------------
    # complete_dropoff
    # ----------------------------------------------------------------------
    def test_complete_dropoff_valid(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(10, 10), 1, RequestStatus.WAITING, 0, 0)
        d = Driver(1, Point(10, 10), 5.0, DriverStatus.TO_PICKUP, r, b, [])
        d.complete_dropoff(15)

        self.assertEqual(d.status, DriverStatus.IDLE)
        self.assertEqual(d.target_point(), None)
        self.assertEqual(d.current_request.status, RequestStatus.DELIVERED)



    def test_complete_dropoff_invalid(self):
        b = DummyBehaviour()
        r = Request(0, Point(3, 4), Point(10, 10), 1, RequestStatus.WAITING, 0, 0)
        d = Driver(1, Point(10, 10), 5.0, DriverStatus.TO_PICKUP, r, b, [])
        with self.assertRaises(TypeError):
            d.complete_dropoff([])
"""
    # ----------------------------------------------------------------------
    # calc_delivery_estimated_travel_time
    # ----------------------------------------------------------------------
    def test_calc_estimated_travel_time_valid(self):
        d = 

        # distance (0,0)->(3,4)=5, (3,4)->(6,8)=5 → total=10
        expected = 10 / 10.0

        t = d.calc_delivery_estimated_travel_time(self.request)
        self.assertAlmostEqual(t, expected)

    def test_calc_estimated_travel_time_invalid(self):
        d = 
        with self.assertRaises(TypeError):
            d.calc_delivery_estimated_travel_time("bad")

    def test_calc_estimated_travel_time_zero_speed(self):
        d = 
        with self.assertRaises(ZeroDivisionError):
            d.calc_delivery_estimated_travel_time(self.request)

    # ----------------------------------------------------------------------
    # calc_delivery_estimated_reward
    # ----------------------------------------------------------------------
    def test_calc_estimated_reward_valid(self):
        d = 

        travel_time = 10 / 10.0  # from previous test
        expected = 5.0 + 2.0 * travel_time

        r = d.calc_delivery_estimated_reward(self.request)
        self.assertAlmostEqual(r, expected)

    def test_calc_estimated_reward_invalid(self):
        d = Driver(1, Point(0, 0), 10.0, DriverStatus.IDLE, None, self.behaviour, [])
        with self.assertRaises(TypeError):
            d.calc_delivery_estimated_reward([])

"""
if __name__ == "__main__":
    unittest.main()
