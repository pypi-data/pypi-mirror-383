import numpy as np
from icosphere import icosphere

from ntsim.utils.rotate_utils import rotate_vectors
from ntsim.SensitiveDetectors.FlyEye.FlyEyePMT import Fly_Eye_PMT
from ntsim.SensitiveDetectors.Base.BaseSensitiveDetector import BaseSensitiveDetector

class Fly_Eye_Compound():
    def __init__(self):
        self._segments_nu: int               = 0
        self._n_segments: int                = 20*self._segments_nu**2
        self._position_compound_m: np.array    = np.empty(shape=(3),dtype=float)
        self._radius_icosphere_m: float         = 0.
        self._unit_vector_compound: np.array = np.empty(shape=(3),dtype=float)
        
        self._position_PMT_m  = np.empty(shape=(0,3),dtype=float)
        self._radius_PMT_m    = np.empty(shape=(0),dtype=float)
        self._unit_vector_PMT = np.empty(shape=(0,3),dtype=float)
        
        self._radius_compound_m: float  = 0.
        
        self._PMT_list = np.empty(shape=(0),dtype=Fly_Eye_PMT)
    
    @property
    def segments_nu(self):
        if not self._segments_nu:
            ValueError('')
        return self._segments_nu
    
    @segments_nu.setter
    def segments_nu(self, new_sengments_new):
        self._segments_nu = new_sengments_new
    
    @property
    def n_segments(self):
        if not self._n_segments:
            ValueError('')
        return self._n_segments

    @property
    def position_compound_m(self):
        if not self._position_compound_m.size:
            ValueError('')
        return self._position_compound_m
    
    @position_compound_m.setter
    def position_compound_m(self, new_position_compound_m):
        self._position_compound_m = new_position_compound_m
    
    @property
    def radius_icosphere_m(self):
        if not self._radius_icosphere_m:
            ValueError('')
        return self._radius_icosphere_m
    
    @radius_icosphere_m.setter
    def radius_icosphere_m(self, new_radius_icosphere_m):
        self._radius_icosphere_m = new_radius_icosphere_m
    
    @property
    def unit_vector_compound(self):
        if not self._unit_vector_compound.size:
            ValueError('')
        return self._unit_vector_compound
    
    @unit_vector_compound.setter
    def unit_vector_compound(self, new_unit_vector_compound):
        self._unit_vector_compound = new_unit_vector_compound/np.linalg.norm(new_unit_vector_compound)
    
    @property
    def position_PMT_m(self):
        if not self._position_PMT_m.size:
            ValueError('')
        return self._position_PMT_m
    
    @position_PMT_m.setter
    def position_PMT_m(self, new_position_PMT_m):
        self._position_PMT_m = new_position_PMT_m
    
    @property
    def radius_PMT_m(self):
        if not self._radius_PMT_m.size:
            ValueError('')
        return self._radius_PMT_m
    
    @radius_PMT_m.setter
    def radius_PMT_m(self, new_radius_PMT_m):
        self._radius_PMT_m = new_radius_PMT_m
    
    @property
    def unit_vector_PMT(self):
        if not self._unit_vector_PMT.size:
            ValueError('')
        return self._unit_vector_PMT
    
    @unit_vector_PMT.setter
    def unit_vector_PMT(self, new_unit_vector_PMT):
        self._unit_vector_PMT = new_unit_vector_PMT
    
    @property
    def radius_compound_m(self):
        radius_compound = np.sqrt(np.sum(self.position_PMT_m[0]**2))+self.radius_PMT_m
        return radius_compound
    
    @property
    def PMT_list(self):
        if not self._PMT_list.size:
            ValueError('')
        return self._PMT_list
    
    @PMT_list.setter
    def PMT_list(self, new_PMT_list):
        self._PMT_list = new_PMT_list
    
    def set_normal_per_segment(self, vertices: np.ndarray) -> np.ndarray:
        side1  = vertices[:,0]-vertices[:,1]
        side2  = vertices[:,1]-vertices[:,2]
        normal = np.cross(side1,side2)
        norm_cross = np.sqrt(np.sum(normal**2,axis=1))
        normal = normal/norm_cross[:,np.newaxis]
        return normal
    
    def generate_icosphere(self) -> None:
        vertices, faces  = icosphere(nu=self.segments_nu)
        vertices        *= self.radius_icosphere_m
        vertices         = vertices[faces]
#        side_length      = np.sqrt(np.sum((vertices[0][0]-vertices[0][1])**2))
        
        self.unit_vector_PMT  = self.set_normal_per_segment(vertices)
        self.unit_vector_PMT  = rotate_vectors(np.array([0.,0.,-1.]),self.unit_vector_compound,self.unit_vector_PMT)
        norm_cross            = np.sqrt(np.sum(self.unit_vector_PMT**2,axis=1))
        self.unit_vector_PMT /= norm_cross[:,np.newaxis]
        
        self.position_PMT_m = np.sum(vertices,axis=1)/3
        self.position_PMT_m = rotate_vectors(np.array([0.,0.,-1.]),self.unit_vector_compound,self.position_PMT_m)
        
#        self.radius_PMT_m = side_length/(2*np.sqrt(3))
        self.radius_PMT_m = np.min(np.sqrt(np.sum(np.diff(self.position_PMT_m,axis=0)**2,axis=1)))/2.
    
    def place_boundings(self) -> np.ndarray:
        position_boundings_m = np.array([position_PMT+self.position_compound_m for position_PMT in self.position_PMT_m])
        return position_boundings_m
    
    def place_PMTs(self, uid: int, parent) -> None:
        for n, segment in enumerate(self.position_PMT_m):
            PMT = Fly_Eye_PMT(uid=uid+n,
                              position=self.position_compound_m+segment,
                              radius=self.radius_PMT_m,
                              photocathode_unit_vector=self.unit_vector_PMT[n],
                              parent=parent)
            self.PMT_list = np.append(self.PMT_list,PMT)