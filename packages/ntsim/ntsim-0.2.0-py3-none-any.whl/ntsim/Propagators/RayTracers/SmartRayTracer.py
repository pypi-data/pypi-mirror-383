import numpy as np
from ntsim.Propagators.RayTracers.rt_utils import ray_tracer
from ntsim.utils.report_timing             import report_timing
from ntsim.Propagators.Base.PropagatorBase import PropagatorBase
from ntsim.IO import gHits, gPhotons, gEvent

class SmartRayTracer(PropagatorBase):

    def configure(self, bboxes_depth, detectors_depth, effects, effects_options, effects_names):
        self.bboxes_depth = bboxes_depth
        self.detectors_depth = detectors_depth
        self.effects = effects
        self.effects_options = effects_options
        self.effects_names = effects_names
    
    @report_timing
    def propagate(self, photons:gPhotons) -> gHits:
        hits_list = ray_tracer(photons.pos_m, 
                               photons.t_ns, 
                               photons.wl_nm, 
                               photons.weight,
                               photons.ta_ns,
                               self.bboxes_depth,
                               self.detectors_depth,
                               self.effects,
                               self.effects_options)

        if len (hits_list):
            uid, t_ns, x, y, z, photon_id, *metadata_values, phe = np.array(hits_list).T
            photon_id= np.asarray(photon_id, dtype=int)
            #get the progenitor tracks for these hits
            track_uid = photons.track_uid[photon_id]
            #initialize the hits object
            hits = gHits(size=len(uid), uid=uid, t_ns=t_ns, phe=phe, track_uid=track_uid)
            #update the metadata
            metadata_names = ['w_noabs','self_weight',*self.effects_names]
            hits.metadata.update(dict(zip(metadata_names, metadata_values)))
            #return the hits
            return hits