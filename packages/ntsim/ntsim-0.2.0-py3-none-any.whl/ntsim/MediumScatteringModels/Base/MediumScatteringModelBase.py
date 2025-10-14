import abc
import numpy as np

import ntsim.utils.gen_utils as gen_utils
from ntsim.Base.BaseConfig import BaseConfig
from ntsim.CherenkovGenerators.cher_utils import unit_vector
from numba import njit, types


@njit(types.float64[:,:](types.float64[:,:],types.float64[:]),parallel=False,fastmath=True,cache=True)
def random_direction(v,random_mu):
    
    output_data = np.empty(shape=(np.shape(v)))
    # v = unit vector axis
    # returns random unit vector v1 with v*v1=t, where t is distributed according to random_mu distribution
    phi_r = 2*np.pi*np.random.uniform(0., 1., size=v.shape[0])
    cosphi_r = np.cos(phi_r)
    sinphi_r = np.sin(phi_r)
    costheta_r = random_mu
    sintheta_r = np.sqrt(1-costheta_r**2)
    
    v = unit_vector(v)
    costheta = v[:,2]
    sintheta = np.sqrt(1-costheta**2)
    phi = np.arctan2(v[:,1],v[:,0])
    cosphi = np.cos(phi)
    sinphi = np.sin(phi)
    output_data[:,0] = cosphi*(costheta*sintheta_r*cosphi_r+sintheta*costheta_r)-sinphi*sintheta_r*sinphi_r
    output_data[:,1] = sinphi*(costheta*sintheta_r*cosphi_r+sintheta*costheta_r)+cosphi*sintheta_r*sinphi_r
    output_data[:,2] = -sintheta*sintheta_r*cosphi_r+costheta*costheta_r
    
    return output_data

class MediumScatteringModelBase(BaseConfig):
    def __init__(self, name: str):
        self._name = name
        self.logger.info("Initialized Medium Scattering Model")
    
    @abc.abstractmethod
    def pdf(self,mu):
        """
        pdf
        """
    
    @abc.abstractmethod
    def random_mu(self,sample=1):
        """
        random mu
        """
    
    @abc.abstractmethod
    def cdf(self,mu):
        """
        cdf
        """
    
    def cdf_numeric(self,mu,n):
        x = np.linspace(-1,mu,n)
        y = self.pdf(x)
        step = (mu+1)/n
        return np.sum(y)*step
    
    def random_direction(self,v):
        costheta_r = self.random_mu(sample=v.shape[0])
        data_output = random_direction(v,costheta_r)
        return data_output

    def plot_random_direction(self):
        import matplotlib as mpl
        from mpl_toolkits.mplot3d import Axes3D
        import matplotlib.pyplot as plt
        pos = [221, 222, 223, 224]
        v = np.array([[0,0,1], [0,1,1], [1,1,1], [1,0,1]])
        sample = 10000
        fig = plt.figure(figsize=plt.figaspect(0.5))
        
        plt.subplots_adjust(hspace=0.4)
        fig.suptitle('Validate rotations', fontsize=14)
        for i in range(4):
            #plt.subplot(pos[i],projection='3d')
            axis = v[i]
            x = np.zeros(sample,dtype=float)
            y = np.zeros(sample,dtype=float)
            z = np.zeros(sample,dtype=float)
            for s in range(sample):
                v1 = self.random_direction(axis.reshape(1,3))
                x[s] = v1[:,0]
                y[s] = v1[:,1]
                z[s] = v1[:,2]
            ax = fig.add_subplot(2, 2, i+1, projection='3d')
            ax.scatter(x,y,z, s=0.05,marker='.')
        plt.show()