import unittest
from phase2.Point import Point


class TestPoint(unittest.TestCase):

    def test_init_valid(self):
        p = Point(3, 4)
        self.assertEqual((p.x, p.y), (3.0, 4.0))

    def test_init_invalid_x(self):
        with self.assertRaises(TypeError):
            Point("a", 5)

    def test_init_invalid_y(self):
        with self.assertRaises(TypeError):
            Point(1, None)

    def test_str(self):
        p = Point(1, 2)
        self.assertEqual(str(p), "Point(x=1.0, y=2.0)")

    def test_eq_true(self):
        self.assertTrue(Point(1, 2) == Point(1, 2))

    def test_eq_false(self):
        self.assertFalse(Point(1, 2) == Point(2, 1))

    def test_eq_not_implemented(self):
        self.assertEqual(Point(1, 1).__eq__("not a point"), NotImplemented)

    def test_add(self):
        p = Point(1, 2) + Point(3, 4)
        self.assertEqual(p, Point(4, 6))

    def test_add_not_implemented(self):
        self.assertEqual(Point(1, 1).__add__("x"), NotImplemented)

    def test_sub(self):
        p = Point(5, 7) - Point(2, 3)
        self.assertEqual(p, Point(3, 4))

    def test_mul(self):
        p = Point(2, 3) * 4
        self.assertEqual(p, Point(8, 12))

    def test_mul_not_implemented(self):
        self.assertEqual(Point(1, 1).__mul__("a"), NotImplemented)

    def test_rmul(self):
        p = 3 * Point(2, 5)
        self.assertEqual(p, Point(6, 15))

    def test_iadd(self):
        p = Point(1, 1)
        p += Point(2, 3)
        self.assertEqual(p, Point(3, 4))

    def test_isub(self):
        p = Point(5, 5)
        p -= Point(1, 2)
        self.assertEqual(p, Point(4, 3))

    def test_distance(self):
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        self.assertEqual(p1.distance_to(p2), 5.0)

    def test_distance_invalid(self):
        with self.assertRaises(TypeError):
            Point(0, 0).distance_to("not a point")


if __name__ == "__main__":
    unittest.main()