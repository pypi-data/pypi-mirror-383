import numpy as np
from numba import njit, types

from ntsim.SensitiveDetectors.Base.BaseSensitiveDetector import BaseSensitiveDetector
from ntsim.Propagators.RayTracers.utils import segment_sphere_intersection

class SphericalSensitiveDetector(BaseSensitiveDetector):
    def __init__(self, uid, position, radius, parent):
        super().__init__(uid, position, 'sphere', parent)
        self.radius = radius

    def line_segment_intersection(self, a, b):
        intersection = segment_sphere_intersection(a, b, self.position, self.radius, 0, 1)
        return intersection

    @staticmethod
    @njit(types.float64(types.float64[:],types.float64[:]), cache=True)
    def position_response(vars, opts) -> float:
        proj = (vars[1]-opts[1])*opts[4] + \
               (vars[2]-opts[2])*opts[5] + \
               (vars[3]-opts[3])*opts[6]
        if proj > 0.:
            return 1.0
        else:
            return 0.0
    
    @staticmethod
    @njit(types.float64(types.float64[:],types.float64[:]), cache=True)
    def simu_radius(vars, opts) -> float:
        prod_radius = opts[1]
        self_radius = opts[2]
        return (self_radius/prod_radius)**2