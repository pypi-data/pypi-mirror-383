from ntsim.SensitiveDetectors.Base.SphericalSensitiveDetector import SphericalSensitiveDetector
from ntsim.SensitiveDetectors.Base.BaseSensitiveDetector import BaseSensitiveDetector

import numpy as np
from numba import njit, types, typed

# create pde effect
example1_waves = np.linspace(350, 600, 100)
example1_pde_values = np.linspace(0.25, 0.05, 100)  # Example PDE values, arbitrary numbers

@njit(types.float64(types.float64[:],types.float64[:]), cache=True)
def example1_pde(vars, opts) -> float:
    w = vars[0]
    return np.interp(w, example1_waves, example1_pde_values)

class Example1SensitiveDetector(SphericalSensitiveDetector):
    def __init__(self, uid: int, position: np.ndarray, radius: float, photocathode_unit_vector: np.ndarray, parent: BaseSensitiveDetector):
        super().__init__(uid, position, radius, parent)
        self.photocathode_unit_vector = photocathode_unit_vector/np.linalg.norm(photocathode_unit_vector)

        # Add effects
        self.add_effect(example1_pde, np.array([uid,0.,0.,0.]), 'pde')
        self.add_effect(self.position_response, np.array([uid,*self.photocathode_unit_vector]), 'pos_response')
