import unittest
from abc import ABCMeta

from phase2.behaviour.DriverBehaviour import DriverBehaviour


class DummyDriver:
    pass


class DummyOffer:
    pass


class ConcreteDriverBehaviour(DriverBehaviour):
    def decide(self, driver, offer, time, run_id):
        return True


class TestDriverBehaviour(unittest.TestCase):

    def test_is_abstract_base_class(self):
        self.assertIsInstance(DriverBehaviour, ABCMeta)

    def test_cannot_instantiate_abstract_class(self):
        with self.assertRaises(TypeError):
            DriverBehaviour()

    def test_subclass_must_implement_decide(self):
        class IncompleteBehaviour(DriverBehaviour):
            pass

        with self.assertRaises(TypeError):
            IncompleteBehaviour()

    def test_concrete_subclass_can_be_instantiated(self):
        behaviour = ConcreteDriverBehaviour()
        self.assertIsInstance(behaviour, DriverBehaviour)

    def test_decide_method_is_callable(self):
        behaviour = ConcreteDriverBehaviour()
        result = behaviour.decide(
            driver=DummyDriver(),
            offer=DummyOffer(),
            time=10,
            run_id="test_run"
        )

        self.assertTrue(result)

    def test_str_returns_class_name(self):
        behaviour = ConcreteDriverBehaviour()
        self.assertEqual(str(behaviour), "ConcreteDriverBehaviour")

    def test_repr_matches_str(self):
        behaviour = ConcreteDriverBehaviour()
        self.assertEqual(repr(behaviour), str(behaviour))


if __name__ == "__main__":
    unittest.main()
