import numpy as np

from ntsim.Triggers.Base.ElectronicsAndTriggerConditionsBase import ElectronicsAndTriggerConditionsBase
from ntsim.IO.gHits import gHits
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass

@dataclass
class BGVDElectronics(ElectronicsAndTriggerConditionsBase):
    """ A BGVDElectronics allows for the simulation of realistic detector behaviour. 
        It implements electron transit time with it's spread and Poisson sampling to incoming hits.
        It makes realistic pulse shape output described by Gumbel's function."""
    
    tts_params:tuple = (62, 3.4)
    pulse_duration_time_ns:int = 100
    discretization_time_ns:int = 5
    n_moving_average:int = 4
    n_process:int = 1

    def __post_init__(self):
       #call the constructor of the base class
       super().__init__("BGVDElectronics")

    def default_func(self, hits: gHits):
        """Default Function must return Hits object with another label. It is always on with BGVDElectronics"""
        hits_data = np.sort(hits.data, order='uid')
        return gHits(size=len(hits_data),
                     uid=hits_data['uid'],
                     phe=hits_data['phe'],
                     t_ns=hits_data['t_ns'])
    
    def transit_time_spread_func(self, hits: gHits):
        """Adds electron transit time distributed according to Normal Distribution with transit time spread as scale"""
        hits_data = np.sort(hits.data, order='uid')
        mu = self.tts_params[0]
        sigma = np.abs(self.tts_params[1] / 2*np.sqrt(2*np.log(2)))
        time_hits = hits_data['t_ns']
        n_hits = np.size(time_hits)
        #TODO: use standard RNG here!
        t_norm_ns = np.random.default_rng().normal(loc=mu, scale=sigma, size=n_hits)
        t_norm_ns = np.where(t_norm_ns < 0, 0, t_norm_ns) # replacing t < 0 with 0
        time_hits += t_norm_ns
        return  gHits(size=len(hits_data),
                      uid=hits_data['uid'],
                      phe=hits_data['phe'],
                      t_ns=time_hits)
     
    def poisson_sampling_func(self, hits: gHits):
        """Makes phe sampling according to Poisson Distribution"""
        hits_data = np.sort(hits.data, order='uid')
        phe_hits = hits_data['phe']
        n_hits = np.size(phe_hits)
        phe_hits = np.random.default_rng().poisson(lam=phe_hits, size=n_hits)
        nonzero_mask = phe_hits > 0
        
        return gHits(size=len(hits_data[nonzero_mask]),
                     uid=hits_data['uid'][nonzero_mask],
                     t_ns=hits_data['t_ns'][nonzero_mask],
                     phe=phe_hits[nonzero_mask])

    def gumbel_pusle_shape(self, data):
        """Applies Gumbel function for amplitude-time pulse shape. Adds moving average to points as well """
        dt = self.pulse_duration_time_ns 
        ds = self.discretization_time_ns
        nma = self.n_moving_average
        
        def modified_gumbel_pdf(x, s, a):
            """ original f(x) = 1 / beta * exp(-(z + exp(-z))), z = (x - s)/beta; max[f(x)] = 1/(beta * e)
                modified f(x) = a * exp(1 - (z + exp(-z))), z = (x - s)/beta; max[f(x)] = a """
            beta = 2.198 * 5
            z = (x - s) / beta
            return a * np.exp(1 - (z + np.exp(-z))) 
        
        def moving_average(y, n):
            """Returns moving average value"""
            y_m = np.zeros(np.size(y))
            for i in range(np.size(y)):
                y_m[i] += np.mean(y[i:i+n])
            return y_m
        
        data = np.sort(data, order='t_ns')
        mu = data['phe']
        sigma = 0.35 * np.sqrt(mu)
        a = np.random.default_rng().normal(loc=mu, scale=sigma, size=np.size(mu))
        uid = data['uid'][0]
        times = np.empty(0)
        phes = np.empty(0)
        ind = (np.argwhere(np.diff(data['t_ns']) > dt))[:,0] + 1
        ind = np.append(0, ind)
        for k in range(np.size(ind)): # goes by pulses
            i_s = ind[k]
            i_e = None # for last index
            if k != np.size(ind) - 1: i_e = ind[k+1] # for all indexes except last

            s = data[i_s:i_e]['t_ns']
            a1 = a[i_s:i_e]
            time_left = np.min(s)
            time_right = np.max(s)
            t = np.arange(time_left - dt/2, time_right + dt/2 + ds, ds)
            tphe = np.zeros(np.size(t))
 
            for i in range(np.size(t)): tphe[i] += np.sum(modified_gumbel_pdf(t[i], s, a1))

            # moving average
            phe = moving_average(tphe, nma)
            phes = np.append(phes, phe)
            times = np.append(times, t)

        uids = np.repeat(uid, np.size(phes))
        return 18*phes, times, uids # 18 is const converting phe -> ADC 
    
    def pulse_shape_func(self, hits: gHits):
        """Applies Gumbel function for amplitude-time pulse and delta-like signal. Adds moving average method as well"""
        hits_out = self.apply_multiprocessing(hits, self.gumbel_pusle_shape)
        return hits_out

    def apply_multiprocessing(self, hits: gHits, mpfunction):
        """Applies multiprocessing for function"""
        hits_out = []
        hits_data = np.sort(hits.data, order='uid')

        if self.n_process != 1:
            ##_________________________________MULTIPROCESSING_________________________________
            split_indices = np.where(np.diff(hits_data['uid']) != 0)[0] + 1
            split_hits_data = np.split(hits_data, split_indices)
                        
            with ProcessPoolExecutor(max_workers=self.n_process) as pool:
                ptu = np.array(pool.map(mpfunction, split_hits_data), dtype=object)
                phe = np.concatenate(ptu[:,0])
                t = np.concatenate(ptu[:,1])
                uid = np.concatenate(ptu[:,2])
                hits_out.append(
                    gHits(size=len(uid), 
                          uid=uid,t_ns=t,phe=phe)
                )
        else:
            ##____________________________________STRAIGHT_____________________________________
            for uid in (np.unique(hits_data['uid'])):
                uid_ind     = np.argwhere(hits_data['uid'] == uid)[:,0]    
                chosen_hits = hits_data[uid_ind] # get hits in selected OM
                phe, t, uids = mpfunction(chosen_hits)
                if len(uids) == 0 : continue
                hits_out.append(
                    gHits(size=len(uids),
                          uid=uids,t_ns=t,phe=phe)
                )
            
        return gHits.concatenate(hits_out)

    def set_functions(self):
        self.add_function(function=self.default_func)
        self.add_function(function=self.transit_time_spread_func)
        self.add_function(function=self.poisson_sampling_func)
        self.add_function(function=self.pulse_shape_func)