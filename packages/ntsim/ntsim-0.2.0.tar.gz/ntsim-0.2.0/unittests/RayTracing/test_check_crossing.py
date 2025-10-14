import unittest
from ntsim.Propagators.RayTracers.rt_utils import check_crossing

class TestCheckCrossing(unittest.TestCase):

    def setUp(self):
        self.bb = (0, 10, 0, 10, 0, 10)

    def test_both_points_inside(self):
        point1 = (5, 5, 5)
        point2 = (6, 6, 6)
        self.assertTrue(check_crossing(point1, point2, self.bb))

    def test_one_point_inside(self):
        point1 = (5, 5, 5)
        point2 = (15, 15, 15)
        self.assertTrue(check_crossing(point1, point2, self.bb))

    def test_crossing_one_face(self):
        point1 = (-5, 5, 5)
        point2 = (5, 5, 5)
        self.assertTrue(check_crossing(point1, point2, self.bb))

    def test_crossing_two_faces(self):
        point1 = (-5, -5, 5)
        point2 = (5, 5, 5)
        self.assertTrue(check_crossing(point1, point2, self.bb))

    def test_no_crossing(self):
        point1 = (-5, -5, -5)
        point2 = (-6, -6, -6)
        self.assertFalse(check_crossing(point1, point2, self.bb))

    def test_touching_edge(self):
        point1 = (10, 5, 5)
        point2 = (15, 5, 5)
        self.assertTrue(check_crossing(point1, point2, self.bb))

if __name__ == '__main__':
    unittest.main()
