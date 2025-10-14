import unittest
from ntsim.Detector.telescopes.example1.Example1SensitiveDetector import Example1SensitiveDetector
import numpy as np

class TestExample1SensitiveDetector(unittest.TestCase):
    def setUp(self):
        self.detector = Example1SensitiveDetector(uid=0, position=np.array([0, 0, 0]), radius=1.0, photocathode_unit_vector=np.array([0, 0, -1]))

    def test_apply_effects(self):
        intersection = np.array([True, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, -1.0])
        total_effect, effects_array = self.detector.apply_effects(400, intersection)
        self.assertAlmostEqual(total_effect, 0.2, places=7)
        self.assertEqual(effects_array[0][0], 'Example1_PDE')
        self.assertAlmostEqual(effects_array[0][1], 0.2, places=7)

if __name__ == '__main__':
    unittest.main()
