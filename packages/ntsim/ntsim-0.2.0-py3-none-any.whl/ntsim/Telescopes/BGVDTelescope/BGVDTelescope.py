import numpy as np

from bgvd_model.GVDGeometry import GVDGeometry

from ntsim.Telescopes.Base.BaseTelescope import BaseTelescope
from ntsim.SensitiveDetectors.BGVDSensitiveDetector.BGVDSensitiveDetector import BGVDSensitiveDetector

from ntsim.BoundingSurfaces.BoundingCylinder import BoundingCylinder
from ntsim.BoundingSurfaces.BoundingSphere import BoundingSphere
from ntsim.BoundingSurfaces.BoundingBox import BoundingBox

class BGVDTelescope(BaseTelescope):
    arg_dict = {
            'geometry_dataset': {'type': str, 'default': '2021', 'help': ''},
            'position_m': {'type': float, 'nargs': 3, 'default': None, 'help': ''},
            'radius_OM_m': {'type': float, 'default': 0.216, 'help': ''},
            'n_clusters': {'type': float, 'nargs': '+', 'choices': [1,2,3,4,5,6,7,8], 'default': [1,2,3,4,5,6,7,8], 'help': ''},
            'season': {'type': int, 'default': 2021, 'help': ''}
        }
    
    def cluster_center_coordinates(self, cluster_data) -> np.ndarray:
        center_postition = np.zeros(3) 
        self.logger.info("Cluster's centered to (0,0)")
        center_postition[0] = cluster_data['mx_m'].mean()
        center_postition[1] = cluster_data['my_m'].mean()
        center_postition[2] = 0

        return center_postition
    
    def add_bounding_boxes(self) -> bool:
        try:
            bgvd = GVDGeometry.from_dataset(self.geometry_dataset)
        except ValueError:
             bgvd = GVDGeometry.from_csv(self.geometry_dataset)
            
        bgvd = bgvd.select(self.n_clusters)
        #read list of clusters from geometry
        self.n_clusters = bgvd.clusters
        df =  bgvd.get_clusters(self.n_clusters)

        position_OM_m     = np.array([df['mx_m'],df['my_m'],df['mz_m']]).T
        self.direction_OM = np.array([df['dir_x'],df['dir_y'],df['dir_z']]).T
        
        self.world_center = [0., 0., 0.]

        if self.position_m is not None:
            self.world_center = self.position_m
            telescope_coordinates = self.cluster_center_coordinates(df)
            position_OM_m -= (telescope_coordinates - self.world_center)
        
        self.world = BoundingCylinder(uid=0, position_m=self.world_center)

        counter = 0
        for n_cluster in self.n_clusters:
            uid_base = n_cluster*10000
            cluster = BoundingCylinder(uid=uid_base)
            self.world.add_child(cluster)
            for n_string in range(8):
                uid_base += 1000
                string = BoundingCylinder(uid=uid_base)
                cluster.add_child(string)
                for n_section in range(3):
                    uid_base += 100
                    section = BoundingCylinder(uid=uid_base)
                    string.add_child(section)
                    for n_channel in range(12):
                        uid_base += 1
                        channel = BoundingSphere(uid=uid_base,position_m=position_OM_m[counter],radius_m=self.radius_OM_m)
                        section.add_child(channel)
                        counter += 1
                    uid_base -= 12
                    section.update_critical_boundaries()
                uid_base -= 3*100
                string.update_critical_boundaries()
            uid_base -= 8*1000
            cluster.update_critical_boundaries()
        self.world.update_critical_boundaries()
        
        self.logger.info("Added bounding nodes")
        return True
        
    
    def place_sensitive_detectors(self) -> bool:
        # Place sensitive detectors at the centers of the bounding box nodes
        if self._world is None:
            raise ValueError("World has not been initialized!")

        if not self.arg_dict:
            raise ValueError("Class has not been configured!")

        if self._sensitive_detector_blueprint is None:
            raise ValueError("Class has no _sensitive_detector!")
        n_unit_vector = 0
        for uid, node in self.world.instances.items():
            if len(node.children) == 0:  # If the node is a leaf (i.e., it has no children)
                detector = self._sensitive_detector_blueprint(
                    uid=node.uid,
                    position=node.position_m,
                    radius=self.radius_OM_m,
                    photocathode_unit_vector=self.direction_OM[n_unit_vector],
                    parent=node
                )
                node._sensitive_detectors.append(detector)
                n_unit_vector += 1
        
        self.logger.info("Placed sensitive detectors")
        return True
    
    
