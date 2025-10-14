from ntsim.MediumProperties.Base.BaseMediumProperties import BaseMediumProperties
import numpy as np
from bgvd_model.BaikalWater import BaikalWater
from argparse import Namespace

class BaikalWaterProperties(BaseMediumProperties):
    arg_dict = {
        'anisotropy': {'type': float, 'default': 0.9, 'help': 'Anisotropy factor'},
        'waves_range': {'type': float, 'nargs': 2, 'default': [350., 610.], 'help': 'Wavelength range in nm'}
    }

    def init(self):
        BaikalWaterProps = BaikalWater()

        self.wavelength_nm           = BaikalWaterProps.wavelength
        self.group_refraction_index  = BaikalWaterProps.group_refraction_index
        self.absorption_inv_length_m = BaikalWaterProps.absorption_inv_length
        self.scattering_inv_length_m = BaikalWaterProps.scattering_inv_length

        self.waves_range             = [self.wavelength_nm[0], self.wavelength_nm[-1]]
