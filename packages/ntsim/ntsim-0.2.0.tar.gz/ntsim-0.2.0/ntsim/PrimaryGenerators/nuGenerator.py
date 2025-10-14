import numpy as np

from ntsim.utils.report_timing import report_timing
from particle import Particle
from numpy import pi as PI
from math import sqrt

import ntsim.Propagators.PrimaryPropagators.NeutrinoPropagator as nuprop
import ntsim.utils.systemofunits as units

from ntsim.PrimaryGenerators.Base.PrimaryGeneratorBase import PrimaryGeneratorBase
from ntsim.utils.gen_utils import resonance_decay
from ntsim.IO.gParticles import gParticles
from ntsim.IO.gTracks import gTracks
from ntsim.random import rng

import nupropagator.Global.systemofunits as sou
import nupropagator.Global.Global as g
import nupropagator.flux.Flux as flux

from nupropagator import nugen

class nuGenerator(PrimaryGeneratorBase):
    arg_dict = {
        'model': {'type': str, 'default': 'KM', 'help': 'flux model'},
        'flux_file': {'type': str, 'default': 'Numu_H3a+KM_E2.DAT', 'help': 'file with fluxes'},
        'flux_type': {'type': str, 'default': 'model_flux', 'help': 'flux event mode'},
        'energy_min': {'type': float, 'default': 10, 'help': 'minimal energy for flux'},
        'energy_max': {'type': float, 'default': 10**8, 'help': 'maximal energy for flux'},
        'cos_min': {'type': float, 'default': -1, 'help': 'minimal cos for flux'},
        'cos_max': {'type': float, 'default': 1, 'help': 'maximal cos for flux'},
        'phi_min': {'type': float, 'default': 0, 'help': 'minimal phi for flux'},
        'phi_max': {'type': float, 'default': 2*PI, 'help': 'maximal phi for flux'},
        'flux_indicator': {'type': float, 'default': 2.7, 'help': 'indicator for E**(-gamma) flux'},
        'N_event': {'type': int, 'default': 2000, 'help': 'Number of neutrino event'},
        'vegas_neval': {'type': int, 'default': 100, 'help': 'Number of vegas evaluation'},
        'position_m': {'type': float, 'nargs': 3, 'type': float, 'default': [0.,0.,0.], 'help': 'final vertex of neutrino'},
        'neutrinoPrimary_pdgid': {'type': int, 'default': 14, 'help': 'PDGID of neutrino'},
        'neutrinoPrimary_energy_mode': {'default': 'fixed', 'help': 'random or fixed'},
        'neutrinoPrimary_direction_mode': {'default': 'fixed', 'help': 'random or fixed'},
        'neutrinoPrimary_target_mode': {'default': 'random', 'help': 'random or fixed'},
        'neutrinoPrimary_current_mode': {'default': 'random', 'help': 'random or fixed'},
        'neutrinoPrimary_pdf_model': {'default': 'CT10nlo', 'help': 'LHAPDF model for nucleon'},
        'neutrinoPrimary_energy_GeV': {'type': float, 'default': 100, 'help': 'energy of neutrino in GeV'},
        'neutrinoPrimary_target': {'default': 'proton', 'help': 'proton/neutron'},
        'neutrinoPrimary_direction': {'nargs': '+', 'type': float, 'default': [0.,0.,1.], 'help': 'unit three vector for neutrino direction'},
        'n_bins': {'default': 100},
        'algo_xs': {'choices': ['vegas','ground'], 'default': 'ground'}
    }
    arg_dict.update(PrimaryGeneratorBase.arg_dict_position)

    @report_timing
    def make_event(self, event):
        
        gen = 0
        if self.neutrinoPrimary_current_mode in ('1', '-1'):
            self.neutrinoPrimary_current_mode = int(self.neutrinoPrimary_current_mode)
        self.generator = nugen.NuGen(self)
        
        #self.generator.get_event_fix_en(opts) #generate even with all information
        
        self.particles_init = gParticles("primary_init",to_propagate=False,gen_cher=False)
        self.particles_prop = gParticles("primary_prop",gen_cher=False)
        self.generator.get_event_fix_en(self) #generate even with all information
        iev = rng.integers(0,len(self.generator.dis.particles[0]['E_GeV'])-1)
        iev_f = self.generator.iev_f
        pdgid_nu = self.generator.nu_pdg
        Etot = self.generator.E_f[iev_f]
        cos = self.generator.cos_f[iev_f]
        phi = self.generator.phi_f[iev_f]
        sin = (1-cos**2)**0.5
        momentum_nu = self.create_momentum_nu(Etot,cos,phi)
        self.n = np.array([np.cos(phi)*sin,np.sin(phi)*sin,cos])
        if self.random_position:
            fposition, weight = self.set_random_position(1, self.random_volume)
            event.EventHeader.event_weight = weight[0]
        else:
            fposition = np.array(self.position_m)
        self.fvertex = fposition
        scalar = np.sum(self.fvertex*self.n)
        self.ivertex  = self.fvertex-self.n*(scalar+np.sqrt(scalar**2 - np.sum(self.fvertex**2)+g.R_E**2))
        time_i_nu = 0

        iposition = self.ivertex
        time_f_nu = np.sqrt(np.sum((fposition - iposition)**2))/sou.light_velocity_vacuum
        self.particles_init.from_custom_array([-1, pdgid_nu, iposition, time_i_nu, momentum_nu, Etot], gParticles.data_type.names)
        self.particles_init.from_custom_array([-1, pdgid_nu, fposition, time_f_nu, momentum_nu, Etot], gParticles.data_type.names)
        momentum_target = np.array([0,0,0])
        pdgid_1 = self.generator.dis.particles[0]['pdgid'][iev]
        pdgid_2 = self.generator.dis.particles[1]['pdgid'][iev]
        pdgid_target = self.generator.target
        momentum = np.zeros([2,4])
        for i in range(2):
            momentum[i][1] = self.generator.dis.particles[i]['Px_GeV'][iev]
            momentum[i][2] = self.generator.dis.particles[i]['Py_GeV'][iev]
            momentum[i][3] = self.generator.dis.particles[i]['Pz_GeV'][iev]
            momentum[i][0] = self.generator.dis.particles[i]['E_GeV'][iev]
        #tot_energy_1 = momentum[0][0]
        #tot_energy_2 = momentum[1][0]
        #momentum_1 = momentum[0][1:]
        #momentum_2 = momentum[1][1:]
        tot_energy_1 = momentum[0][0]
        tot_energy_2 = Etot - tot_energy_1 + sou.mass[pdgid_target]*units.MeV/units.GeV
        momentum_1 = momentum[0][1:]
        momentum_2 = momentum_nu - momentum_1
        
        self.particles_init.from_custom_array([0, pdgid_target, fposition, time_f_nu, momentum_target, sou.mass[pdgid_target]*units.MeV/units.GeV], gParticles.data_type.names)
        self.particles_prop.from_custom_array([0, pdgid_1, fposition, time_f_nu, momentum_1, tot_energy_1], gParticles.data_type.names)
        if pdgid_2 == 2224:
            momentum_pi, tot_energy_pi, momentum_p, tot_energy_p = resonance_decay(momentum_2, tot_energy_2, 211, 2212)
            self.particles_prop.from_custom_array([0, 211, fposition, time_f_nu, momentum_pi, tot_energy_pi], gParticles.data_type.names)
            self.particles_prop.from_custom_array([0, 2212, fposition, time_f_nu, momentum_p, tot_energy_p], gParticles.data_type.names)
        elif abs(pdgid_1) == 13 and pdgid_target == 2212 and pdgid_2 == 2214:
            momentum_pi, tot_energy_pi, momentum_p, tot_energy_p = resonance_decay(momentum_2, tot_energy_2, 111, 2112)
            self.particles_prop.from_custom_array([0, 111, fposition, time_f_nu, momentum_pi, tot_energy_pi], gParticles.data_type.names)
            self.particles_prop.from_custom_array([0, 2112, fposition, time_f_nu, momentum_p, tot_energy_p], gParticles.data_type.names)
        elif pdgid_target == 2112 and pdgid_2 == 2214:
            momentum_pi, tot_energy_pi, momentum_p, tot_energy_p = resonance_decay(momentum_2, tot_energy_2, 211, 2112)
            self.particles_prop.from_custom_array([0, 211, fposition, time_f_nu, momentum_pi, tot_energy_pi], gParticles.data_type.names)
            self.particles_prop.from_custom_array([0, 2112, fposition, time_f_nu, momentum_p, tot_energy_p], gParticles.data_type.names)
        elif pdgid_2 == 1114:
            momentum_pi, tot_energy_pi, momentum_p, tot_energy_p = resonance_decay(momentum_2, tot_energy_2, -211, 2112)
            self.particles_prop.from_custom_array([0, -211, fposition, time_f_nu, momentum_pi, tot_energy_pi], gParticles.data_type.names)
            self.particles_prop.from_custom_array([0, 2112, fposition, time_f_nu, momentum_p, tot_energy_p], gParticles.data_type.names)
        elif pdgid_target == 2212 and pdgid_2 == 2214:
            momentum_pi, tot_energy_pi, momentum_p, tot_energy_p = resonance_decay(momentum_2, tot_energy_2, 211, 2112)
            self.particles_prop.from_custom_array([0, 211, fposition, time_f_nu, momentum_pi, tot_energy_pi], gParticles.data_type.names)
            self.particles_prop.from_custom_array([0, 2112, fposition, time_f_nu, momentum_p, tot_energy_p], gParticles.data_type.names)
        elif pdgid_2 == 2114:
            momentum_pi, tot_energy_pi, momentum_p, tot_energy_p = resonance_decay(momentum_2, tot_energy_2, 111, 2112)
            self.particles_prop.from_custom_array([0, 111, fposition, time_f_nu, momentum_pi, tot_energy_pi], gParticles.data_type.names)
            self.particles_prop.from_custom_array([0, 2112, fposition, time_f_nu, momentum_p, tot_energy_p], gParticles.data_type.names)
            
            
#        if pdgid_2 != 2224:
#            self.particles.add_particle(1, pdgid_2, *fposition, time_f_nu, *momentum_2, tot_energy_2)
#        else:
#            momentum_pi, tot_energy_pi, momentum_p, tot_energy_p = resonance_decay(momentum_2, tot_energy_2)
#            self.particles.add_particle(1, 211, *fposition, time_f_nu, *momentum_pi, tot_energy_pi)
#            self.particles.add_particle(1, 2212, *fposition, time_f_nu, *momentum_p, tot_energy_p)
        event.particles = self.particles
        
        from nupropagator import NuPropagator 
        self.propagator = NuPropagator.NuPropagator(self)
        self.propagator.prepare_propagation()

        tracks = gTracks("nu_tracks", gen_cher=False)
        ev = event.particles[0].get_named_data()[0]
#        self.info = self.propagator.get_dragging()
        info = [0,ev['pdgid'],[ev['x_m'],ev['y_m'],ev['z_m']],ev['time_ns'],ev['E_tot_GeV'],0.]
        tracks.from_custom_array(info, tracks.data_type.names)
#        self.info = self.propagator.get_dragging()
        ev = event.particles[0].get_named_data()[1]
        info = [0,ev['pdgid'],[ev['x_m'],ev['y_m'],ev['z_m']],ev['time_ns'],ev['E_tot_GeV'],np.sqrt(np.sum((fposition - iposition)**2))]
        tracks.from_custom_array(info, tracks.data_type.names)
#        print(info)
        event.tracks = tracks

    def create_momentum_nu(self, E, cos, phi):
        sin = (1-cos**2)**0.5
        return np.array([E*sin*np.cos(phi), E*sin*np.sin(phi), E*cos])
