import unittest
from unittest.mock import patch, MagicMock
from phase2.MutationRule import MutationRule
from phase2.metrics.EventManager import EventManager
from phase2.metrics.Event import Event, EventType
from phase2.Request import RequestStatus
from phase2.behaviour import EarningsMaxBehaviour, GreedyDistanceBehaviour, LazyBehaviour
from phase2.MutationRule import MutationRule
from phase2.Request import Request



"""
- Bestem input
- Regn det forventede output ud
- sammenlign det faktiske output med det forventede output.

Skal gøres for:
[x] instantiation, herunder typechecking
[x] str
[x] repr
- maybe_mutate
- mutate_driver
"""




class TestMutationRule(unittest.TestCase):

    def test_valid_initialization(self):
        rule = MutationRule(n_trips=5, threshold=0.75, run_id="test_run")

        self.assertEqual(rule.n_trips, 5)
        self.assertEqual(rule.threshold, 0.75)
        self.assertEqual(rule.run_id, "test_run")

    def test_invalid_n_trips_type(self):
        with self.assertRaises(TypeError):
            MutationRule(n_trips=5.5, threshold=0.5, run_id="test_run")

        with self.assertRaises(TypeError):
            MutationRule(n_trips="5", threshold=0.5, run_id="test_run")

    def test_invalid_threshold_type(self):
        with self.assertRaises(TypeError):
            MutationRule(n_trips=5, threshold=1, run_id="test_run")

        with self.assertRaises(TypeError):
            MutationRule(n_trips=5, threshold="0.5", run_id="test_run")

    def test_invalid_run_id_type(self):
        with self.assertRaises(TypeError):
            MutationRule(n_trips=5, threshold=0.5, run_id=123)

    def test_str_representation(self):
        rule = MutationRule(n_trips=3, threshold=0.2, run_id="run")

        self.assertEqual(
            str(rule),
            "MutationRule(n_trips=3, threshold=0.2)"
        )

    def test_repr_matches_str(self):
        rule = MutationRule(n_trips=10, threshold=0.9, run_id="run")

        self.assertEqual(repr(rule), str(rule))


class FakeTrip:
    def __init__(self, status):
        self.status = status


class FakeDriver:
    def __init__(self, driver_id, behaviour, history):
        self.id = driver_id
        self.behaviour = behaviour
        self.history = history


class TestMutationRuleMaybeMutate(unittest.TestCase):

    def setUp(self):
        self.rule = MutationRule(
            n_trips=4,
            threshold=0.5, # if half of trips are expired, mutate
            run_id="test_run"
        )

    @patch("phase2.MutationRule.EventManager")
    def test_does_not_mutate_when_not_enough_trips(self, mock_event_manager):
        driver = FakeDriver(
            driver_id=1,
            behaviour=MagicMock(),
            history=[FakeTrip(RequestStatus.EXPIRED)]
        )

        self.rule.maybe_mutate(driver, time=10)

        mock_event_manager.assert_not_called()

    @patch("phase2.MutationRule.EventManager")
    def test_does_not_mutate_when_expired_ratio_below_threshold(self, mock_event_manager):
        history = [
            FakeTrip(RequestStatus.EXPIRED),
            FakeTrip(RequestStatus.DELIVERED),
            FakeTrip(RequestStatus.DELIVERED),
            FakeTrip(RequestStatus.DELIVERED),
        ]

        driver = FakeDriver(
            driver_id=1,
            behaviour=MagicMock(),
            history=history
        )

        self.rule.maybe_mutate(driver, time=10)

        mock_event_manager.assert_not_called()

    @patch("phase2.MutationRule.choice")
    @patch("phase2.MutationRule.EventManager")
    def test_mutates_driver_when_expired_ratio_meets_threshold(
        self, mock_event_manager, mock_choice
    ):
        history = [
            FakeTrip(RequestStatus.EXPIRED),
            FakeTrip(RequestStatus.EXPIRED),
            FakeTrip(RequestStatus.DELIVERED),
            FakeTrip(RequestStatus.DELIVERED),
        ]
        old_behaviour = MagicMock()
        new_behaviour_class = MagicMock()

        mock_choice.return_value = new_behaviour_class

        event_manager_instance = MagicMock()
        mock_event_manager.return_value = event_manager_instance

        driver = FakeDriver(
            driver_id=7,
            behaviour=old_behaviour,
            history=history
        )
        self.rule.maybe_mutate(driver, time=20)

        # Behaviour updated
        self.assertEqual(driver.behaviour, new_behaviour_class)

        # EventManager created with correct run_id
        mock_event_manager.assert_called_once_with("test_run")

        # Event logged
        event_manager_instance.add_event.assert_called_once()

    @patch("phase2.MutationRule.choice")
    @patch("phase2.MutationRule.EventManager")
    def test_mutation_excludes_current_behaviour(
        self, mock_event_manager, mock_choice
    ):

        history = [
            FakeTrip(RequestStatus.EXPIRED),
            FakeTrip(RequestStatus.EXPIRED),
            FakeTrip(RequestStatus.EXPIRED),
            FakeTrip(RequestStatus.EXPIRED),
        ]

        driver = FakeDriver(
            driver_id=7,
            behaviour=EarningsMaxBehaviour.EarningsMaxBehaviour(),
            history=history
        )

        mock_choice.return_value = MagicMock()

        self.rule.maybe_mutate(driver, time=5)

        mock_choice.assert_called_once()
        chosen_candidates = mock_choice.call_args[0][0]

        self.assertEqual(
            set(chosen_candidates),
            {GreedyDistanceBehaviour.GreedyDistanceBehaviour, LazyBehaviour.LazyBehaviour}
        )


if __name__ == "__main__":
    unittest.main()