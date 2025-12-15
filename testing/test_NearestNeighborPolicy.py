import unittest
from unittest.mock import MagicMock

from phase2.Point import Point
from phase2.Driver import Driver, DriverStatus
from phase2.Request import Request, RequestStatus
from phase2.behaviour.EarningsMaxBehaviour import EarningsMaxBehaviour
from phase2.behaviour.GreedyDistanceBehaviour import GreedyDistanceBehaviour
from phase2.dispatch.NearestNeighborPolicy import NearestNeighborPolicy


class TestNearestNeighborPolicy(unittest.TestCase):

    def setUp(self):
        self.policy = NearestNeighborPolicy()

    def test_assign_no_idle_drivers_returns_empty(self):
        # Arrange
        drivers = [Driver(id=1, position=Point(0, 0), speed=1.0,
                          status=DriverStatus.TO_PICKUP, current_request=None, behaviour=GreedyDistanceBehaviour(),
                          history=[], run_id="test_run")]
        requests = [Request(id=1, pickup=Point(1, 1), dropoff=Point(2, 2), creation_time=0,
                            status=RequestStatus.WAITING, assigned_driver=None, wait_time=0, run_id="test_run")]
        time = 0
        run_id = "test_run"

        # Act
        result = self.policy.assign(drivers, requests, time, run_id)

        # Assert
        self.assertEqual(result, [])

    def test_assign_no_waiting_requests_returns_empty(self):
        # Arrange
        drivers = [Driver(id=1, position=Point(0, 0), speed=1.0,
                          status=DriverStatus.IDLE, current_request=None, behaviour=GreedyDistanceBehaviour(),
                          history=[], run_id="test_run")]
        requests = [Request(id=1, pickup=Point(1, 1), dropoff=Point(2, 2), creation_time=0,
                            status=RequestStatus.DELIVERED, assigned_driver=None, wait_time=0, run_id="test_run")]
        time = 0
        run_id = "test_run"

        # Act
        result = self.policy.assign(drivers, requests, time, run_id)

        # Assert
        self.assertEqual(result, [])

    def test_assign_single_driver_single_request(self):
        # Arrange
        driver = Driver(id=1, position=Point(0, 0), speed=1.0,
                        status=DriverStatus.IDLE, current_request=None, behaviour=GreedyDistanceBehaviour(),
                        history=[], run_id="test_run")
        request = Request(id=1, pickup=Point(1, 1), dropoff=Point(2, 2), creation_time=0,
                          status=RequestStatus.WAITING, assigned_driver=None, wait_time=0, run_id="test_run")
        time = 0
        run_id = "test_run"

        # Act
        result = self.policy.assign([driver], [request], time, run_id)

        # Assert
        self.assertEqual(len(result), 1)
        assigned_driver, assigned_request = result[0]
        self.assertEqual(assigned_driver, driver)
        self.assertEqual(assigned_request, request)

    def test_assign_multiple_drivers_multiple_requests(self):
        # Arrange
        driver1 = Driver(id=1, position=Point(0, 0), speed=1.0,
                         status=DriverStatus.IDLE, current_request=None, behaviour=GreedyDistanceBehaviour(),
                         history=[], run_id="test_run")
        driver2 = Driver(id=2, position=Point(10, 10), speed=1.0,
                         status=DriverStatus.IDLE, current_request=None, behaviour=EarningsMaxBehaviour(),
                         history=[], run_id="test_run")
        request1 = Request(id=1, pickup=Point(1, 1), dropoff=Point(2, 2), creation_time=0,
                           status=RequestStatus.WAITING, assigned_driver=None, wait_time=0, run_id="test_run")
        request2 = Request(id=2, pickup=Point(11, 11), dropoff=Point(12, 12), creation_time=0,
                           status=RequestStatus.WAITING, assigned_driver=None, wait_time=0, run_id="test_run")
        time = 0
        run_id = "test_run"

        # Act
        result = self.policy.assign([driver1, driver2], [request1, request2], time, run_id)

        # Assert
        self.assertEqual(len(result), 2)
        self.assertIn((driver1, request1), result)
        self.assertIn((driver2, request2), result)

    def test_assign_already_assigned_requests_skipped(self):
        # Arrange
        driver1 = Driver(id=1, position=Point(0, 0), speed=1.0,
                         status=DriverStatus.IDLE, current_request=None, behaviour=EarningsMaxBehaviour(),
                         history=[], run_id="test_run")
        driver2 = Driver(id=2, position=Point(0, 0), speed=1.0,
                         status=DriverStatus.IDLE, current_request=None, behaviour=GreedyDistanceBehaviour(),
                         history=[], run_id="test_run")
        request1 = Request(id=1, pickup=Point(1, 1), dropoff=Point(2, 2), creation_time=0,
                           status=RequestStatus.WAITING, assigned_driver=None, wait_time=0, run_id="test_run")
        request2 = Request(id=2, pickup=Point(1, 1), dropoff=Point(2, 2), creation_time=0,
                           status=RequestStatus.WAITING, assigned_driver=None, wait_time=0, run_id="test_run")
        time = 0
        run_id = "test_run"

        # Act
        result = self.policy.assign([driver1, driver2], [request1, request2], time, run_id)

        # Assert
        self.assertEqual(len(result), 2)
        # Ensure each request is assigned to only one driver
        assigned_requests = [r.id for d, r in result]
        self.assertEqual(len(set(assigned_requests)), 2)


if __name__ == "__main__":
    unittest.main()
