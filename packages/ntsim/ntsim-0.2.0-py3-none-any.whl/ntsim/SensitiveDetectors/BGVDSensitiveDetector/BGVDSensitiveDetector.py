from typing import List
from numba import njit, types, typed
import numpy as np
from ntsim.SensitiveDetectors.Base.SphericalSensitiveDetector import SphericalSensitiveDetector
from ntsim.SensitiveDetectors.Base.BaseSensitiveDetector import BaseSensitiveDetector

from bgvd_model import OpticalModule

#compile the functions for numba
bgvd_angular_dependency = njit(types.float64(types.float64))(OpticalModule.angular_dependency)
bgvd_transmission_gel_glass = njit(types.float64(types.float64))(OpticalModule.transmission_gel_glass)
bgvd_efficiency = njit(types.float64(types.float64))(OpticalModule.efficiency)
    
@njit(types.float64(types.float64[:],types.float64[:]), cache=True)
def om_angular_dependence(vars, opts) -> float:
    # vars[5-7] stores hit unit vector from the SphericalSensitiveDetector center to the hit position
    # opts[0-2] stores unit vector pointing to SphericalSensitiveDetector photocathode center (at least for BGVD case)
    unit_x = vars[5]
    unit_y = vars[6]
    unit_z = vars[7]
    x = unit_x*opts[1]+unit_y*opts[2]+unit_z*opts[3]
    x = -x
    return bgvd_angular_dependency(x)

@njit(types.float64(types.float64[:],types.float64[:]), cache=True)
def pde(vars, opts) -> float:
    w = vars[0]
    return bgvd_efficiency(w)

@njit(types.float64(types.float64[:],types.float64[:]), cache=True)
def transmission_gel_glass(vars, opts) -> float:
    w = vars[0]
    return bgvd_transmission_gel_glass(w)

class BGVDSensitiveDetector(SphericalSensitiveDetector):
    _self_radius = OpticalModule.radius
    
    def __init__(self, uid: int, position: np.ndarray, radius: float, photocathode_unit_vector: np.ndarray, parent: BaseSensitiveDetector):
        super().__init__(uid, position, radius, parent)
        plug = np.array([uid,0.,0.,0.,0.,0.,0.])
        self.photocathode_unit_vector = photocathode_unit_vector/np.linalg.norm(photocathode_unit_vector)
        # Add effects
        self.add_effect(om_angular_dependence,np.array([uid,*self.photocathode_unit_vector,0.,0.,0.]),'angular_dependence')
        self.add_effect(pde,plug,'pde')
        self.add_effect(transmission_gel_glass,plug,'gel_transmission')
#        self.add_effect(self.position_response, np.array([uid,*self.position,*self.photocathode_unit_vector]),'pos_response')
        self.add_effect(self.simu_radius, np.array([uid,radius,self._self_radius,0.,0.,0.,0.]),'prod_radius')
