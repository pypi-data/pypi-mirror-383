import numpy as np

from ntsim.Triggers.Base.ElectronicsAndTriggerConditionsBase import ElectronicsAndTriggerConditionsBase
from ntsim.IO.gHits import gHits
from dataclasses import dataclass

@dataclass
class BGVDTriggerConditions(ElectronicsAndTriggerConditionsBase):
    """ BGVDTriggerConditions implements one cluster trigger condition on hits, which previously went through BGVDElectronics """
    
    time_window_ns:int = 100
    pulse_duration_time_ns:int = 100
    phe_limits:tuple = (1.7, 3.5)
    trigger_flag:bool = True
    
    def __post_init__(self):
        super().__init__("BGVDTriggerConditions")

    def default_trigger(self, hits: gHits)->gHits:
        """Default Trigger must return Hits object. It is always on with BGVDTriggerConditions"""
        hits_data = np.sort(hits.data, order='uid')
        return gHits.from_structarray(hits_data)
    
    def one_cluster_trigger(self, hits: gHits)->gHits:
        """This function checks if there are two neighbour OMs worked in one time window"""

        hits_data = np.sort(hits.data, order='uid')  
        hits_out_temp = []
        
        low_bound = self.phe_limits[0] * 18 # 18 is const for convertion phe -> ADC in BGVDElectronics
        high_bound = self.phe_limits[1] * 18
        pulse_duration = self.pulse_duration_time_ns
        time_window = self.time_window_ns

        for uid in np.unique(hits_data['uid'])[1:]: #starts with the 2nd element
            left_uid_ind  = np.argwhere(hits_data['uid'] == uid - 1)
            neighbour_hits = hits_data[left_uid_ind]
            if len(neighbour_hits) == 0: continue
            
            uid_ind       = np.argwhere(hits_data['uid'] == uid)
            chosen_hits   = hits_data[uid_ind]
            chosen_hits = np.sort(chosen_hits, order='t_ns')
            neighbour_hits = np.sort(neighbour_hits, order='t_ns')
            
            peak_ind = np.argwhere(np.diff(chosen_hits['t_ns']) > pulse_duration)[:,0] + 1
            peak_ind = np.append(0, peak_ind)

            add_peak_flag = False
            for k in range(np.size(peak_ind)): # goes by pulses in one OM
                i_s = peak_ind[k]
                i_e = None # for last index
                if k != np.size(peak_ind) - 1: i_e = peak_ind[k+1] # for all indexes except last
                chosen_hits_peak = chosen_hits[i_s:i_e]
                if np.max(chosen_hits_peak['phe']) < low_bound: continue
                
                indt = np.argwhere(chosen_hits_peak['phe'] > low_bound)[:,0]
                ct_s = chosen_hits_peak['t_ns'][indt][0]
                
                neighbour_peak_ind = np.argwhere(np.diff(neighbour_hits['t_ns']) > pulse_duration)[:,0] + 1
                neighbour_peak_ind = np.append(0, neighbour_peak_ind)
                for nk in range(np.size(neighbour_peak_ind)): # goes by pulses in one OM
                    ni_s = neighbour_peak_ind[nk]
                    ni_e = None
                    if nk != np.size(neighbour_peak_ind) - 1: ni_e = neighbour_peak_ind[nk+1]
                    neighbour_hits_peak = neighbour_hits[ni_s:ni_e]
                    
                    if np.max(neighbour_hits_peak['phe']) < low_bound: continue
                    if np.max(chosen_hits_peak['phe']) < high_bound and np.max(neighbour_hits_peak['phe']) < high_bound: continue 
                    
                    nindt = np.argwhere(neighbour_hits_peak['phe'] > low_bound)[:,0]
                    nt_s = neighbour_hits_peak['t_ns'][nindt][0]
                    
                    if np.abs(nt_s - ct_s) > time_window: continue
                    add_peak_flag = True

                    hits_out_temp.append(
                        gHits.from_structarray(neighbour_hits_peak)
                    )
                if add_peak_flag:
                    hits_out_temp.append(
                        gHits.from_structarray(chosen_hits_peak)
                    )
        #concatenate all accumulated hits
        hits_out = gHits.concatenate(hits_out_temp)
        #store only the unique hits 
        hits_out._data = np.unique(hits_out._data)
        return hits_out

    def set_functions(self):
        self.add_function(function=self.default_trigger)
        
        if self.trigger_flag:
            self.add_function(function=self.one_cluster_trigger)

