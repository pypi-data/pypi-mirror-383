import unittest
from argparse import Namespace
from ntsim.Detector.telescopes.example1.Example1MediumProperties import Example1MediumProperties

class TestExample1MediumProperties(unittest.TestCase):
    def setUp(self):
        self.medium_properties = Example1MediumProperties()

    def test_configure(self):
        opts = Namespace()
        opts.telescope = Namespace()
        opts.telescope.Example1 = Namespace()
        opts.telescope.Example1.waves = (350, 600)
        opts.telescope.Example1.scattering_inv_length_m = (0.001, 0.002)
        opts.telescope.Example1.absorption_inv_length_m = (0.001, 0.002)
        opts.telescope.Example1.group_refraction_index = (1.33, 1.34)

        self.assertTrue(self.medium_properties.configure(opts))

        self.assertEqual(len(self.medium_properties.get_wavelength()), 100)
        self.assertEqual(len(self.medium_properties.get_scattering_inv_length()), 100)
        self.assertEqual(len(self.medium_properties.get_absorption_inv_length()), 100)
        self.assertEqual(len(self.medium_properties.get_group_refraction_index()), 100)

        self.assertEqual(self.medium_properties.get_wavelength()[0], 350)
        self.assertEqual(self.medium_properties.get_wavelength()[-1], 600)
        self.assertEqual(self.medium_properties.get_scattering_inv_length()[0], 0.001)
        self.assertEqual(self.medium_properties.get_scattering_inv_length()[-1], 0.002)
        self.assertEqual(self.medium_properties.get_absorption_inv_length()[0], 0.001)
        self.assertEqual(self.medium_properties.get_absorption_inv_length()[-1], 0.002)
        self.assertEqual(self.medium_properties.get_group_refraction_index()[0], 1.33)
        self.assertEqual(self.medium_properties.get_group_refraction_index()[-1], 1.34)

if __name__ == '__main__':
    unittest.main()
