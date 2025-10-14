import numpy as np

from ntsim.MediumScatteringModels.Base.MediumScatteringModelBase import MediumScatteringModelBase
from ntsim.random import rng

class HenyeyGreenstein(MediumScatteringModelBase):
    def __init__(self, name: str):
        super().__init__(name)
        
        self._g = None
    
    @property
    def anisotropy(self):
        if self._g is None:
            raise ValueError("The value of the anisotropy of the medium is not established!")
        return self._g
    
    @anisotropy.setter
    def anisotropy(self, new_g):
        self._g = new_g
        
    def pdf(self,mu):
        g = self.anisotropy
        return 0.5*(1-g**2)*np.power(1+g**2-2*g*mu,-1.5)

    def cdf(self,mu):
        g = self.anisotropy
        g2 = np.power(g,2)
        gmu = g*mu
        f1 = 1/np.sqrt(1+g2-2*gmu)
        f2 = 1/(1+g)
        cdf = 0.5*(1-g2)*(f1-f2)/g # FIXME 1/g to be added!!!!
        return cdf

    def random_mu(self,sample=1):
        g = self.anisotropy
        s = rng.uniform(-1,1,sample) # -1,1 is crucial! (DN)

        if (g != 0.0):
            x = np.power((1-g**2)/(1+g*s),2)
            return 0.5/g*(1+g**2-x)
        else:
            return s
