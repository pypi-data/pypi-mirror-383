import unittest
from ntsim.Propagators.RayTracers.rt_utils import check_inside

class TestCheckInside(unittest.TestCase):

    def setUp(self):
        # Define a bounding box for testing
        self.bb = (0, 10, 0, 10, 0, 10)  # x_min, x_max, y_min, y_max, z_min, z_max

    def test_point_inside(self):
        point = (5, 5, 5)
        self.assertTrue(check_inside(point, self.bb))

    def test_point_on_edge(self):
        point = (10, 5, 5)
        self.assertTrue(check_inside(point, self.bb))

    def test_point_outside(self):
        point = (11, 5, 5)
        self.assertFalse(check_inside(point, self.bb))

    def test_point_on_corner(self):
        point = (0, 0, 0)
        self.assertTrue(check_inside(point, self.bb))

    def test_point_below(self):
        point = (5, 5, -1)
        self.assertFalse(check_inside(point, self.bb))

    def test_point_above(self):
        point = (5, 5, 11)
        self.assertFalse(check_inside(point, self.bb))

    def test_point_left(self):
        point = (-1, 5, 5)
        self.assertFalse(check_inside(point, self.bb))

    def test_point_right(self):
        point = (11, 5, 5)
        self.assertFalse(check_inside(point, self.bb))

    def test_point_front(self):
        point = (5, -1, 5)
        self.assertFalse(check_inside(point, self.bb))

    def test_point_back(self):
        point = (5, 11, 5)
        self.assertFalse(check_inside(point, self.bb))

if __name__ == '__main__':
    unittest.main()
