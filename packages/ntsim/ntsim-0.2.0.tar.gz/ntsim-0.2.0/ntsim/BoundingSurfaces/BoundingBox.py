import numpy as np
from numba import njit, types

from ntsim.BoundingSurfaces.Base.BoundingBase import BoundingBase

class BoundingBox(BoundingBase):
    def __init__(self, uid: int, position_m: np.array = np.array([0.,0.,0.]), width_x_m: float = 0., width_y_m: float = 0., height_m: float = 0., parent=None):
        super().__init__(uid, position_m, parent)
        
        self._position_m = position_m
        self._width_x_m  = width_x_m
        self._width_y_m  = width_y_m
        self._height_m   = height_m
        
        self.quantities = np.append(self.position_m,(self.width_x_m,self.width_y_m,self.height_m))
        
        self.label = self.__class__.__name__
    
    @property
    def position_m(self):
        return self._position_m
    
    @position_m.setter
    def position_m(self, new_position_m):
        self._position_m = new_position_m
    
    @property
    def width_x_m(self):
        return self._width_x_m
    
    @width_x_m.setter
    def width_x_m(self, new_width_x_m):
        self._width_x_m = new_width_x_m
    
    @property
    def width_y_m(self):
        return self._width_y_m
    
    @width_y_m.setter
    def width_y_m(self, new_width_y_m):
        self._width_y_m = new_width_y_m
    
    @property
    def height_m(self):
        return self._height_m
    
    @height_m.setter
    def height_m(self, new_height_m):
        self._height_m = new_height_m
    
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
                self.position_m   = 0.5*(np.max(position_children+np.array([width_x_children,width_y_children,height_children]).T, axis=0) +
                                         np.min(position_children-np.array([width_x_children,width_y_children,height_children]).T, axis=0))
                max_point = np.abs(position_children - self.position_m) + \
                            0.5*np.array([width_x_children,width_y_children,height_children]).T
                self.width_x_m = np.max((np.max(max_point[:,0],axis=0),self.width_x_m))*2
                self.width_y_m = np.max((np.max(max_point[:,1],axis=0),self.width_y_m))*2
                self.height_m  = np.max((np.max(max_point[:,2],axis=0),self.height_m))*2
            elif child_label == 'BoundingCylinder':
                children_cylinder = [child for child in self.children if child.label == child_label]
                position_children = [child.position_m for child in children_cylinder]
                radius_children   = [child.radius_m for child in children_cylinder]
                height_children   = [child.height_m for child in children_cylinder]
                self.position_m   = 0.5*(np.max(position_children+np.array([*[radius_children]*2,height_children]).T, axis=0) +
                                         np.min(position_children-np.array([*[radius_children]*2,height_children]).T, axis=0))
                max_point = np.abs(position_children - self.position_m) + \
                            np.array([radius_children,radius_children,height_children]).T
                self.width_x_m = np.max((np.max(max_point[:,0],axis=0),self.width_x_m))*2
                self.width_y_m = np.max((np.max(max_point[:,1],axis=0),self.width_y_m))*2
                self.height_m  = np.max((np.max(max_point[:,2],axis=0),self.height_m))*2
            elif child_label == 'BoundingSphere':
                children_sphere = [child for child in self.children if child.label == child_label]
                position_children = [child.position_m for child in children_sphere]
                radius_children   = [child.radius_m for child in children_sphere]
                self.position_m   = 0.5*(np.max(position_children+np.array([radius_children]*3).T, axis=0) +
                                         np.min(position_children-np.array([radius_children]*3).T, axis=0))
                max_point = np.abs(position_children - self.position_m) + \
                            np.array([radius_children,radius_children,radius_children]).T
                self.width_x_m = np.max((np.max(max_point[:,0],axis=0),self.width_x_m))*2
                self.width_y_m = np.max((np.max(max_point[:,1],axis=0),self.width_y_m))*2
                self.height_m  = np.max((np.max(max_point[:,2],axis=0),self.height_m))*2
        self.quantities = np.append(self.position_m,(self.width_x_m,self.width_y_m,self.height_m))
    
    '''
    @staticmethod
    @njit(types.boolean(types.float64[:],types.float64[:],types.float64[:]), cache=True)
    def check_intersection(point1, point2, bb):
        # Define the parametric line: P(t) = point1 + t * (point2 - point1)
        delta = point2 - point1

        # Define the clipping parameters for t
        t_min = 0
        t_max = 1

        # Clip against each axis
        for i in range(3):
            if delta[i] == 0:
                # Line is parallel to this axis; check if it's outside the bounding box
                if point1[i] < bb[i] or point1[i] > bb[i + 3]:
                    return False
            else:
                # Compute the intersection values for this axis
                t1 = (bb[i] - point1[i]) / delta[i]
                t2 = (bb[i + 3] - point1[i]) / delta[i]

                # Swap if necessary to ensure t1 < t2
                if t1 > t2:
                    t1, t2 = t2, t1

                # Update the clipping parameters
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)

                # Check if the line is outside the bounding box
                if t_min > t_max:
                    return False

        # If we reach here, the line segment intersects the bounding box
        return True
    '''