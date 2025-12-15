import unittest
from unittest.mock import MagicMock
from phase2.Offer import Offer
from phase2.Request import Request
from phase2.Driver import Driver


class TestOffer(unittest.TestCase):
    def setUp(self):
        self.mock_driver = MagicMock(spec=Driver)
        self.mock_request = MagicMock(spec=Request)

    def test_valid_offer_creation(self):
        offer = Offer(
            driver=self.mock_driver,
            request=self.mock_request,
            estimated_total_distance=10.5,
            estimated_distance_to_pickup=3,
            estimated_reward=25.0
        )
        self.assertEqual(offer.driver, self.mock_driver)
        self.assertEqual(offer.request, self.mock_request)
        self.assertEqual(offer.estimated_total_distance, 10.5)
        self.assertEqual(offer.estimated_distance_to_pickup, 3)
        self.assertEqual(offer.estimated_reward, 25.0)

    def test_invalid_driver_type_raises(self):
        with self.assertRaises(TypeError) as context:
            Offer(
                driver="not_a_driver",
                request=self.mock_request,
                estimated_total_distance=5,
                estimated_distance_to_pickup=3,
                estimated_reward=10
            )
        self.assertEqual(str(context.exception), "driver must be a Driver")

    def test_invalid_request_type_raises(self):
        with self.assertRaises(TypeError) as context:
            Offer(
                driver=self.mock_driver,
                request="not_a_request",
                estimated_total_distance=10,
                estimated_distance_to_pickup=5,
                estimated_reward=10
            )
        self.assertEqual(str(context.exception), "request must be a Request")

    def test_invalid_estimated_travel_time_type_raises(self):
        with self.assertRaises(TypeError) as context:
            Offer(
                driver=self.mock_driver,
                request=self.mock_request,
                estimated_total_distance="fast",
                estimated_distance_to_pickup=5,
                estimated_reward=10
            )
        self.assertEqual(str(context.exception), "estimated_total_distance must be a number")

    def test_invalid_estimated_reward_type_raises(self):
        with self.assertRaises(TypeError) as context:
            Offer(
                driver=self.mock_driver,
                request=self.mock_request,
                estimated_total_distance=5,
                estimated_distance_to_pickup=3,
                estimated_reward="a lot"
            )
        self.assertEqual(str(context.exception), "estimated_reward must be a number")

if __name__ == "__main__":
    unittest.main()
