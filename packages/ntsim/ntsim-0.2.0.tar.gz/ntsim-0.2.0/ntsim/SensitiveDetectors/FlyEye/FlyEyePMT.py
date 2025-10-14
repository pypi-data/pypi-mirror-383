import numpy as np

from numba import njit, types

from ntsim.SensitiveDetectors.Base.SphericalSensitiveDetector import SphericalSensitiveDetector
from ntsim.SensitiveDetectors.Base.BaseSensitiveDetector import BaseSensitiveDetector

bgvd_angular_parameters = np.array([0.3082,-0.54192,0.19831,0.04912])
bgvd_waves = np.linspace(300,650,8)
bgvd_eff   = np.array([0.28,0.35,0.35,0.3,0.22,0.12,0.05,0.02])
bgvd_wavelength  = np.linspace(350,650,14)
bgvd_transmission_gel_glass = np.array([1.38e-3,5.e-3,0.544,0.804,0.83,0.866,0.9,0.9,0.9,0.9,0.9,0.9,0.9,0.9])

@njit(types.float64(types.float64[:],types.float64[:]), cache=True)
def om_angular_dependence(vars, opts) -> float:
    # vars[5-7] stores hit unit vector from the SphericalSensitiveDetector center to the hit position
    # opts[1-3] stores unit vector pointing to SphericalSensitiveDetector photocathode center (at least for BGVD case)
    unit_x = vars[5]
    unit_y = vars[6]
    unit_z = vars[7]
    x = unit_x*opts[1]+unit_y*opts[2]+unit_z*opts[3]
    x = -x
    f = 0.0
    for m in range(4):
        f += bgvd_angular_parameters[m]*x**m
    return f

@njit(types.float64(types.float64[:],types.float64[:]), cache=True)
def pde(vars, opts) -> float:
    w = vars[0]
    return np.interp(w,bgvd_waves,bgvd_eff)

@njit(types.float64(types.float64[:],types.float64[:]), cache=True)
def transmission_gel_glass(vars, opts) -> float:
    w = vars[0]
    return np.exp(np.interp(w,bgvd_wavelength,np.log(bgvd_transmission_gel_glass)))

class Fly_Eye_PMT(SphericalSensitiveDetector):
    def __init__(self, uid: int, position: np.ndarray, radius: float, photocathode_unit_vector: np.ndarray, parent: BaseSensitiveDetector):
        super().__init__(uid, position, radius, parent)
        self.photocathode_unit_vector = photocathode_unit_vector/np.linalg.norm(photocathode_unit_vector)
        
        # Add effects 
        self.add_effect(om_angular_dependence, np.array([uid,*self.photocathode_unit_vector,0.,0.,0.]), 'om_angular_dependence')
        self.add_effect(pde, np.array([uid,0.,0.,0.,0.,0.,0.]), 'pde')
        self.add_effect(transmission_gel_glass, np.array([uid,0.,0.,0.,0.,0.,0.]), 'transmission_gel_glass')
        self.add_effect(self.position_response, np.array([uid,*position,*self.photocathode_unit_vector]), 'position_response')