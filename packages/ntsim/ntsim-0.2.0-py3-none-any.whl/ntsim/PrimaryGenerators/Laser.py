import numpy as np

from ntsim.PrimaryGenerators.Base.PrimaryGeneratorBase import PrimaryGeneratorBase
from ntsim.PrimaryGenerators.Diffuser import DiffuserExponential,DiffuserCone
from ntsim.utils.gen_utils import generate_cherenkov_spectrum
from ntsim.utils.report_timing import report_timing
from ntsim.IO.gPhotons import gPhotons

class Laser(PrimaryGeneratorBase):
    arg_dict = {
        'n_photons': {'type': int, 'default': 10000, 'help': 'number of photons to generate'},
        'photons_bunches': {'type': int, 'default': 1, 'help': 'number of bunches'},
        'photons_weight': {'type': float, 'default': 1000., 'help': 'statistical weight of a photon'},
        'position_m': {'type': float, 'nargs': 3, 'default': [0.,0.,0.], 'help': 'three vector for laser position'},
        'direction': {'type': float, 'nargs': 3, 'default': [0.,0.,1.], 'help': 'unit three vector for photons direction'},
        'wavelength': {'type': float, 'default': 350., 'help': ''},
        'diffuser': {'type': str, 'nargs': 2, 'default': ('none',0), 'help': 'laser diffuser mode: (exp,sigma) or (cone, angle)'}
    }
        
    def set_diffuser(self):
        self.logger.info(f'Selected diffuser: "{self.diffuser[0]}" with parameter: {self.diffuser[1]}')
        if self.diffuser[0] == 'exp':
            self.laser_diffuser = DiffuserExponential(float(self.diffuser[1]))
        elif self.diffuser[0] == 'cone':
            self.laser_diffuser = DiffuserCone(float(self.diffuser[1]))
        elif self.diffuser[0] == 'none':
            self.laser_diffuser = None
        else:
            raise ValueError('Invalid diffuser type')

    def __post_configure__(self):
        self.set_diffuser()
        n_photons_bunch = int(self.n_photons/self.photons_bunches)
        self.photons = gPhotons(size=n_photons_bunch,
                                pos_m=self.position_m,
                                t_ns=0,
                                wl_nm=self.wavelength,
                                direction=self.direction,
                                weight=self.photons_weight,
                               )
    
    def get_direction(self):
        dir0 = np.array(self.direction,dtype=np.float64)
        if not self.laser_diffuser:
            self.dir = np.tile(dir0,(self.n_photons_bunch,1))
        else:
            dir = np.tile(dir0,(self.n_photons_bunch,1))
            dir = self.laser_diffuser.random_direction(dir)
            dir = np.reshape(dir,(self.n_photons_bunch,3))
            self.dir = dir

    def make_photons(self):
        photons = self.photons
        if self.laser_diffuser is not None:
            #reset direction to the default value
            photons.direction = self.direction
            #set new random directions
            photons.direction = self.laser_diffuser.random_direction(photons.direction).reshape(-1,3)
        return photons

    @report_timing
    def make_event(self, event):
        event.photons['Laser'] = self.make_photons_generator()

    def make_photons_generator(self):
        for i in range(self.photons_bunches):
            yield self.make_photons()
