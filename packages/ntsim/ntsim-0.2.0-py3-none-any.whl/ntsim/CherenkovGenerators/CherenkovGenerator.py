import numpy as np
import scipy as sp
from ntsim.random import rng

import ntsim.utils.systemofunits as units

from ntsim.utils.pdg_constants import *

from ntsim.IO.gParticles import gParticles
from ntsim.IO.gPhotons import gPhotons 
from ntsim.IO.gTracks import gTracks
from ntsim.IO.gEvent import gEvent

from ntsim.utils.gen_utils import sample_cherenkov_photon_directions
#from ntsim.utils.gen_utils import generate_cherenkov_spectrum
from ntsim.utils.report_timing import report_timing

#from ntsim.CherenkovGenerators.cher_utils import sample_cherenkov_photon_directions_n
from ntsim.CherenkovGenerators.cher_utils import *

from ntsim.utils.gen_utils import rotate_photons as pre_rotate_photons
from ntsim.utils.gen_utils import generate_cherenkov_spectrum

from ntsim.CherenkovGenerators.Base.CherenkovBase import CherenkovBase

from time import time

def segment_positions(charged_vertex_uid_1,charged_vertex_uid_2):
        delta_pos_uid = delta_pos(charged_vertex_uid_1,charged_vertex_uid_2)
        return delta_pos_uid

class CherenkovGenerator(CherenkovBase):
    arg_dict = {
        'photon_suppression': {'type': int, 'default': 1000, 'help': ''},
        'cherenkov_wavelengths_nm': {'type': float, 'nargs': 2, 'default': [350,610], 'help': ''},
        'mean_refraction_index': {'type': float, 'default': 1.34, 'help': ''},
        'photons_in_bunch': {'type': int, 'default': 1000000, 'help': ''},
        'energy_edge': {'type': float, 'default': 100, 'help': ''},
        'parameterization': {'type': str, 'choices': ['Gamma', 'Greisen'], 'default': 'Greisen', 'help': ''},
        'generate_in_cylinder': {'action': 'store_true', 'help': ''},
        'cylinder_position_m': {'type': float, 'nargs': 3, 'default': [0.,0.,0.], 'help': ''},
        'cylinder_dimensions': {'type': float, 'nargs': 2, 'default': [1000,1360], 'help': ''}
    }
    
    @report_timing
    def cherenkov_tracks(self, tracks: gTracks):
        
        if len(tracks)==0:
            self.logger.warning("No tracks!")
            return 0,np.zeros(shape=(1,0,3)),np.zeros(shape=(1,0)),np.zeros(shape=(1,0,3)),np.zeros(shape=(0)),np.zeros(shape=(0))
        
        ph_fraction    = 1./self.photon_suppression
        wavelength_min = self.cherenkov_wavelengths_nm[0]
        wavelength_max = self.cherenkov_wavelengths_nm[1]
        
        vertex = tracks.pos_m
        mask_water = vertex[:,2] >= 0.
        
        tracks_mod = tracks[mask_water]
        
        if not any(mask_water):
            return 0,np.zeros(shape=(0,3)),np.zeros(shape=(0)),np.zeros(shape=(0,3)),np.zeros(shape=(0)),np.zeros(shape=(0))
        
        vertex = tracks_mod.pos_m
        uid    = tracks_mod.uid
        pdgid  = tracks_mod.pdgid
        t      = tracks_mod.t_ns
        energy = tracks_mod.Etot_GeV
        length = tracks_mod.step_length_m
        
        if self.generate_in_cylinder:
            mask_r = np.sqrt((vertex[:,0]-self.cylinder_position_m[0])**2+
                             (vertex[:,1]-self.cylinder_position_m[1])**2) <= self.cylinder_dimensions[0]
            mask_h = vertex[:,2] <= self.cylinder_dimensions[1]
            
            mask_in_cylinder = mask_r & mask_h
            
            if not any(mask_in_cylinder):
                return 0,np.zeros(shape=(0,3)),np.zeros(shape=(0)),np.zeros(shape=(0,3)),np.zeros(shape=(0)),np.zeros(shape=(0))
        
            vertex = vertex[mask_in_cylinder]
            uid    = uid[mask_in_cylinder]
            pdgid  = pdgid[mask_in_cylinder]
            t      = t[mask_in_cylinder]
            energy = energy[mask_in_cylinder]
            length = length[mask_in_cylinder]
        
        charged_mask, masses = data_from_pdg(pdgid)
        charged_uid          = uid[charged_mask]
        charged_uid_mask     = charged_uid[:-1] == charged_uid[1:]
        
        charged_time   = t[charged_mask]
        charged_pdgid  = pdgid[charged_mask]
        charged_vertex = vertex[charged_mask]
        charged_energy = energy[charged_mask]
        
        charged_uid_selected    = charged_uid[:-1][charged_uid_mask]
        charged_vertex_uid_1 = charged_vertex[:-1][charged_uid_mask]
        charged_vertex_uid_2 = charged_vertex[1:][charged_uid_mask]
        charged_time_uid_1   = charged_time[:-1][charged_uid_mask]
        charged_time_uid_2   = charged_time[1:][charged_uid_mask]
        charged_masses_uid   = masses[:-1][charged_uid_mask]
        mean_charged_energy  = (charged_energy[:-1][charged_uid_mask]+charged_energy[1:][charged_uid_mask])*0.5
        
        delta_pos_uid = delta_pos(charged_vertex_uid_1,charged_vertex_uid_2)
    #    pos_segments  = distance_pos(charged_vertex_uid_1,charged_vertex_uid_2)
        time_segments = distance_time(charged_time_uid_1,charged_time_uid_2)
        pos_segments  = length[charged_mask][1:][charged_uid_mask]
        
        sin2_th       = get_sin2th(mean_charged_energy,charged_masses_uid,self.mean_refraction_index)
        n_per_cm_mean = Frank_Tamm_formula(sin2_th,wavelength_min,wavelength_max)
        seg_cher_phts = rng.poisson(n_per_cm_mean*pos_segments*ph_fraction*(units.m/units.cm))
        tot_cher_phts = np.sum(seg_cher_phts)
        
        if tot_cher_phts == 0:
            return tot_cher_phts,np.zeros(shape=(0,3)),np.zeros(shape=(0)),np.zeros(shape=(0,3)),np.zeros(shape=(0)),np.zeros(shape=(0))
        
        ph_pos, ph_t, progenitor, seg_dir = photon_quantities(charged_vertex_uid_1,
                                                              delta_pos_uid,
                                                              charged_time_uid_1,
                                                              time_segments,
                                                              charged_uid_selected,
                                                              seg_cher_phts,
                                                              tot_cher_phts)
        
        ph_dir        = sample_cherenkov_photon_directions_n(sin2_th,seg_cher_phts,tot_cher_phts)
        #ph_dir        = sample_cherenkov_photon_directions(tot_cher_phts, self.mean_refraction_index)
        ph_dir        = rotate_photons(seg_dir,ph_dir)
        ph_wavelength = generate_cherenkov_spectrum_n(wavelength_min,wavelength_max,tot_cher_phts)
        #override progenitor: just store track ID
        
#        ph_pos = np.expand_dims(ph_pos,axis=1)
#        ph_dir = np.expand_dims(ph_dir,axis=1)
#        ph_t   = np.expand_dims(ph_t,axis=1)
        
        return tot_cher_phts,ph_pos,ph_t,ph_dir,ph_wavelength,progenitor
    
    def configure_parameters(self):
        
        self.params_NKG_a_b_sum_mu_a = 0.8981172413412156
        self.params_NKG_a_b_sum_mu_b = -8.2058066069328
        self.params_NKG_a_b_sum_sigma_a = 0.0753458299773126
        self.params_NKG_a_b_sum_sigma_b = 4.70492059094909

        self.params_NKG_a_max_sum_mu_a = 0.8970836740142546
        self.params_NKG_a_max_sum_mu_b = 1.0367973288295156
        self.params_NKG_a_max_sum_sigma_a = 0.012646113843874273
        self.params_NKG_a_max_sum_sigma_b = 0.6554602053475697

        self.params_NKG_b_max_sum_mu_a = 24.23905516113146
        self.params_NKG_b_max_sum_mu_b = -82.79163784279021
        self.params_NKG_b_max_sum_mu_n = 29.92182783141866
        self.params_NKG_b_max_sum_sigma_a = 3.4300832858261705
        self.params_NKG_b_max_sum_sigma_b = -10.673135257009374
        self.params_NKG_b_max_sum_sigma_c = 0.008919724522696335

        self.params_cor_a_b_a = -0.00039439073731101226
        self.params_cor_a_b_b = -0.9889032621863614
        self.params_cor_a_max_a = 0.05404799344583355
        self.params_cor_a_max_b = 1.6753832533827284
        self.params_cor_b_max_a = 4.258076390393444
        self.params_cor_b_max_b = -15.289070045704687
        self.params_cor_b_max_c = -0.8687092191715677
        
        self.coef = np.array([[1,8,0],[1,0,1],[0,1,1]])
        
        self.amount_photons_a = 130655.3
        self.amount_photons_b = -14470
        
        self.costh_values, self.costh_prob = gen_costh_prob(self.mean_refraction_index)
        
        self.light_velocity_vacuum_medium = units.light_velocity_vacuum/self.mean_refraction_index
    
    @report_timing
    def cherenkov_cascades(self, cascade_starters: gParticles):
    
        ph_fraction    = 1./self.photon_suppression
        wavelength_min = self.cherenkov_wavelengths_nm[0]
        wavelength_max = self.cherenkov_wavelengths_nm[1]
        
        self.configure_parameters()
        
        cascade_starters_data = cascade_starters.data
        
        position_m = cascade_starters_data['pos_m']
        mask_water = position_m[:,2] >= 0.
        
        cascade_starters_data_mod = cascade_starters_data[mask_water]
        
        position_m = cascade_starters_data_mod['pos_m']
        uid        = cascade_starters_data_mod['uid']
        time_ns    = cascade_starters_data_mod['t_ns']
        direction  = cascade_starters_data_mod['direction']
        energy_GeV = cascade_starters_data_mod['Etot_GeV']
        
        if self.generate_in_cylinder:
            mask_r = np.sqrt((position_m[:,0]-self.cylinder_position_m[0])**2+
                             (position_m[:,1]-self.cylinder_position_m[1])**2) <= self.cylinder_dimensions[0]
            mask_h = position_m[:,2] <= self.cylinder_dimensions[1]
            
            mask_in_cylinder = mask_r & mask_h
            
            if not any(mask_in_cylinder):
                return 0,np.zeros(shape=(0,3)),np.zeros(shape=(0)),np.zeros(shape=(0,3)),np.zeros(shape=(0)),np.zeros(shape=(0))
        
            position_m = position_m[mask_in_cylinder]
            uid        = uid[mask_in_cylinder]
            time_ns    = time_ns[mask_in_cylinder]
            direction  = direction[mask_in_cylinder]
            energy_GeV = energy_GeV[mask_in_cylinder]
        
        ene_mask = energy_GeV >= self.energy_edge
        
        total_amount_photons = 0
        n_photons = 0
        photon_positions_m_low = np.zeros(shape=(0,3))
        photon_positions_m_up  = np.zeros(shape=(0,3))
        ph_time_low = np.zeros(shape=(0))
        ph_time_up  = np.zeros(shape=(0))
        ph_dir_low = np.zeros(shape=(0,3))
        ph_dir_up  = np.zeros(shape=(0,3))
        ph_wavelength_low = np.zeros(shape=(0))
        ph_wavelength_up  = np.zeros(shape=(0))
        progenitor_low = np.zeros(shape=(0))
        progenitor_up  = np.zeros(shape=(0))
        
        position_m_up = position_m[ene_mask]
        uid_up        = uid[ene_mask]
        time_ns_up    = time_ns[ene_mask]
        direction_up  = direction[ene_mask]
        energy_GeV_up = energy_GeV[ene_mask]
        n_cascades_up = len(energy_GeV_up)
        
        if n_cascades_up:
            
            gamma_1 = rng.normal(size=n_cascades_up)
            gamma_2 = rng.normal(size=n_cascades_up)
            gamma_3 = rng.normal(size=n_cascades_up)
            gamma_z = np.expand_dims(np.array([gamma_1,gamma_2,gamma_3]).T,axis=2)
            
            y = energy_GeV_up/Ec_ele_GeV
            
            params_NKG_a_b_sum_sample_mu      = line(y,      self.params_NKG_a_b_sum_mu_a,      self.params_NKG_a_b_sum_mu_b)
            params_NKG_a_b_sum_sample_sigma   = line(y,      self.params_NKG_a_b_sum_sigma_a,   self.params_NKG_a_b_sum_sigma_b)
            params_NKG_a_max_sum_sample_mu    = line(y,      self.params_NKG_a_max_sum_mu_a,    self.params_NKG_a_max_sum_mu_b)
            params_NKG_a_max_sum_sample_sigma = line(y,      self.params_NKG_a_max_sum_sigma_a, self.params_NKG_a_max_sum_sigma_b)
            params_NKG_b_max_sum_sample_mu    = logn_line(y, self.params_NKG_b_max_sum_mu_a,    self.params_NKG_b_max_sum_mu_b,    self.params_NKG_b_max_sum_mu_n)
            params_NKG_b_max_sum_sample_sigma = inv_line(y,  self.params_NKG_b_max_sum_sigma_a, self.params_NKG_b_max_sum_sigma_b, self.params_NKG_b_max_sum_sigma_c)
            
            cor_a_b   = line(y,     self.params_cor_a_b_a,   self.params_cor_a_b_b)
            cor_a_max = ln_line(y,  self.params_cor_a_max_a, self.params_cor_a_max_b)
            cor_b_max = inv_line(y, self.params_cor_b_max_a, self.params_cor_b_max_b, self.params_cor_b_max_c)
            
            par_mu = np.array([params_NKG_a_b_sum_sample_mu,params_NKG_a_max_sum_sample_mu,params_NKG_b_max_sum_sample_mu]).T
            par_mu = np.expand_dims(par_mu, axis=2)
            
            cov_matr = np.array([params_NKG_a_b_sum_sample_sigma,params_NKG_a_max_sum_sample_sigma,params_NKG_b_max_sum_sample_sigma])[:,None]*\
                    np.array([params_NKG_a_b_sum_sample_sigma,params_NKG_a_max_sum_sample_sigma,params_NKG_b_max_sum_sample_sigma])[None,:]
            
            cov_matr = np.array([cov_matr[:,:,p] for p in range(n_cascades_up)])

            cov_matr[:,0,1] *= cor_a_b
            cov_matr[:,0,2] *= cor_a_max
            cov_matr[:,1,2] *= cor_b_max
            cov_matr[:,1,0] *= cor_a_b
            cov_matr[:,2,0] *= cor_a_max
            cov_matr[:,2,1] *= cor_b_max
            
            L = np.linalg.cholesky(cov_matr)

            data_init = par_mu+np.matmul(L,gamma_z)
            data_init[:,2] = np.exp(data_init[:,2]**2)
            
            params_NKG = np.linalg.solve(self.coef, data_init)
            
            data_NKG_a = np.exp(params_NKG[:,0])
            data_NKG_b = params_NKG[:,1]
            data_NKG_m = params_NKG[:,2]
            
            x_data = np.linspace(0,35,10000)
            x_diff = np.diff(x_data)[0]
            
            NKG = NKG_adv(x_data, data_NKG_a, data_NKG_b, data_NKG_m)
            
            tot_NKG = np.sum(NKG, axis=1)
            
            p_NKG = NKG/np.transpose([tot_NKG])
            
            mean_photons = self.amount_photons_a*energy_GeV_up+self.amount_photons_b
            amount_photons = rng.poisson(lam=mean_photons*ph_fraction)
            total_amount_photons = np.sum(amount_photons)
            
            photon_positions_m  = np.zeros(shape=(total_amount_photons,3), dtype=float)
            
            cascace_positions_m = np.repeat(position_m_up, amount_photons, axis=0)
            cascace_directions  = np.repeat(direction_up, amount_photons, axis=0)
            cascade_times_ns    = np.repeat(time_ns_up, amount_photons)
            
            pht_t = random_choice(x_data, amount_photons, p_NKG)
            pht_t = pht_t+rng.uniform(-x_diff,x_diff,total_amount_photons)
            photon_positions_m[:,2] = pht_t*X0
            
            ph_time_up = cascade_times_ns+photon_positions_m[:,2]/self.light_velocity_vacuum_medium
            
            photon_positions_m_up = rotate_photons(cascace_directions,photon_positions_m)
            photon_positions_m_up += cascace_positions_m
            
            ph_dir = sample_photon_directions(total_amount_photons, self.costh_values, self.costh_prob)
            ph_dir_up = rotate_photons(cascace_directions, ph_dir)
            
            ph_wavelength_up = generate_cherenkov_spectrum_n(wavelength_min,wavelength_max,total_amount_photons)
            
#            photon_positions_m_up = np.expand_dims(photon_positions_m, axis=1)
#            ph_dir_up             = np.expand_dims(ph_dir, axis=1)
#            ph_time_up            = np.expand_dims(ph_time, axis=1)
            progenitor_up = np.repeat(uid_up, amount_photons)
        
        position_m_low = position_m[~ene_mask]
        uid_low        = uid[~ene_mask]
        time_ns_low    = time_ns[~ene_mask]
        direction_low  = direction[~ene_mask]
        energy_GeV_low = energy_GeV[~ene_mask]
        n_cascades_low = len(energy_GeV_low)
        
        if n_cascades_low:
            
            par_tmax_a = 2.00
            par_tmax_b = 0.98
            par_q_const = 4.13
            
            casc_n_photons = rng.poisson(1.18e5*energy_GeV_low*ph_fraction)
            # TODO: check it has Poisson distribution
            casc_q_central_e = np.ones_like(energy_GeV_low) * par_q_const
            casc_tmax_central_e = par_tmax_a + par_tmax_b * np.log(energy_GeV_low)
        
            casc_q = casc_q_central_e
            casc_tmax = casc_tmax_central_e
            casc_gamma_k = casc_q + 1
            casc_gamma_theta = casc_tmax / (casc_q + 1)
            casc_gamma_theta[casc_gamma_theta<0] = 0.
            #
            n_photons = casc_n_photons.sum()
            #
            ph_pos = np.zeros((n_photons,3))
            ph_gamma_k = np.repeat(casc_gamma_k, casc_n_photons)
            ph_gamma_theta = np.repeat(casc_gamma_theta, casc_n_photons)
            ph_t = rng.gamma(shape=ph_gamma_k, scale=ph_gamma_theta, size=n_photons)
            ph_pos[:,2] += ph_t*X0
            
            cascace_positions_m = np.repeat(position_m_low, casc_n_photons, axis=0)
            cascace_directions  = np.repeat(direction_low, casc_n_photons, axis=0)
            cascade_times_ns    = np.repeat(time_ns_low, casc_n_photons)
            
            ph_time_low = cascade_times_ns+ph_pos[:,2]/self.light_velocity_vacuum_medium
            
            photon_positions_m_low = rotate_photons(cascace_directions,ph_pos)
            photon_positions_m_low += cascace_positions_m
            
            ph_dir = sample_photon_directions(n_photons, self.costh_values, self.costh_prob)
            ph_dir_low = rotate_photons(cascace_directions, ph_dir)
            
            ph_wavelength_low = generate_cherenkov_spectrum_n(wavelength_min,wavelength_max,n_photons)
            
#            photon_positions_m_low = np.expand_dims(photon_positions_m, axis=1)
#            ph_dir_low             = np.expand_dims(ph_dir, axis=1)
#            ph_time_low            = np.expand_dims(ph_time, axis=1)
            progenitor_low = np.repeat(uid_low, casc_n_photons)
        
        total_amount_photons = total_amount_photons+n_photons
        photon_positions_m = np.concatenate((photon_positions_m_low,photon_positions_m_up),axis=0)
        ph_time = np.concatenate((ph_time_low,ph_time_up),axis=0)
        ph_dir = np.concatenate((ph_dir_low,ph_dir_up),axis=0)
        ph_wavelength = np.concatenate((ph_wavelength_low,ph_wavelength_up))
        progenitor = np.concatenate((progenitor_low,progenitor_up))
        
        return total_amount_photons,photon_positions_m,ph_time,ph_dir,ph_wavelength,progenitor
    
    def cherenkov_bunches(self, event: gEvent, data, generator, label: str) -> None:
        n_ph_steps = 1
        
        tot_cher_phts,ph_pos,ph_t,ph_dir,ph_wavelength,progenitor = generator(data)
        n_bunches, bunch_bounds = count_bunches(tot_cher_phts, self.photons_in_bunch)

        all_photons = []
        for bunch in range(n_bunches):
            if not tot_cher_phts: break
            
            bound_min = bunch_bounds[bunch]
            bound_max = bunch_bounds[bunch+1]
            
            tot_cher_phts_bunch = bunch_bounds[bunch+1]-bunch_bounds[bunch]
            ph_pos_bunch        = ph_pos[bound_min:bound_max]
            ph_t_bunch          = ph_t[bound_min:bound_max]
            ph_dir_bunch        = ph_dir[bound_min:bound_max]
            ph_wavelength_bunch = ph_wavelength[bound_min:bound_max]
            progenitor_bunch    = progenitor[bound_min:bound_max]
            #create the photons object
            photons = gPhotons(size=len(ph_wavelength_bunch),
                               pos_m=ph_pos_bunch,
                               t_ns=ph_t_bunch,
                               direction=ph_dir_bunch,
                               wl_nm=ph_wavelength_bunch,
                               weight=self.photon_suppression,
                               ta_ns=0,
                               track_uid=progenitor_bunch
                              )
            all_photons+=[photons]
        #store all photons in the event
        event.photons[label] = all_photons
        
    @report_timing
    def generate(self, event: gEvent):
        
        for n_tracks, tracks in enumerate(event.tracks.values()):
            if len(tracks) != 0:
                self.cherenkov_bunches(event, tracks, self.cherenkov_tracks, f'CherenkovTracks{n_tracks}')
        
        for n_particles, particles in enumerate(event.particles.values()):
            if len(particles) != 0 and particles.gen_cher:
                self.cherenkov_bunches(event, particles, self.cherenkov_cascades, f'CherenkovCascades{n_particles}')