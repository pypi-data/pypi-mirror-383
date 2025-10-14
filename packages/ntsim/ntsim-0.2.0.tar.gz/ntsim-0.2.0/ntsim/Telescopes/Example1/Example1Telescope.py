from ntsim.Telescopes.Base.BaseTelescope import BaseTelescope
from ntsim.BoundingSurfaces.BoundingBox import BoundingBox
from ntsim.BoundingSurfaces.BoundingCylinder import BoundingCylinder
from ntsim.BoundingSurfaces.BoundingSphere import BoundingSphere
#from ntsim.SensitiveDetectors.Example1.Example1SensitiveDetector import Example1SensitiveDetector
import numpy as np
from argparse import Namespace

class Example1Telescope(BaseTelescope):
    arg_dict = {
            'radius': {'type': float, 'default': 1, 'help': 'sensitive_detector radius'},
            'photocathode_unit_vector': {'type': float, 'nargs': 3, 'default': [0, 0, -1], 'help': 'unit vector of the sensitive detector photocathode'},
            'n_clusters_x': {'type': int, 'default': 1, 'help': 'Number of clusters in x direction'},
            'n_clusters_y': {'type': int, 'default': 1, 'help': 'Number of clusters in y direction'},
            'n_clusters_z': {'type': int, 'default': 1, 'help': 'Number of clusters in z direction'},
            'x_cluster_spacing': {'type': float, 'default': 1, 'help': 'Spacing between clusters in x direction'},
            'y_cluster_spacing': {'type': float, 'default': 1, 'help': 'Spacing between clusters in y direction'},
            'z_cluster_spacing': {'type': float, 'default': 1, 'help': 'Spacing between clusters in z direction'},
            'n_strings_x': {'type': int, 'default': 1, 'help': 'Number of strings in x direction'},
            'n_strings_y': {'type': int, 'default': 1, 'help': 'Number of strings in y direction'},
            'x_string_spacing': {'type': float, 'default': 1, 'help': 'Spacing between strings in x direction'},
            'y_string_spacing': {'type': float, 'default': 1, 'help': 'Spacing between strings in y direction'},
            'n_detectors_z': {'type': int, 'default': 1, 'help': 'Number of detectors in z direction'},
            'z_detector_spacing': {'type': float, 'default': 1, 'help': 'Spacing between detectors in z direction'},
            
            'world_center': {'type': float, 'nargs': 3, 'default': [0, 0, 0], 'help': 'Center of the world'},
        }

    def add_bounding_boxes(self) -> bool:
        self.world_center = np.array(self.world_center)

        # Create a world
#        self._world = BoundingBoxNode(uid=0, center=self.world_center, dimensions=np.array([1, 1, 1]))  # dimensions will be updated in add_bounding_boxes method
        self._world = BoundingBox(uid=0)  # dimensions will be updated in add_bounding_boxes method

        # On UID numbering scheme
        # Assign UIDs to clusters starting from 1.
        # Assign UIDs to strings starting from 100. For each string, its UID will be 100 + cluster_uid * 100 + relative_string_uid.
        # Assign UIDs to sensitive detectors starting from 1000. For each sensitive detector, its UID will be 1000 + string_uid * 10 + relative_detector_uid.

        # To get the cluster UID from a string UID: (string_uid - 100) // 100
        # To get the relative string UID within its cluster: (string_uid - 100) % 100
        # To get the string UID from a detector UID: (detector_uid - 1000) // 10
        # To get the relative detector UID within its string: (detector_uid - 1000) % 10

        if self.n_clusters_x * self.n_clusters_y * self.n_clusters_z > 100:
            raise ValueError("Number of clusters exceeds the limit of 100!")

        # Initialize bounding box nodes
        cluster_uid = 1
        string_uid_base = 100
        detector_uid_base = 1000
        for q in range(self.n_clusters_z):
            for i in range(self.n_clusters_x):
                for j in range(self.n_clusters_y):
                    # Adjust cluster_center calculation
                    cluster_center = self.world_center / 2 + np.array([(i - (self.n_clusters_x - 1) / 2) * self.x_cluster_spacing,
                                                               (j - (self.n_clusters_y - 1) / 2) * self.y_cluster_spacing, (q - (self.n_clusters_z - 1) / 2) * self.z_cluster_spacing / 2])
                    # cluster = BoundingBoxNode(uid=cluster_uid, center=cluster_center, dimensions=np.array([0, 0, 0]))  # Initialize with zero dimensions
                    cluster = BoundingBox(uid=cluster_uid)  # Initialize with zero dimensions
                    self.world.add_child(cluster)
                    cluster_uid += 1

                    for k in range(self.n_strings_x):
                        for l in range(self.n_strings_y):
                            # Adjust string_center calculation
                            string_center = cluster_center + np.array([(k - (self.n_strings_x - 1) / 2) * self.x_string_spacing,
                                                                   (l - (self.n_strings_y - 1) / 2) * self.y_string_spacing, 0])
#                        string = BoundingBoxNode(uid=string_uid_base, center=string_center, dimensions=np.array([0, 0, 0]))  # Initialize with zero dimensions
                            string = BoundingCylinder(uid=string_uid_base)  # Initialize with zero dimensions
                            cluster.add_child(string)
                            string_uid_base += 1

                            for m in range(self.n_detectors_z):
                                total_detector_height = self.n_detectors_z * self.z_detector_spacing
                                adjusted_start_z = string_center[2] - total_detector_height / 2 + self.z_detector_spacing / 2  # +z_spacing/2 to start from the center of the first detector
                                detector_center = string_center + np.array([0, 0, (adjusted_start_z + m * self.z_detector_spacing)])
                                detector_radius = self.radius
#                            detector_dimensions = np.array([2 * detector_radius, 2 * detector_radius, 2 * detector_radius])
#                            detector = BoundingBoxNode(uid=detector_uid_base, center=detector_center, dimensions=detector_dimensions)
                                detector = BoundingSphere(uid=detector_uid_base, position_m=detector_center, radius_m=detector_radius)
                                string.add_child(detector)
                                detector_uid_base += 1

                        # Update string dimensions
                            string.update_critical_boundaries()
                # Update cluster dimensions
                    cluster.update_critical_boundaries()

        # Update world dimensions
        self.world.update_critical_boundaries()
#        self.world.check_children_within_bounds()

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
                    position=node.position_m,
                    radius=self.radius,
                    photocathode_unit_vector=np.array(self.photocathode_unit_vector),
                    parent=node
                )
                node._sensitive_detectors.append(detector)
        return True
