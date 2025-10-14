import abc
from argparse import Namespace
import numpy as np
import ntsim.utils.systemofunits as units
from ntsim.Base.BaseConfig import BaseConfig

from numba import njit, types

@njit(types.containers.Tuple([types.float64[:],types.float64[:],types.float64[:]])(types.float64[:],types.float64[:],types.float64[:],types.float64[:],types.float64[:]),cache=True)
def interpolate(waves,wavelength_nm,scattering_inv_length_m,absorption_inv_length_m,group_refraction_index):
    mus = np.interp(waves,wavelength_nm,scattering_inv_length_m)
    mua = np.interp(waves,wavelength_nm,absorption_inv_length_m)
    n   = np.interp(waves,wavelength_nm,group_refraction_index)

    return mua,mus,n

@njit(types.containers.Tuple([types.float64[:],types.float64[:],types.float64[:],types.float64[:]])(types.float64[:],types.float64[:],types.float64[:]),cache=True)
def get_helpers(mua,mus,n):
    light_velocity_medium = units.light_velocity_vacuum/n
    
    ta    = 1/(mua*light_velocity_medium)
    ts    = 1/(mus*light_velocity_medium)
    t_tot = 1/((mua+mus)*light_velocity_medium)
    
    return ta, ts, light_velocity_medium, t_tot

class BaseMediumProperties(BaseConfig):
    def __init__(self, name: str):
        self._name = name
        self._wavelength_nm = None
        self._scattering_inv_length_m = None
        self._absorption_inv_length_m = None
        self._group_refraction_index = None
        self._anisotropy = None
        self._scattering_model = None

        import logging
        self.log = logging.getLogger(name)
        self.log.info("initialized MediumProperties")

    @property
    def name(self) -> str:
        return self._name

    @property
    def scattering_model(self) -> str:
        return self._scattering_model

    @scattering_model.setter
    def scattering_model(self, value: str):
        self._scattering_model = value

    @property
    def wavelength_nm(self) -> np.ndarray:
        return self._wavelength_nm

    @wavelength_nm.setter
    def wavelength_nm(self, value: np.ndarray):
        self._wavelength_nm = value

    @property
    def scattering_inv_length_m(self) -> np.ndarray:
        return self._scattering_inv_length_m

    @scattering_inv_length_m.setter
    def scattering_inv_length_m(self, value: np.ndarray):
        self._scattering_inv_length_m = value

    @property
    def absorption_inv_length_m(self) -> np.ndarray:
        return self._absorption_inv_length_m

    @absorption_inv_length_m.setter
    def absorption_inv_length_m(self, value: np.ndarray):
        self._absorption_inv_length_m = value

    @property
    def group_refraction_index(self) -> np.ndarray:
        return self._group_refraction_index

    @group_refraction_index.setter
    def group_refraction_index(self, value: np.ndarray):
        self._group_refraction_index = value

    @property
    def anisotropy(self) -> float:
        return self._anisotropy

    @anisotropy.setter
    def anisotropy(self, value: float):
        self._anisotropy = value
    
    def interpolate(self,waves):
        
        mua,mus,n = interpolate(waves,self.wavelength_nm,self.scattering_inv_length_m,
                                self.absorption_inv_length_m,self.group_refraction_index)

        return mua,mus,n
    
    def get_helpers(self,mua,mus,n):
        
        ta,ts,light_velocity_medium,t_tot = get_helpers(mua,mus,n)
        
        return ta, ts, light_velocity_medium, t_tot
    '''
    def interpolate(self,waves):
        mus = np.interp(waves,self.wavelength_nm,self.scattering_inv_length_m)
        mua = np.interp(waves,self.wavelength_nm,self.absorption_inv_length_m)
        n   = np.interp(waves,self.wavelength_nm,self.group_refraction_index)

        return mua,mus,n
    
    def get_helpers(self,mua,mus,n):
        light_velocity_medium = units.light_velocity_vacuum/n
        
        ta    = 1/(mua*light_velocity_medium)
        ts    = 1/(mus*light_velocity_medium)
        t_tot = 1/((mua+mus)*light_velocity_medium)
        
        return ta, ts, light_velocity_medium, t_tot
    '''