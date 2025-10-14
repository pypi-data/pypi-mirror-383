import numpy as np

from ntsim.MediumScatteringModels.Base.MediumScatteringModelBase import MediumScatteringModelBase
from ntsim.random import rng

class Rayleigh(MediumScatteringModelBase):
    def pdf(self, mu):
        return 3./8.*(1 + mu**2)

    def cdf(self,mu):
        return 0.5+1/8*mu*(3+mu*mu)

    def random_mu(self,sample):
        r = rng.uniform(0,1,sample)
        z = 2*(2*r-1)
        dz = np.sqrt(np.power(z,2)+1)
        z1 = z+dz
        z2 = z-dz
        B_sign = np.sign(z2)
        A = (z+dz)**(float(1)/3)
        B = np.abs(z-dz)**(float(1)/3)
        mu = A+B*B_sign
        return mu

    def random_mu_numeric(self, sample=1):
        # F(mu) = (mu^3 + 3*mu + 4) / 8
        CDF = 1./8.*np.poly1d([1.,0.,3.,4.])
        costh = np.linspace(-1,1,1000)
        import matplotlib.pyplot as plt
        if sample != 1:
            res = []
            for s in rng.uniform(0,1,sample):
                poly_roots = (CDF-s).roots
                real_root = poly_roots[poly_roots.imag==0].real[0]
                res.append(real_root)
            return np.array(res)
        else:
            s = rng.uniform(0,1)
            poly_roots = (CDF-s).roots
            real_root = poly_roots[poly_roots.imag==0].real[0]
            return real_root
