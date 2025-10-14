import numpy as np
from abc import ABC, abstractmethod
from numba import njit, types

class BoundingBase(ABC):
    instances = {}
    
    def __init__(self, uid: int, position_m: np.array, parent = None):
        
        if uid in self.instances:
            raise ValueError(f"UID {uid} is already in use.")
        assert len(position_m) == 3
        
        self._label = ''
        
        self._uid           = uid
        self._position_m    = position_m
        self.children       = []
        self.instances[uid] = self
        self._parent        = parent
        self._depth         = -1
        
        self._sensitive_detectors = []
        
        self._quantities = np.empty(shape=(6))
        
#        self.check_children_within_bounds()
    
    @property
    def label(self):
        return self._label
    
    @label.setter
    def label(self, new_label):
        self._label = new_label
    
    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value
    
    @property
    def uid(self):
        return self._uid
    
    @property
    def position_m(self):
        return self._position_m
    
    @property
    def quantities(self):
        return self._quantities
    
    @quantities.setter
    def quantities(self, new_quantities):
        self._quantities = new_quantities
    
    def add_child(self, child, check_bounds=False):
        if child.uid not in self.instances:
            raise ValueError(f"Child with UID {child.uid} does not exist.")
        child.parent = self
        self.children.append(child)
        if check_bounds:
            self.check_children_within_bounds()  # Sanity check after adding a child
    
    def check_children_within_bounds(self):
        for child in self.children:
            if not np.all(self.critical_boundaries[:3] <= child.critical_boundaries[:3]) or \
               not np.all(self.critical_boundaries[3:] >= child.critical_boundaries[3:]):
                raise ValueError(f"Child with UID {child.uid} is not contained within parent with UID {self.uid}.")
            child.check_children_within_bounds()  # Recursively check grandchildren
    
    def find_node(self, uid):
        if self.uid == uid:
            return self
        for child in self.children:
            found = child.find_node(uid)
            if found is not None:
                return found
        return None
    
    def print(self, indent=0):
        center_str = ', '.join(f'{x:.2f}' for x in self.position_m)
        dimensions_str = ', '.join(f'{x:.2f}' for x in self.dimensions)
        bounding_box_str = ', '.join(f'{x:.2f}' for x in self.bounding_box)
        print('  ' * indent + f'UID: {self.uid}, Center: [{center_str}], Dimensions: [{dimensions_str}], Bounding Box: [{bounding_box_str}], Depth: {self._depth}')
        for child in self.children:
            child.print(indent + 1)
    
    @staticmethod
    @njit(types.float64[:,:](types.float64[:],types.float64[:,:],types.float64[:],types.float64[:]), cache=True)
    def distance2farcylinder(start_point, center_cylinders, radius_cylinders, height_cylinders):
        distance_vector = np.empty(shape=np.shape(center_cylinders),dtype=float)
        distance_value  = np.empty(shape=center_cylinders.shape[0],dtype=float)
        end_point = np.empty(shape=(3))
        for n_cylinder, center_cylinder in enumerate(center_cylinders):
            x_proj = center_cylinder[0] - start_point[0]
            y_proj = center_cylinder[1] - start_point[1]
            distance_xy = np.sqrt(x_proj**2 + y_proj**2)
            if distance_xy == 0.:
                x_proj_1 = radius_cylinders[n_cylinder]
                y_proj_1 = 0.
            else:
                x_proj_1 = x_proj * radius_cylinders[n_cylinder] / distance_xy
                y_proj_1 = y_proj * radius_cylinders[n_cylinder] / distance_xy
            end_point[0] = x_proj_1 + center_cylinder[0]
            end_point[1] = y_proj_1 + center_cylinder[1]
            end_point[2] = height_cylinders[n_cylinder] + center_cylinder[2]
            for n in range(3):
                distance_vector[n_cylinder][n] = end_point[n] - start_point[n]
            distance_value[n_cylinder] = np.sqrt(distance_vector[n_cylinder][0]**2 +
                                                distance_vector[n_cylinder][1]**2 +
                                                distance_vector[n_cylinder][2]**2)
        return distance_vector
    
    @staticmethod
    @njit(types.float64[:,:](types.float64[:],types.float64[:,:],types.float64[:]), cache=True)
    def distance2farsphere(start_point, center_spheres, radius_spheres):
        distance_vector = np.empty(shape=np.shape(center_spheres),dtype=float)
        distance_value  = np.empty(shape=center_spheres.shape[0],dtype=float)
        for n_sphere, center_sphere in enumerate(center_spheres):
            x_proj = center_sphere[0] - start_point[0]
            y_proj = center_sphere[1] - start_point[1]
            z_proj = center_sphere[2] - start_point[2]
            distance = np.sqrt(x_proj**2 + y_proj**2)
            if distance == 0.:
                x_proj_1 = 0.
                y_proj_1 = 0.
#                z_proj_1 = radius_spheres[n_sphere]
            else:
                x_proj_1 = x_proj * radius_spheres[n_sphere] / distance
                y_proj_1 = y_proj * radius_spheres[n_sphere] / distance
#                z_proj_1 = z_proj * radius_spheres[n_sphere] / distance
            distance_vector[n_sphere][0] = x_proj_1 + x_proj
            distance_vector[n_sphere][1] = y_proj_1 + y_proj
            distance_vector[n_sphere][2] = radius_spheres[n_sphere] + z_proj
            distance_value[n_sphere] = np.sqrt(distance_vector[n_sphere][0]**2 +
                                                distance_vector[n_sphere][1]**2 +
                                                distance_vector[n_sphere][2]**2)
        return distance_vector
    
    '''
    @abstractmethod
    def check_intersection(start_point,end_point,centert,*parameters):
        pass
    '''