import numpy as np

from ntsim.MediumScatteringModels.Base.MediumScatteringModelBase import MediumScatteringModelBase
from ntsim.MediumScatteringModels.HenyeyGreenstein import HenyeyGreenstein
from ntsim.MediumScatteringModels.Rayleigh import Rayleigh
from ntsim.random import rng

class HGplusRayleigh(MediumScatteringModelBase):
    def __init__(self, name, waves, mua, mus, refractive_index, g, rl_fraction=0.01):
        super(HGplusRayleigh, self).__init__(name, waves, mua, mus, refractive_index, g)
        self.hg_fraction = 1. - rl_fraction
        self.rl_fraction = rl_fraction
        self.hg_model = HenyeyGreenstein(name, waves, mua, mus, refractive_index, g)
        self.rl_model = Rayleigh(name, waves, mua, mus, refractive_index, g)

    def pdf(self, mu):
        self.hg_model.g = self.g
        return self.hg_fraction*self.hg_model.pdf(mu) + self.rl_fraction*self.rl_model.pdf(mu)

    def cdf(self, mu):
        self.hg_model.g = self.g
        return self.hg_fraction*self.hg_model.cdf(mu) + self.rl_fraction*self.rl_model.cdf(mu)

    def random_mu(self, sample=1):
        if sample != 1:
            rnd_nb = rng.uniform(0,1,sample)
            s_hg = self.hg_model.random_mu(len(rnd_nb[rnd_nb <  self.hg_fraction]))
            s_rl = self.rl_model.random_mu(len(rnd_nb[rnd_nb >= self.hg_fraction]))
            s_tot = np.concatenate((s_hg,s_rl))
            rng.shuffle(s_tot)
            return s_tot
        else:
            if rng.uniform(0,1) < self.hg_fraction:
                return self.hg_model.random_mu()
            else:
                return self.rl_model.random_mu()
