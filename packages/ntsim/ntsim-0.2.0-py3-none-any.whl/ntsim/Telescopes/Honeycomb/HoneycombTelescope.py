from ntsim.Telescopes.Base.BaseTelescope import BaseTelescope
from ntsim.BoundingSurfaces.BoundingBox import BoundingBox
from ntsim.BoundingSurfaces.BoundingCylinder import BoundingCylinder
from ntsim.BoundingSurfaces.BoundingSphere import BoundingSphere
#from ntsim.SensitiveDetectors.Example1.Example1SensitiveDetector import Example1SensitiveDetector
import numpy as np
from argparse import Namespace

class HoneycombTelescope(BaseTelescope):
    arg_dict = {
            'side': {'type': float, 'default': 1, 'help': 'length of comb side'},
            'height': {'type': float, 'default': 10, 'help': 'total height of telescope'},
            'width': {'type': int, 'default': 10, 'help': 'total width of telescope'},
            'length': {'type': int, 'default': 10, 'help': 'total length of telescope'},
            'z_spacing': {'type': float, 'default': 1, 'help': 'spacing in z direction'},
            'r_spacing': {'type': float, 'default': 3, 'help': 'spacing in x and y directions'},
            'position': {'type': float, 'nargs': 3, 'default': [0, 0, 0], 'help': 'center of the first comb'},
            'central_string': {'type': bool, 'default': False, 'help': 'place central string'},
            'radius': {'type': float, 'default': 1, 'help': 'sensitive_detector radius'},
            'photocathode_unit_vector': {'type': float, 'nargs': 3, 'default': [0, 0, -1], 'help': 'unit vector of the sensitive detector photocathode'},
            'world_center': {'type': float, 'nargs': 3, 'default': [0, 0, 0], 'help': 'Center of the world'},
        }
    
    def add_bounding_boxes(self) -> bool:
        self.world_center = np.array(self.world_center)

        # Create a world
 #       self._world = BoundingBoxNode(uid=0, center=self.world_center, dimensions=np.array([1, 1, 1]))  # dimensions will be updated in add_bounding_boxes method
        self._world = BoundingCylinder(uid=0, position_m=self.world_center)

        # On UID numbering scheme
        # Assign UIDs to clusters starting from 1.
        # Assign UIDs to strings starting from 100. For each string, its UID will be 100 + cluster_uid * 100 + relative_string_uid.
        # Assign UIDs to sensitive detectors starting from 1000. For each sensitive detector, its UID will be 1000 + string_uid * 10 + relative_detector_uid.

        # To get the cluster UID from a string UID: (string_uid - 100) // 100
        # To get the relative string UID within its cluster: (string_uid - 100) % 100
        # To get the string UID from a detector UID: (detector_uid - 1000) // 10
        # To get the relative detector UID within its string: (detector_uid - 1000) % 10

        
        if self.central_string == True:
            n_strings = 7
        else:
            n_strings = 6
            
        n_detectors_z = int(self.height // self.z_spacing)
        Nx = int(self.width * 2 // self.r_spacing)
        Ny = int(self.length // (self.r_spacing * np.sin(np.pi/3)))
        # Initialize bounding box nodes
        cluster_uid = 1
        string_uid_base = 100
        detector_uid_base = 1000
        #Nx = 1
        #Ny = 3
        for nx in range(Nx):
            cluster_center_x_n = self.position[0] + nx * self.r_spacing/2
            cluster_center_z_n = self.position[2]
            for ny in range(Ny):
                if nx % 2 == 0:
                    cluster_center_y_n = self.position[1] + ny * 2 * self.r_spacing * np.cos(np.pi/6)
                else:
                    cluster_center_y_n = self.position[1] + self.r_spacing * np.sin(np.pi/3) + ny * 2 * self.r_spacing * np.cos(np.pi/6)
            
                cluster_center_n = np.array([cluster_center_x_n, cluster_center_y_n, cluster_center_z_n])
                cluster_center = self.world.position_m + cluster_center_n
                cluster = BoundingCylinder(uid=cluster_uid, position_m=cluster_center)
                self.world.add_child(cluster)
                cluster_uid += 1

                for j in range(n_strings):
                    if j == 6:
                        string_center = cluster_center
                    else:
                        string_center_x = cluster_center[0] + self.side * np.cos(j * np.pi/ 3)
                        string_center_y = cluster_center[1] + self.side * np.sin(j * np.pi/ 3)
                        string_center_z = cluster_center[2]
                        string_center = np.array([string_center_x, string_center_y, string_center_z])
                    string = BoundingCylinder(uid=string_uid_base, position_m=string_center)
                    cluster.add_child(string)
                    string_uid_base += 1

                    for k in range(n_detectors_z):
                        adjusted_start_z = string_center[2] - self.height / 2 + self.z_spacing / 2
                        detector_center = string_center + np.array([0, 0, adjusted_start_z + k * self.z_spacing])
                        detector = BoundingSphere(uid=detector_uid_base, position_m=detector_center, radius_m=self.radius)
                        string.add_child(detector)
                        detector_uid_base += 1

                    # Update string dimensions
                    string.update_critical_boundaries()
            
                # Update cluster dimensions
                cluster.update_critical_boundaries()

        # Update world dimensions
        self.world.update_critical_boundaries()
        #self.world.check_children_within_bounds()

        return True

    def place_sensitive_detectors(self) -> bool:
        # Place sensitive detectors at the centers of the bounding box nodes
        if self._world is None:
            raise ValueError("World has not been initialized!")

        if not self.arg_dict:
            raise ValueError("Class has not been configured!")

        if self._sensitive_detector_blueprint is None:
            raise ValueError("Class has no _sensitive_detector!")

        for uid, node in self.world.instances.items():
            if len(node.children) == 0:  # If the node is a leaf (i.e., it has no children)
                detector = self._sensitive_detector_blueprint(
                    uid=node.uid,
                    position = node.position_m,
                    radius=self.radius,
                    photocathode_unit_vector=np.array(self.photocathode_unit_vector),
                    parent=node
                )
                node._sensitive_detectors.append(detector)
        return True
