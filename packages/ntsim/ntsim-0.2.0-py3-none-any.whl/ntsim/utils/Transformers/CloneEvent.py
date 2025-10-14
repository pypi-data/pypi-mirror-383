import numpy as np
from ntsim.utils.Transformers.Base.TransformerBase import TransformerBase

class cloneEvent(TransformerBase):
    # transform photons: shift and rotate
    def __init__(self):
        self.name = 'cloneEvent'
        import logging
        self.log = logging.getLogger(self.name)
        self.log.info('initialized')

    def configure(self, opts):
        self.n_events            = opts.cloner_n
        self.cylinder_center     = opts.cloner_cylinder_center_m
        self.cylinder_dimensions = opts.cloner_cylinder_dimensions_m
        self.accumulate_hits     = opts.cloner_accumulate_hits

    def transform(self,r,id):
        r = r + self.random_shift[id,:]
        return r

    def generate_random_shifts(self) -> None:
        R = self.cylinder_dimensions[0]
        H = self.cylinder_dimensions[1]
        r = np.sqrt(np.random.default_rng().uniform(0, R**2 , self.n_events))
        phi = np.random.default_rng().uniform(0 , 2*np.pi , self.n_events)
        x = np.multiply(r, np.cos(phi))
        y = np.multiply(r, np.sin(phi))
        z = np.random.default_rng().uniform(0, H, self.n_events)-0.5*H
        self.random_shift = np.array([x,y,z]).T
