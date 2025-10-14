import numpy as np
import itertools
from ntsim.CloneGenerators.Base.CloneBase import CloneBase
from ntsim.IO.gPhotons import gPhotons
from ntsim.IO.gHits import gHits
from ntsim.utils.gen_utils import make_random_position_shifts
from ntsim.utils.report_timing import report_timing

class CloneGenerator(CloneBase):
    arg_dict = {
        'n_clones': {'type': int, 'default': 1, 'help': 'amount of clones'},
        'set_position':{'action': 'store_true', 'help': 'set center of cloning cylinder'},
        'position_m': {'type': float, 'nargs': 3, 'default': [0.,0.,0.], 'help': 'center of cloning cylinder'},
        'dimensions_m': {'type': float, 'nargs': 2, 'default': [10., 0.], 'help': 'radius and height of cloning cylinder'},
        'accumulate_hits': {'action':'store_true', 'help': 'accumulation hits trigger'},
        'clone_event_id': {'type': int, 'default': -1, 'help': 'id of event to clone (must be less than total amount of events)'}
    }
    
    def configure(self, opts):
        super().configure(opts)
        
        self.cloner_hits = []
        self.cloner_hits_total = [gHits(f'ClonerHits_total')]
        self.running_clone_id = 0
        for clone_id in range(self.n_clones):
            self.cloner_hits.append(gHits(f'ClonerHits_{clone_id}'))
    
    def make_clones_shifts(self):
        cloner_shifts = make_random_position_shifts(self.dimensions_m[0], self.dimensions_m[1], self.n_clones)
        return cloner_shifts
    
    def make_event_ids(self, n_events):
        if self.clone_event_id >=0:
            random_event_ids = np.full((self.n_clones,), self.clone_event_id)
        else:
            random_event_ids = np.random.randint(0, n_events, (self.n_clones,))
        return random_event_ids
    
    def make_center_shift(self, primary):
        if self.set_position:
            ind = np.isnan(self.position_m)
            if np.size(primary):
                cloner_center_shift = self.position_m - primary[-1].position_m
                cloner_center_shift[:,ind] = 0
                self.center_shift = cloner_center_shift
            else:
                self.center_shift = []

    @report_timing
    def calculate_cloner_hits(self, shifts, photons, detectors_depth, bboxes_depth, effects, effects_options, effects_names):
        from ntsim.Propagators.RayTracers.rt_utils import ray_tracer
        cloned_photons_gen = self.generate_cloned_photons(shifts, photons)
        q = self.running_clone_id - np.shape(shifts)[0]
        for clone_id, cloned_photons in enumerate(cloned_photons_gen):
            cloner_hits_list = ray_tracer(cloned_photons.position_m,cloned_photons.time_ns,cloned_photons.wavelength_nm,cloned_photons.weight,cloned_photons.absorption_time_ns,
                                              bboxes_depth,detectors_depth, effects, effects_options)
            if len(cloner_hits_list):
                hits_array = np.array(cloner_hits_list).T
                if self.accumulate_hits == False:
                    self.cloner_hits[q+clone_id].from_custom_array([hits_array[0],hits_array[1],hits_array[-1]],['om_uid','t_ns','phe'])
                else:
                   self.cloner_hits_total[0].from_custom_array([hits_array[0],hits_array[1],hits_array[-1]],['om_uid','t_ns','phe'])
        # print('acc',self.accumulate_hits)
        # print('hits\n', self.cloner_hits[q : q+np.shape(shifts)[0]], np.shape(self.cloner_hits[q : q+np.shape(shifts)[0]]))
        return self.cloner_hits[q : q+np.shape(shifts)[0]] , self.cloner_hits_total

    def generate_cloned_photons(self, shifts, original_photons):
        # if self.dimensions_m[0] !=0:
        #     original_photons.weight = original_photons.weight  * np.pi * (self.dimensions_m[0])**2 / (self.n_clones+1)
        # else:
        #     original_photons.weight = original_photons.weight / (self.n_clones+1)
        n_photons = original_photons.n_photons
        n_steps = original_photons.scattering_steps
        direction = original_photons.direction
        progenitor = original_photons.progenitor
        t_ns = original_photons.time_ns
        ta = original_photons.absorption_time_ns
        ts = original_photons.scattering_time_ns
        wavelength_nm = original_photons.wavelength_nm
        weight = original_photons.weight
        position_orig = original_photons.position_m
        # print('n_clones in event', n_clones)
        #for neutrino, checking photons birth place
        # print('photons__pos_orig\n', position_orig, np.shape(position_orig))  
        # print('\nphotons__pos_orig_z\n', position_orig[:,:,2], np.shape(position_orig[:,:,2]))
        # print('shifts\n', shifts, np.shape(shifts))
        # print('min\n',np.amin(position_orig[:,:,2]))
        # z0 = np.amin(position_orig[:,:,2]) + shifts[:,2]
        # print('zo\n', z0, np.shape(z0))
        # mask = (z0<0)
        # # print(mask)
        # shifts[mask,2] = 0
        # print('new shifts\n', shifts) 

        if self.set_position:
            if np.size(self.center_shift) == 0:
                ind = np.isnan(self.position_m)
                self.center_shift = self.position_m - position_orig[0,0]
                self.center_shift[ind] = 0
            position_orig = position_orig + self.center_shift

        for clone_id in range(np.shape(shifts)[0]):
            new_cloned_photons = gPhotons('cloned_photons')
            position_m = position_orig + shifts[clone_id]
            new_cloned_photons.from_custom_array([position_m,t_ns,direction,wavelength_nm,weight,ta].names)
            yield new_cloned_photons


    # def transform(self,r,shifts):
    #     if not self.position_m is None:
    #         dr = self.position_m - r[0,0]
    #         r = r + dr
    #     #print('r and shifts\n', np.shape(r), np.shape(shifts))
    #     r = np.expand_dims(r, axis=0)
    #     shifts = np.expand_dims(shifts, axis=1)
    #     shifts = np.expand_dims(shifts, axis=1)
    #     r = r + shifts
    #     return r