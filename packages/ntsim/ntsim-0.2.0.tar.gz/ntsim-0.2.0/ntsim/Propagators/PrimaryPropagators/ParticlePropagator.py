from particle import Particle
import numpy as np

from ntsim.utils.report_timing import report_timing
from ntsim.Propagators.Base.PropagatorBase import PropagatorBase

from ntsim.IO.gTracks import gTracks
from ntsim.IO.gParticles import gParticles
from ntsim.IO.gPhotons import gPhotons
from ntsim.IO.converters import g4data

import ntsim.utils.systemofunits as units

from g4camp.g4camp import g4camp

class ParticlePropagator(PropagatorBase):
    arg_dict = {
        'skip_mode':               {'type': str, 'choices': ('cut','fraction'), 'default': 'cut', 'help': ''},
        'g4_casc_bounds_e':        {'type': float, 'nargs': 2, 'default': [10.,10_000.], 'help': 'set minimal/maximal energy to store cascade starters'},
        'g4_mode_custom_physlist': {'type': str, 'choices': ('all_phys','fast','em_cascade'), 'default': 'fast', 'help': ''},
        'g4_photon_suppression':   {'type': int, 'default': 1000, 'help': ''},
        'g4_random_seed':          {'type': int, 'default': 42, 'help': 'set random seed for Geant4'},
        'g4_detector_height':      {'type': float, 'default': 1360., 'help': 'set height (in meters) of cylindrical detector volume'},
        'g4_detector_radius':      {'type': float, 'default': 1000., 'help': 'set radius (in meters) of cylindrical detector volume'},
        'g4_rock_depth':           {'type': float, 'default': 200., 'help': 'set height (in meters) of cylindrical detector volume'},
        'g4_enable_cherenkov':     {'dest': 'g4_cherenkov', 'action': 'store_true', 'help': 'enable production of photons in Geant4'},
        'g4_save_process_name':    {'action': 'store_true', 'help': ''}
    }
    
    def configure(self, opts):
        
        super().configure(opts)
        
        self._g4prop = g4camp(mode_physlist=self.g4_mode_custom_physlist,optics=self.g4_enable_cherenkov,primary_generator='gun')
        self._g4prop.setPhotonSuppressionFactor(self.g4_photon_suppression)
        self._g4prop.setSkipMinMax(self.skip_mode,*self.g4_casc_bounds_e)
        self._g4prop.setRandomSeed(self.g4_random_seed)
        self._g4prop.setDetectorHeight(self.g4_detector_height)
        self._g4prop.setDetectorRadius(self.g4_detector_radius)
        self._g4prop.setRockDepth(self.g4_rock_depth)
        self._g4prop.SaveProcessName(self.g4_save_process_name)
        self._g4prop.configure()
        
        self.world_height_m    = self.g4_rock_depth+self.g4_detector_height
        self.position_shifts_m = 0.5*self.world_height_m-self.g4_rock_depth
    
    def save_metadata(self, i_data, o_data):
        o_data.metadata['parent_uid'] = i_data['parent_uid']
        if self.g4_save_process_name:
            o_data.metadata['process_name'] = i_data['process_name']
    
    @report_timing
    def propagate(self,event):
        
        for gun_particles in list(event.particles.values()):
            if not gun_particles.to_propagate:
                continue
            for n, data in enumerate(gun_particles):
                
                pdgid            = data['pdgid']
                position_m       = data['pos_m']
                direction        = data['direction']
                total_energy_GeV = data['Etot_GeV']
                time_ns          = data['t_ns']
                if abs(pdgid) in (12,14,16):
                    mass_GeV = 0.
                else:
                    mass_GeV = Particle.from_pdgid(pdgid).mass*units.MeV/units.GeV # in GeV
                Ekin_GeV = total_energy_GeV - mass_GeV
                
                self._g4prop.setGunParticle(pdgid)
                self._g4prop.setGunPosition(*position_m, 'm')
                self._g4prop.setGunTime(time_ns, 'ns')
                self._g4prop.setGunDirection(*direction)
                self._g4prop.setGunEnergy(Ekin_GeV, 'GeV')
                
                run = next(self._g4prop.run(1))
                
                g4_cascade_starters = run.particles
                g4_tracks           = run.tracks
                
                if g4_cascade_starters.unique_data:
                    
                    g4_cascade_starters_data = g4_cascade_starters.get_named_data()
                    
                    particles = g4data.to_Particles(g4_cascade_starters_data)
                    
                    particles.gen_cher = True
                    self.save_metadata(g4_cascade_starters_data, particles)
                    
                    event.particles[f'g4_cascade_starters_{n}'] = particles
                
                if g4_tracks.unique_data:
                    g4_tracks_data = g4_tracks.get_named_data()
                    tracks = g4data.to_Tracks(g4_tracks_data)
                    self.save_metadata(g4_tracks_data, tracks)
                    
                    event.tracks[f'g4_tracks_{n}'] = tracks
                
                if self._g4prop.optics:
                    self.logger.info('Geant4 Photon Generation (...)')
                    
                    g4_photons      = run.photons
                    g4_photons_data = g4_photons.get_named_data()
                    
                    photons = g4data.to_Photons(g4_photons_data)
                    event.photons = np.atleast_1d(photons)