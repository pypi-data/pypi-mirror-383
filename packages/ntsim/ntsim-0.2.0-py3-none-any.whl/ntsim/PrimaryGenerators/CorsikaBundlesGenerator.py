from ntsim.PrimaryGenerators.Base.PrimaryGeneratorBase import PrimaryGeneratorBase
from particle import Particle
from ntsim.utils.report_timing import report_timing
import ntsim.utils.systemofunits as units
from ntsim.IO.gParticles import gParticles
from ntsim.utils.read_corsika import process_corsika_file

import numpy as np

def get_bundle_center(pos_x, pos_y):
    center_x = np.mean(pos_x)
    center_y = np.mean(pos_y)
    return np.array([center_x, center_y])

class CorsikaBundlesGenerator(PrimaryGeneratorBase):
    """A primary generator, which adds particles from the given Corsika file.

    Each Corsika file is expected to have particles (e.g. muons, electrons) from several EAS'es, born by primary particle
    (e.g. proton, helium). After chosing file, EAS index should be given to let the generator know, from which particular EAS
    particles should be read

    Parameters
    ----------
    filename: str 
       Path to Corsika file
    EAS: int
       Index of EAS to read particles from, set to 0 by default.
    particle_pdg: int
       PDG code for particle to be added from Corsika file, set to 13 (muons) by default
    primary_pdg: int 
       PDG code for EAS primary particle, set to 2212 (proton) by default. It will not be propagated
    position: float
       New x, y position in meters for particles bundle center on surface, by default bundle position is read from the Corsika file
    azimuth:
       New azimuth orientation in degrees for particles bundle, by default bundle orientation is read from the Corsika file
    """

    CorsikaToGeant4_dict = {
        1: 22,      # Gamma
        2: 11,      # Electron
        3:-11,      # Positron
        5:-13,      # Muon+
        6: 13,      # Muon
        13: 2112,   # Neutron
        14: 2212,   # Proton
        15:-2212,   # Anti-proton
        68: 14,     # Neutrino mu
        69:-14,     # Anti-neutrino mu
        66: 12,     # Neutrino e
        67:-12      # Anti-neutrino e
    }

    arg_dict = {
        'filename'       : {'type': str, 'help': ''},
        'EAS'            : {'type': int, 'default': 0, 'help': ''},
        'particle_pdg'   : {'type': int, 'default': [13], 'help': ''},
        'primary_pdg'    : {'type': int, 'default': 2212, 'help': ''},
        'position'       : {'type': float, 'nargs': 2, 'default':[None, None], 'help': ''},
        'azimuth'        : {'type': float, 'default': None, 'help': ''}
    }

    arg_dict.update(PrimaryGeneratorBase.arg_dict_position)

    def get_direction_diff(self, data):
        # if azimuth params passed, find difference
        if self.azimuth != None:
            if 0 <= self.azimuth <= 360:
                return np.radians(self.azimuth) - np.radians(data['primary']['Z_A_angles'][1])
            else:
                raise argparse.ArgumentTypeError(f'Azimuth angle {self.azimuth} must be 0-360 deg.')
        else:
            return .0

    def get_position_diff(self, data):
        # if position params passed, find difference
        if None not in self.position:
            center_pos  = get_bundle_center(data['x'], data['y'])
            return self.position - center_pos
        else:
            return np.array([.0, .0])

    def change_normalize_direction(self, direction, angle_diff):
        # change dir. vector
        zenith          = np.pi - np.arccos(direction[2])
        azimuth         = np.arccos(direction[0]/np.sin(zenith))
        dpx             = np.sin(zenith)*(np.cos(azimuth+angle_diff)-np.cos(azimuth))
        dpy             = np.sin(zenith)*(np.sin(azimuth+angle_diff)-np.sin(azimuth))
        direction[:2]   += np.array([dpx, dpy])
        
        # normalize dir. vector
        norm        = np.sqrt(np.sum(np.power(direction, 2)))
        direction   = direction/norm

        return direction

    def get_Geant_pdg(self, cor_code):
        cor_code = int(cor_code/1000)
        try:
            return self.CorsikaToGeant4_dict[cor_code]
        except KeyError:
            self.logger.debug('No such particle in list, id: %d , returning code 0', cor_code)
            return 0

    # Print log
    def logger_info(self):
        self.logger.info('FILE: %s EAS: %d Particles: %s', self.filename, self.EAS, self.particle_pdg)
    
    @report_timing
    def make_event(self, event):
        # Object of class gParticles to add particles properties
        self.particles = gParticles("Primary")

        self.logger_info()
        
        # read CORSIKA DAT file and make positions in meters
        CORdata         = process_corsika_file(self.filename, desired_EAS = self.EAS)
        CORdata['x']    = np.multiply(CORdata['x'], units.cm)
        CORdata['y']    = np.multiply(CORdata['y'], units.cm)
        
        # map secondary particles we need
        particles_map = list(map(lambda pid:self.get_Geant_pdg(pid) in self.particle_pdg, CORdata['id']))
        for key in list(CORdata.keys())[1:]:
            CORdata[key] = np.array(CORdata[key])[np.array(particles_map)]

        # calculate difference in directions and positions
        angle_diff  = self.get_direction_diff(CORdata)
        pos_diff    = self.get_position_diff(CORdata)

        # form primary part. direction vector from it's angles
        primary_vector = np.array([np.cos(np.radians(CORdata['primary']['Z_A_angles'][1]))*np.sin(np.radians(CORdata['primary']['Z_A_angles'][0])),    \
                                np.sin(np.radians(CORdata['primary']['Z_A_angles'][1]))*np.sin(np.radians(CORdata['primary']['Z_A_angles'][0])),    \
                                -np.cos(np.radians(CORdata['primary']['Z_A_angles'][0]))])
        # rotate primary part. direction vector and normalize it
        primary_vector = self.change_normalize_direction(primary_vector, angle_diff)
        # add pripary part. to file
        self.particles.add_particles(0, 0, self.primary_pdg, [-1, -1, -1], -1, primary_vector, CORdata['primary']['energy'], 1)

        # iterate through read particles
        for dat_ind, dat_particle in enumerate(CORdata['id']):
            gpid_particle = self.get_Geant_pdg(dat_particle)

            momentum = np.array([CORdata['px'][dat_ind], CORdata['py'][dat_ind], -CORdata['pz'][dat_ind]])    # GeV, CORSIKA z axis aims down
            position = [CORdata['x'][dat_ind], CORdata['y'][dat_ind], PrimaryGeneratorBase.arg_dict_position['cylinder_height']['value'][1]] # m
            
            abs_momentum  = np.sqrt(np.sum(np.square(momentum), axis=0))
            mass_GeV      = Particle.from_pdgid(gpid_particle).mass*units.MeV/units.GeV # in GeV
            tot_energy    = np.sqrt(abs_momentum**2 + mass_GeV**2)
            direction     = momentum/abs_momentum

            time  = CORdata['time'][dat_ind]    # particle time t0,ns on surface
            uid   = 0     # particle id (number)
            gen   = 0     # generation

            # change pos and dir of each secondary part.
            position[:2]    += pos_diff
            direction       = self.change_normalize_direction(direction, angle_diff)

            self.particles.add_particles(uid, gen, gpid_particle, position, time, direction, tot_energy)
            self.logger.debug('adding particle #%d: pdg=%d, E=%f GeV',dat_ind, gpid_particle, tot_energy)
        event.particles = self.particles
