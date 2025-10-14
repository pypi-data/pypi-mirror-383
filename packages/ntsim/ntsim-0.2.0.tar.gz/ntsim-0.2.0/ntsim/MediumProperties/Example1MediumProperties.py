from ntsim.MediumProperties.Base.BaseMediumProperties import BaseMediumProperties
import numpy as np
from argparse import Namespace

class Example1MediumProperties(BaseMediumProperties):
    arg_dict = {
    'waves_range': {'type': float, 'nargs': 2, 'default': [350, 600], 'help': 'Wavelength range in nm'},
    'scattering_inv_length_m_range': {'type': float, 'nargs': 2, 'default': [0.1, 1.0], 'help': 'Inverse scattering length range in meters'},
    'absorption_inv_length_m_range': {'type': float, 'nargs': 2, 'default': [0.1, 1.0], 'help': 'Inverse absorption length range in meters'},
    'group_refraction_index_range': {'type': float, 'nargs': 2, 'default': [1.0, 1.5], 'help': 'Group refraction index range'},
    'anisotropy': {'type': float, 'default': 0.9, 'help': 'Anisotropy factor'}
    }
    
    def init(self):
        # Set wavelength range
        self.wavelength_nm = np.linspace(self.waves_range[0], self.waves_range[1], num=100)
        # Set scattering_inv_length_m
        self.scattering_inv_length_m = np.linspace(self.scattering_inv_length_m_range[0], self.scattering_inv_length_m_range[1], num=100)
        # Set absorption_inv_length_m
        self.absorption_inv_length_m = np.linspace(self.absorption_inv_length_m_range[0], self.absorption_inv_length_m_range[1], num=100)
        # Set group_refraction_index
        self.group_refraction_index = np.linspace(self.group_refraction_index_range[0], self.group_refraction_index_range[1], num=100)