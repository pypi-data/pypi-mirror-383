import numpy as np
from ntsim.IO.gParticles import gParticles
from ntsim.utils.report_timing import report_timing
import ntsim.utils.systemofunits as units
from ntsim.PrimaryGenerators.Base.PrimaryGeneratorBase import PrimaryGeneratorBase
from particle import Particle
from ntsim.utils.gen_utils import make_random_position_shifts

class ToyGen(PrimaryGeneratorBase):
    arg_dict = {
        'particle_pdgid'   : {'type': int, 'default': 13, 'help': ''},
        'n_gun_particles'  : {'type': int, 'default': 1, 'help': ''},
        'tot_energy_GeV'   : {'type': float, 'default': 1, 'help': ''},
        'position_m'       : {'type': float, 'nargs': 3, 'default': [0,0,0], 'help': ''},
        'direction'        : {'type': float, 'nargs': 3, 'default': [0,0,1], 'help': ''},
        'shifts_dimensions': {'type': float, 'nargs': 2, 'default': [0,0], 'help': ''}
    }
    arg_dict.update(PrimaryGeneratorBase.arg_dict_position)
    
    def __post_configure__(self):
        N_particles = self.n_gun_particles
        self.particles = gParticles(size=N_particles, 
                                    uid = np.arange(N_particles),
                                    pdgid = self.particle_pdgid,
                                    Etot_GeV = self.tot_energy_GeV,
                                    t_ns=0,
                                    pos_m=self.position_m,
                                    direction=self.direction
                                   )
        
    @report_timing
    def make_event(self, event):
        particles = self.particles
        #sample position
        if self.random_position:
            particles.position, weight = self.set_random_position(1, self.random_volume)
            event.EventHeader.event_weight = weight
        #sample direction
        if self.set_angular_direction:
            particles.direction = self.angular_direction(self.direction_theta, self.direction_phi)
        #push our particles to the event    
        event.particles['Primary'] = particles
        #output the information
        for p in particles:
            self.logger.info(f'Generated particle %d: %s with energy %g GeV',
                             p['uid'], 
                             Particle.from_pdgid(p['pdgid']).name, 
                             p['Etot_GeV'])
        