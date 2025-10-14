import numpy as np
from ntsim.IO.gPhotons import gPhotons
from ntsim.PrimaryGenerators.Base.PrimaryGeneratorBase import PrimaryGeneratorBase
from ntsim.random import rng

class IsotropicSource(PrimaryGeneratorBase):
    arg_dict={'position_m': {'type': float , 'nargs': 3 , 'default': [0.,0.,0.] , 'help': 'position of point-like source'},
              'n_photons': {'type': float ,  'default': 100000 , 'help': 'amount of photons to generate'},
              'n_bunches': {'type': int ,  'default': 1 , 'help': 'amount of photons'},
              'photons_weight': {'type': int , 'default': 10000 , 'help': 'amount of bunches'},
              'wavelength_nm': {'type': float , 'default': 400 , 'help': 'photons wavelength'}}

    def __post_configure__(self):
        self.photons_in_bunch = int(self.n_photons / self.n_bunches)
        self.photons = gPhotons(size = self.photons_in_bunch,
                                pos_m=self.position_m,
                                t_ns=0,
                                direction=[0,0,0],# will be defined later
                                wl_nm=self.wavelength_nm,
                                weight=self.photons_weight,
                               )
    def make_event(self, event):
        event.photons["IsotropicSource"] = self.make_photons_generator()

    def make_direction(self):
        phi = rng.uniform(0 , 2*np.pi ,self.photons_in_bunch)
        theta = rng.uniform(0 , np.pi , self.photons_in_bunch)
        direction = np.stack(
            [np.cos(phi) * np.sin(theta),
             np.sin(phi) * np.sin(theta),
             np.cos(theta)],
            axis=-1
        )
        return direction

    def make_photons(self):
        self.photons.direction = self.make_direction()
        return self.photons

    def make_photons_generator(self):
        for i in range(self.n_bunches):
            yield self.make_photons()
            
