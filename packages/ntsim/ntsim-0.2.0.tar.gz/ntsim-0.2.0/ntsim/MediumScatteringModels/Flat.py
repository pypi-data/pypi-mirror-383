import numpy as np

from ntsim.MediumScatteringModels.Base.MediumScatteringModelBase import MediumScatteringModelBase
from ntsim.random import rng

class FlatScatteringModel(MediumScatteringModelBase):
    def pdf(self, mu):
        if type(mu) == float:
            return 0.5
        else:
            return np.ones(mu.shape)/2.

    def cdf(self, mu):
        return 0.5*(1.+mu)

    def random_mu(self, sample=1):
        return rng.uniform(-1,1,sample)
