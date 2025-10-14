import numpy as np
from numba import njit, types

from ntsim.BoundingSurfaces.Base.BoundingBase import BoundingBase

class BoundingSphere(BoundingBase):
    def __init__(self, uid: int, position_m: np.array = np.array([0.,0.,0.]), radius_m: float = 0., parent = None):
        super().__init__(uid, position_m, parent)
        
        self._position_m = position_m
        self._radius_m   = radius_m
        
        self.quantities = np.append(self.position_m,(self.radius_m,0.,0.))
        
        self.label = self.__class__.__name__
    
    @property
    def position_m(self):
        return self._position_m
    
    @position_m.setter
    def position_m(self, new_position_m):
        self._position_m = new_position_m
    
    @property
    def radius_m(self):
        return self._radius_m
    
    @radius_m.setter
    def radius_m(self, new_radius_m):
        self._radius_m = new_radius_m
    
    def update_critical_boundaries(self) -> None:
        if not self.children:
            return None
        for child_label in set([child.label for child in self.children]):
            if child_label == 'BoundingBox':
                children_box = [child for child in self.children if child.label == child_label]
                position_children = np.array([child.position_m for child in children_box])
                width_x_children  = np.array([child.width_x_m for child in children_box])
                width_y_children  = np.array([child.width_y_m for child in children_box])
                height_children   = np.array([child.height_m for child in children_box])
                self.position_m   = 0.5*(np.max(position_children, axis=0) +
                                         np.min(position_children, axis=0))
                max_point = np.abs(position_children - self.position_m) + \
                            np.array([width_x_children,width_y_children,height_children]).T
                distance_list = np.array([np.sqrt(np.sum(max_point**2,axis=1))])
                self.radius_m = np.max((np.max(distance_list),self.radius_m))
            elif child_label == 'BoundingCylinder':
                children_cylinder = [child for child in self.children if child.label == child_label]
                position_children = np.array([child.position_m for child in children_cylinder])
                radius_children   = np.array([child.radius_m for child in children_cylinder], dtype=float)
                height_children   = np.array([child.height_m for child in children_cylinder], dtype=float)
                self.position_m   = 0.5*(np.max(position_children, axis=0) +
                                         np.min(position_children, axis=0))
                point_list = self.distance2farcylinder(self.position_m,position_children,radius_children,height_children)
                distance_list = np.sqrt(np.sum(point_list**2,axis=1))
                self.radius_m = np.max((np.max(distance_list),self.radius_m))
            elif child_label == 'BoundingSphere':
                children_sphere = [child for child in self.children if child.label == child_label]
                position_children = np.array([child.position_m for child in children_sphere])
                radius_children   = np.array([child.radius_m for child in children_sphere], dtype=float)
                self.position_m   = 0.5*(np.max(position_children, axis=0) +
                                         np.min(position_children, axis=0))
                point_list = self.distance2farsphere(self.position_m,position_children,radius_children)
                distance_list = np.sqrt(np.sum(point_list**2,axis=1))
                self.radius_m = np.max((np.max(distance_list),self.radius_m))
        self.quantities = np.append(self.position_m,(self.radius_m,0.,0.))
    
    '''
    @staticmethod
    @njit(types.boolean(types.float64[:],types.float64[:],types.float64[:]), cache=True)
    def check_intersection(point1, point2, bounding_sphere):
        
        x1,y1,z1   = point1
        x2,y2,z2   = point2
        x3,y3,z3,r = bounding_sphere
        
        a = (x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2
        b = 2*((x2 - x1) * (x1 - x3) + (y2 - y1) * (y1 - y3) + (z2 - z1) * (z1 - z3))
        c = x3**2 + y3**2 + z3**2 + x1**2 + y1**2 + z1**2 - 2*(x3*x1 + y3*y1 + z3*z1) - r**2
        
        d = b**2 - 4*a*c
        
        if d < 0:
            return False
        
        return True
    '''