import configargparse
from argparse import BooleanOptionalAction

from ntsim.IO.gEvent import gEvent
from ntsim.utils.arguments_handling import NestedNamespace
from ntsim.PrimaryGenerators.Factory.PrimaryGeneratorFactory import PrimaryGeneratorFactory
from ntsim.Propagators.Factories.ParticlePropagatorFactory import ParticlePropagatorFactory
from ntsim.CherenkovGenerators.Factory.CherenkovGeneratorFactory import CherenkovGeneratorFactory
from ntsim.PrimaryGenerators.ToyGen import ToyGenConfig
from ntsim.Propagators.PrimaryPropagators.ParticlePropagator import ParticlePropagatorConfig

from dataclasses import dataclass

import logging
logger = logging.getLogger('ParticlePropagator')
logformat='[%(name)20s ] %(levelname)8s: %(message)s'
logging.basicConfig(format=logformat)
    
@dataclass
class CherenkovGeneratorConfig:
    cherenkov_wavelengths: list
    refraction_index:     float
    photon_suppression:     int

def CherenkovGenerator_options(opts: NestedNamespace) -> CherenkovGeneratorConfig:
    return CherenkovGeneratorConfig(
        cherenkov_wavelengths = opts.cherenkov.cherenkov_wavelengths,
        refraction_index      = opts.cherenkov.refraction_index,
        photon_suppression    = opts.cherenkov.photon_suppression
    )

def ParticleGenerator_options(opts: NestedNamespace) -> ToyGenConfig:
    return ToyGenConfig(
        particle_pdgid  = opts.g4particle.particle_pdgid,
        n_gun_particles = opts.g4particle.n_gun_particles,
        position_m      = opts.g4particle.position_m,
        direction       = opts.g4particle.direction,
        kin_energy_GeV  = opts.g4particle.kin_energy_GeV
    )

def mcPhotonPropagator_options(opts: NestedNamespace) -> ParticlePropagatorConfig:
    return ParticlePropagatorConfig(
        photon_suppression  = opts.cherenkov.photon_suppression,
        g4_casc_max_e       = opts.g4particle.g4_casc_max_e,
        g4_casc_max_pht     = opts.g4particle.g4_casc_max_pht,
        g4_enable_cherenkov = opts.g4particle.g4_enable_cherenkov,
        g4_random_seed      = opts.g4particle.g4_random_seed,
        g4_detector_height  = opts.g4particle.g4_detector_height,
        g4_detector_radius  = opts.g4particle.g4_detector_radius
    )

if __name__ == '__main__':
    parser = configargparse.get_argument_parser()
    parser.add('--g4particle.generator_name',dest='primary_generator_name',type=str,default='ToyGen',help='')
    parser.add('--g4particle.propagator_name',dest='particle_propagator_name',type=str,default='ParticlePropagator',help='')
    parser.add('--g4particle.particle_pdgid',type=int,default=11,help='')
    parser.add('--g4particle.n_gun_particles',type=int,default=1,help='')
    parser.add('--g4particle.position_m',type=float,nargs=3,default=[0,0,0],help='initial position of primary particle')
    parser.add('--g4particle.direction',type=float,nargs=3,default=[0,0,1],help='direction of primary particle')
    parser.add('--g4particle.kin_energy_GeV',type=float,default=1,help='')
    parser.add('--g4particle.g4_casc_max_e',type=float,default=0.05,help='')
    parser.add('--g4particle.g4_casc_max_pht',type=float,default=0.05,help='')
    parser.add('--g4particle.g4_enable_cherenkov',action=BooleanOptionalAction,default=False,help='')
    parser.add('--g4particle.g4_random_seed',type=int,default=42,help='random seed for the Geant4')
    parser.add('--g4particle.g4_detector_height',type=float,default=1360,help='')
    parser.add('--g4particle.g4_detector_radius',type=float,default=1000,help='')
    
    parser.add('--cherenkov.photon_suppression',type=int,default=10,help='')
    parser.add('--cherenkov.generator',dest='cherenkov_generator_name',type=str,nargs='+',default=['trackCherenkov','cascadeCherenkov'],help='')
    parser.add("--cherenkov.cherenkov_wavelengths",nargs=2,type=float,default=[350,650],help="wavelength range")
    parser.add("--cherenkov.refraction_index",type=float,default=1.34,help="average refraction index for photon generators")
    
    
    opts = parser.parse_args(namespace=NestedNamespace())
    
    event    = gEvent()
    
    factory_generator = PrimaryGeneratorFactory()
    factory_generator.configure(opts)
    particle_generator = factory_generator.get_instance()[0]
    particle_generator.configure(ParticleGenerator_options(opts))
    particle_generator.make_event(event)

    factory_propagator = ParticlePropagatorFactory()
    factory_propagator.configure(opts)
    particle_propagator = factory_propagator.get_instance()[0]
    particle_propagator.configure(mcPhotonPropagator_options(opts))
    particle_propagator.propagate(event)
    
    factory_cherenkov = CherenkovGeneratorFactory()
    factory_cherenkov.configure(opts)
    track_cherenkov_generator = factory_cherenkov.get_instance()[0]
    cascade_cherenkov_generator = factory_cherenkov.get_instance()[1]

    track_cherenkov_generator.configure(CherenkovGenerator_options(opts))
    track_photons = []
    for tracks in event.tracks:
        track_photons.append(track_cherenkov_generator.propagate(tracks))

    cascade_cherenkov_generator.configure(CherenkovGenerator_options(opts))
    cascade_photons = []
    for particles in event.particles:
        if particles.status.any() == 0: continue
        cascade_photons.append(cascade_cherenkov_generator.propagate(particles))
    
    print(cascade_photons[0].position_m)
    print(event)