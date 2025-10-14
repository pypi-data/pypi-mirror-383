from numba import njit, types, prange

from ntsim.utils.report_timing import report_timing
from ntsim.Propagators.Base.PropagatorBase import PropagatorBase
from ntsim.IO import gPhotons
import numpy as np

@njit(types.containers.Tuple([types.float64[:,:],types.float64[:]])(types.float64[:,:],types.float64[:,:],types.float64[:],types.float64[:]),parallel=False,cache=True)
def random_trajectory_step(r0,omega0,ts,light_velocity_medium):
    n_photons = len(ts)
    r_out = np.empty(shape=(n_photons,3))
    t_out = np.empty(shape=n_photons)
    
    for i_pht in prange(n_photons):
        t = np.random.exponential(scale=ts[i_pht])
        
        dx = omega0[i_pht,0] * t * light_velocity_medium[i_pht]
        dy = omega0[i_pht,1] * t * light_velocity_medium[i_pht]
        dz = omega0[i_pht,2] * t * light_velocity_medium[i_pht]
        
        r_out[i_pht,0] = r0[i_pht,0] + dx
        r_out[i_pht,1] = r0[i_pht,1] + dy
        r_out[i_pht,2] = r0[i_pht,2] + dz
        
        t_out[i_pht] = t
        
    return r_out, t_out

class MCPhotonPropagator(PropagatorBase):
    arg_dict = {
        'n_scatterings': {'type': int, 'default': 5, 'help': ''}
    }
    
    @report_timing
    def propagate(self, photons:gPhotons, medium_prop, medium_scat) -> gPhotons:
        mua, mus, refraction_index           = medium_prop.interpolate(photons.wl_nm)
        ta, ts, light_velocity_medium, t_tot = medium_prop.get_helpers(mua,mus,refraction_index)
        
        medium_scat.anisotropy = medium_prop.anisotropy
        self.logger.debug('processing photons of size %d with dtype %s',photons.size, photons._dtype)
        #create the object for containing photons with scattering steps
        photons = photons.expand_dimensions(n=self.n_scatterings, 
                                              expand_fields=['pos_m', 'direction', 't_ns'])
        for step in range(1,self.n_scatterings):
            #set the next step
            photons.pos_m[:,step], t_step = random_trajectory_step(photons.pos_m[:,step-1],
                                                                     photons.direction[:,step-1],
                                                                     ts,
                                                                     light_velocity_medium)
            photons.t_ns[:,step] = photons.t_ns[:,step-1] + t_step
            photons.direction[:,step] = medium_scat.random_direction(photons.direction[:,step-1])
        
        photons.ta_ns = ta
        photons.metadata['ts_ns'] = ts
        self.logger.debug('created photons of size %d with dtype %s',photons.size, photons._dtype)
        return photons