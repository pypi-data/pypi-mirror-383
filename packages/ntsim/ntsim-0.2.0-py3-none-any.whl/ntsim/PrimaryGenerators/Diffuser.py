from ntsim.MediumScatteringModels.Base.MediumScatteringModelBase import MediumScatteringModelBase
from ntsim.random import rng
import numpy as np

import logging
log = logging.getLogger('Diffuser')

class DiffuserExponential(MediumScatteringModelBase):
    def __init__(self,sigma=1):
        print(sigma)
        self.sigma = sigma
        self.module_type = 'generator'
        log.info("initialized")

    def diff(self,mu):
        return np.exp(mu/self.sigma) - np.exp(-1/self.sigma)

    def pdf(self,mu):
        return np.exp(mu/self.sigma)/(self.diff(1.)*self.sigma)

    def random_mu(self,sample=1):
        p = rng.uniform(0.,1.,sample)
        return self.sigma*np.log(np.exp(-1/self.sigma) + p*(self.diff(1.)))

    def cdf(self,mu):
        return self.diff(mu)/self.diff(1.)

class DiffuserCone(MediumScatteringModelBase):
    def __init__(self,cone_angle=30.):
        self.cone_angle = cone_angle


    def pdf(self,mu):
        return 0.

    def random_mu(self,sample=1):
        return np.cos(np.deg2rad(self.cone_angle))

    def cdf(self,mu):
        return 0.
