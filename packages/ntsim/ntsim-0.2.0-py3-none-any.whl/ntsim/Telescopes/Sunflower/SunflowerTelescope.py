import numpy as np

from ntsim.Telescopes.Base.BaseTelescope import BaseTelescope
from ntsim.SensitiveDetectors.FlyEye.FlyEyePMT import Fly_Eye_PMT
from ntsim.SensitiveDetectors.FlyEye.FlyEyeCompound import Fly_Eye_Compound

from ntsim.BoundingSurfaces.BoundingCylinder import BoundingCylinder
from ntsim.BoundingSurfaces.BoundingSphere import BoundingSphere
from ntsim.BoundingSurfaces.BoundingBox import BoundingBox

class SunflowerTelescope(BaseTelescope):
    arg_dict = {
            'telescope_position_m': {'type': float, 'nargs': 3, 'default': [0.,0.,0.], 'help': ''},
            'n_strings': {'type': int, 'default': 1, 'help': ''},
            'n_detectors_z': {'type': int, 'default': 1, 'help': ''},
            'z_spacing_m': {'type': float, 'default': 1., 'help': ''},
            'segments_nu': {'type': int, 'default': 1, 'help': ''},
            'radius_icosphere': {'type': float, 'default': 10., 'help': ''},
            'unit_vector_compound': {'type': float, 'nargs': 3, 'default': [0.,0.,-1.], 'help': ''}
        }
    
    def add_bounding_boxes(self) -> bool:
        Fly_Eye = Fly_Eye_Compound()
        Fly_Eye.segments_nu = self.segments_nu
        Fly_Eye.radius_icosphere_m = self.radius_icosphere
        Fly_Eye.unit_vector_compound = self.unit_vector_compound
        Fly_Eye.generate_icosphere()
        
        self.radius_compound_m = Fly_Eye.radius_compound_m
        self.radius_PMT_m      = Fly_Eye.radius_PMT_m
        self.unit_vector_PMT   = Fly_Eye.unit_vector_PMT
        
        self.world_center = np.array(self.telescope_position_m)

        self.world = BoundingCylinder(uid=1)

        cluster_uid = 1
        string_uid_base = 1000
        compound_uid_base = 100000
        detector_uid_base = 10000000
        
        total_detector_height = self.n_detectors_z*self.z_spacing_m

        for n_string in range(self.n_strings):
            r = 50*np.sqrt(n_string)
            phi = np.pi*(1+5**0.5)*n_string
            x = r*np.cos(phi)
            y = r*np.sin(phi)
            string_position_m = self.telescope_position_m + np.array([x,y,0.])
            adjusted_start_z = string_position_m[2]-total_detector_height/2.+self.z_spacing_m/2. - self.telescope_position_m[2]
            string = BoundingCylinder(uid=string_uid_base)
            self.world.add_child(string)
            string_uid_base += 1
            
            for n_compound in range(self.n_detectors_z):
                Fly_Eye.position_compound_m = string_position_m+np.array([0.,0.,adjusted_start_z+n_compound*self.z_spacing_m])
                compound = BoundingSphere(uid=compound_uid_base)
                detector_positions_m = Fly_Eye.place_boundings()
                string.add_child(compound)
                compound_uid_base += 1
                for detector_bounding_position_m in detector_positions_m:
                    detector = BoundingSphere(uid=detector_uid_base, position_m=detector_bounding_position_m, radius_m=Fly_Eye.radius_PMT_m)
                    compound.add_child(detector)
                    detector_uid_base += 1
                
                compound.update_critical_boundaries()
            
            string.update_critical_boundaries()
        
        self.world.update_critical_boundaries()
#        self.world.check_children_within_bounds()

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
                if n_unit_vector >= 20*self.segments_nu**2 : n_unit_vector = 0
                detector = self._sensitive_detector_blueprint(
                    uid=node.uid,
                    position=node.position_m,
                    radius=self.radius_PMT_m,
                    photocathode_unit_vector=np.array(self.unit_vector_PMT[n_unit_vector]),
                    parent=node
                )
                node._sensitive_detectors.append(detector)
                n_unit_vector += 1
        
        self.logger.info("Placed sensitive detectors")
        return True