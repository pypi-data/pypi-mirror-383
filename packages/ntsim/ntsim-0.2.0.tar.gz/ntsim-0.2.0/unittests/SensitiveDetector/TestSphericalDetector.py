import unittest
from ntsim.Detector.SphericalSensitiveDetector import SphericalSensitiveDetector
import numpy as np
import configargparse
from ntsim.utils.gen_utils import segment_generator

class TestSphericalDetector(unittest.TestCase):
    def setUp(self):
        # Create a SphericalSensitiveDetector for use in the tests
        self.detector = SphericalSensitiveDetector(position=np.array(opts.center), radius=opts.radius)

    def test_line_segment_intersection(self):
        # Test a line segment that should intersect the detector
        self.check_intersection(intersect=True, expected=True)

        # Test a line segment that should not intersect the detector
        self.check_intersection(intersect=False, expected=False)

    def check_intersection(self, intersect, expected):
        segments = segment_generator(center=self.detector.position, radius=self.detector.radius, num_segments=opts.num_segments, intersect=intersect)
        for i in range(opts.num_segments):
            a = segments[i, 0, :]
            b = segments[i, 1, :]
            intersection = self.detector.line_segment_intersection(a, b)
            self.assertEqual(intersection[0], expected)

if __name__ == '__main__':
    # Parse command line arguments
    parser = configargparse.get_argument_parser()
    parser.add('--center', type=float, nargs=3, default=[0, 0, 0], help='Center of the sphere')
    parser.add('--radius', type=float, default=2, help='Radius of the sphere')
    parser.add('--num_segments', type=int, default=3, help='number of segments to generate')

    opts = parser.parse_args()

    unittest.main(argv=['first-arg-is-ignored'], exit=False)
