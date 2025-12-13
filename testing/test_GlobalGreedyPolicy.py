import unittest
from phase2.Point import Point
from phase2.Driver import Driver, DriverStatus
from phase2.Request import Request, RequestStatus
from phase2.dispatch.GlobalGreedyPolicy import GlobalGreedyPolicy
from phase2.behaviour.EarningsMaxBehaviour import EarningsMaxBehaviour

b = EarningsMaxBehaviour()


class TestGlobalGreedyPolicy(unittest.TestCase):

    def setUp(self):
        self.policy = GlobalGreedyPolicy()

        # Create drivers
        self.driver_idle_1 = Driver(1, Point(0, 0), 1.0, DriverStatus.IDLE, None,
                                    b, [], "test_run")
        self.driver_idle_2 = Driver(2, Point(5, 0), 1.0, DriverStatus.IDLE, None,
                                    b, [], "test_run")
        self.driver_busy = Driver(3, Point(10, 0), 1.0, DriverStatus.TO_PICKUP, None,
                                  b, [], "test_run")

        # Create requests
        self.request_waiting_1 = Request(1, Point(1, 0), Point(2, 0), 0, RequestStatus.WAITING,
                                         None, 0, "test_run")
        self.request_waiting_2 = Request(2, Point(6, 0), Point(7, 0), 0, RequestStatus.WAITING,
                                         None, 0, "test_run")
        self.request_completed = Request(3, Point(10, 0), Point(12, 0), 0, RequestStatus.DELIVERED,
                                         None, 0, "test_run")

    def test_basic_greedy_assignment(self):
        matched = self.policy.assign(
            drivers=[self.driver_idle_1, self.driver_idle_2, self.driver_busy],
            requests=[self.request_waiting_1, self.request_waiting_2, self.request_completed],
            time=0,
            run_id="test_run"
        )

        # Only idle drivers and waiting requests are considered
        self.assertEqual(len(matched), 2)

        # Check that driver-request pairs are as expected (greedy by distance)
        self.assertEqual(matched[0], (self.driver_idle_1, self.request_waiting_1))
        self.assertEqual(matched[1], (self.driver_idle_2, self.request_waiting_2))

        # No driver or request reused
        driver_ids = [d.id for d, r in matched]
        request_ids = [r.id for d, r in matched]
        self.assertEqual(len(driver_ids), len(set(driver_ids)))
        self.assertEqual(len(request_ids), len(set(request_ids)))

    def test_no_idle_drivers(self):
        matched = self.policy.assign(
            drivers=[self.driver_busy],
            requests=[self.request_waiting_1],
            time=0,
            run_id="test_run"
        )
        self.assertEqual(matched, [])

    def test_no_waiting_requests(self):
        matched = self.policy.assign(
            drivers=[self.driver_idle_1],
            requests=[self.request_completed],
            time=0,
            run_id="test_run"
        )
        self.assertEqual(matched, [])

    def test_equal_distances(self):
        # Both drivers same distance to request
        driver1 = Driver(1, Point(0, 0), 1.0, DriverStatus.IDLE, None,
                         b, [], "test_run")
        driver2 = Driver(2, Point(0, 0), 1.0, DriverStatus.IDLE, None,
                         b, [], "test_run")
        request = Request(1, Point(5, 0), Point(6, 0), 0, RequestStatus.WAITING,
                          None, 0, "test_run")

        matched = self.policy.assign(
            drivers=[driver1, driver2],
            requests=[request],
            time=0,
            run_id="test_run"
        )

        self.assertEqual(len(matched), 1)
        self.assertIn(matched[0][0].id, [driver1.id, driver2.id])
        self.assertEqual(matched[0][1].id, request.id)

    def test_more_requests_than_drivers(self):
        matched = self.policy.assign(
            drivers=[self.driver_idle_1],
            requests=[self.request_waiting_1, self.request_waiting_2],
            time=0,
            run_id="test_run"
        )

        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0][0], self.driver_idle_1)
        self.assertIn(matched[0][1], [self.request_waiting_1, self.request_waiting_2])

    def test_more_drivers_than_requests(self):
        matched = self.policy.assign(
            drivers=[self.driver_idle_1, self.driver_idle_2],
            requests=[self.request_waiting_1],
            time=0,
            run_id="test_run"
        )

        self.assertEqual(len(matched), 1)
        self.assertIn(matched[0][0], [self.driver_idle_1, self.driver_idle_2])
        self.assertEqual(matched[0][1], self.request_waiting_1)


if __name__ == "__main__":
    unittest.main()
