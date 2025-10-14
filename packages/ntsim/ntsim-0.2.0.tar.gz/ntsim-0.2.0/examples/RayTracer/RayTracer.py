import numpy as np
from argparse import Namespace
import configargparse

from ntsim.Medium.base.BaseMediumProperties                import BaseMediumProperties
from ntsim.PrimaryGenerators.Laser                           import Laser, LaserConfig
from ntsim.Medium.Medium                                     import Medium
from ntsim.Propagators.PhotonPropagators.MCPhotonPropagator  import MCPhotonPropagator, mcPhotonPropagatorConfig
import ntsim.utils.systemofunits as units
from ntsim.Telescopes.Factory.TelescopeFactory                         import TelescopeFactory
from ntsim.Medium.Example1MediumProperties import Example1MediumProperties, Example1MediumPropertiesConfig
from ntsim.Telescopes.Base.BoundingBoxNode                     import BoundingBoxNode
from ntsim.Telescopes.Example1.Example1Telescope             import Example1TelescopeConfig
from ntsim.SensitiveDetectors.Factory.SensitiveDetectorFactory      import SensitiveDetectorFactory
from examples.Telescopes.Example1.Example1Telescope          import example1_telescope_options
from ntsim.Propagators.RayTracers.rt_utils                   import ray_tracer
from ntsim.utils.report_timing                               import report_timing
import logging
log=logging.getLogger('NTsim')
logformat='[%(name)20s ] %(levelname)8s: %(message)s'
logging.basicConfig(format=logformat)
from dataclasses import dataclass, field
from typing import Union, List

import cProfile

def example1_medium_properties_options(opts) -> Example1MediumPropertiesConfig:
    return Example1MediumPropertiesConfig(
        waves = opts.photons.waves,
        anisotropy = opts.medium.anisotropy,
        scattering_inv_length_m = opts.medium.absorption_inv_length_m,
        absorption_inv_length_m = opts.medium.absorption_inv_length_m,
        group_refraction_index = opts.medium.group_refraction_index,
        scattering_model = opts.medium.model
    )

def photon_propagator_options(opts) -> mcPhotonPropagatorConfig:
    return mcPhotonPropagatorConfig(
        n_scatterings = opts.photonpropagator.n_scatterings
    )

def laser_options(opts) -> LaserConfig:
    if opts.laser.diffuser[0] == 'exp':
        diffuser = DiffuserExponential(float(opts.laser.diffuser[1]))
    elif opts.laser.diffuser[0] == 'cone':
        diffuser = DiffuserCone(float(opts.laser.diffuser[1]))
    elif opts.laser.diffuser[0] == 'none':
        diffuser = None
    else:
        raise ValueError("Invalid diffuser type")

    return LaserConfig(
        waves=opts.photons.waves,
        n_bunches=opts.photons.bunches,
        photon_weight=opts.photons.weight,
        n_photons=opts.laser.n_photons,
        direction=opts.laser.direction,
        position=opts.laser.position,
        diffuser=diffuser,
        progenitor = [0]
    )

class simulation:
    def init(self):
        self.light_source = Laser()  #
        self.propagator   = mcPhotonPropagator() #

    def configure(self,opts):
        self.light_source.configure(laser_options(opts))
        self.propagator.configure(photon_propagator_options(opts))
        # Create a TelescopeFactory object
        tel_factory = TelescopeFactory()
        # Configure the factory with the provided options
        tel_factory.configure(opts)

        # Get telescope
        tel_blueprint = tel_factory.get_blueprint()
        self.telescope = tel_blueprint(tel_factory.name)

        # Configure the telescope
        telescope_config = example1_telescope_options(opts)
        self.telescope.configure(example1_telescope_options(opts))

        # Build the bounding boxes for the telescope
#        self.telescope.build(detector_blueprint=Example1SensitiveDetector)
        det_factory = SensitiveDetectorFactory()
        det_factory.configure(opts)
        detector_blueprint = det_factory.get_blueprint()
        self.telescope.build(detector_blueprint=detector_blueprint)

        # Initialize and add medium properties to the telescope
        medium_properties = Example1MediumProperties('Example1MediumProperties')
        self.medium       = Medium(medium_properties) #
        self.medium.configure(example1_medium_properties_options(opts))

        # Initialize detector effects
        self.effects = self.telescope.sensitive_detectors[0].effects
        self.effects_options = np.array(self.telescope.sensitive_detectors[0].effects_options)
        self.effects_names = np.array(self.telescope.sensitive_detectors[0].effects_names)

    @report_timing
    def process(self):
        bbox_array, detector_array = self.telescope.flatten_nodes()
        self.telescope.world.print()

        target_depth = opts.depth
        bboxes_depth = self.telescope.boxes_at_depth(bbox_array, target_depth)
        detectors_depth = self.telescope.detectors_at_depth(bbox_array, detector_array, target_depth)
#        print(f'bboxes_depth: {bboxes_depth}')
#        print(f'detectors_depth: {detectors_depth}')
        print(f'effects: {self.effects} {self.effects_options} {self.effects_names}')
        for bunch_id, photons in enumerate(self.light_source.make_photons_generator()):
            self.propagator.propagate(photons,self.medium)
            hits_list=ray_tracer(photons.r,photons.t, photons.wavelength, bboxes_depth,
                       detectors_depth,self.effects,self.effects_options)
            # Create a structured array from hits_list
            print(hits_list)
            # Convert each inner list to a tuple
            hits_tuple_list = [tuple(x) for x in hits_list]
            dtype_fields = [('uid', 'f8'), ('t_hit', 'f8'), ('x_hit', 'f8'), ('y_hit', 'f8'), ('z_hit', 'f8')] + [(name, 'f8') for name in self.effects_names] + [('w_noabs', 'f8'), ('i_photon', 'f8'), ('weight', 'f8')]
            print(dtype_fields)
            hits_array = np.array(hits_tuple_list, dtype=dtype_fields)
            print(hits_array)




def profiler(opts):
    profiler = cProfile.Profile()
    profiler.enable()
    simu = simulation()
    simu.init()
    simu.configure(opts)
    simu.process()
    profiler.disable()
    profiler.print_stats(sort='cumulative')
    profiler.dump_stats('profile_results.prof')


if __name__ == '__main__':
    __name__ = 'RayTracerExample'
    # Parse command line arguments
    from ntsim.utils.arguments_handling import NestedNamespace

    parser = configargparse.get_argument_parser()
    parser.add_argument('-l', '--log-level',type=str,choices=('deepdebug', 'debug', 'info', 'warning', 'error', 'critical'),default='INFO',help='logging level')
    parser.add('--medium.model', type=str, choices=('HenyeyGreenstein','Rayleigh','HG+Rayleigh','FlatScatteringModel'),default='HenyeyGreenstein', help='scattering model')
    parser.add('--medium.scattering_inv_length_m', type=float, default=[1./(10*units.m),1./(40*units.m)], help='scattering inverse length in m^-1')
    parser.add('--medium.absorption_inv_length_m', type=float, default=[1./(20*units.m),1./(100*units.m)], help='absorption inverse length in m^-1')
    parser.add('--medium.group_refraction_index', type=float, nargs=2, default=[1.34,1.36], help='group refraction index')
    parser.add('--medium.anisotropy', type=float, default=0.88, help='scattering anisotropy')

    parser.add('--photonpropagator.n_scatterings', type=int, default=5, help='number of random scatterings')

    parser.add('--photons.waves', type=float, nargs=2, default=[350,600], help='wavelengths in nm')
    parser.add('--photons.bunches', type=int,default=1,help="number of bunches")
    parser.add("--photons.weight",type=float,default=1,help="statistical weight of a photon")

    parser.add('--output-dir', type=str, default='plots/', help='Output directory for plots')
    parser.add("--laser.n_photons",type=int,default=10000, help="number of photons to generate")
    parser.add("--laser.direction",nargs='+',type=float,default=[0.,0.,1.],help="unit three vector for photons direction")
    parser.add("--laser.position",nargs='+',type=float,default=[0.,0.,0.],help="three vector for laser position")
    parser.add("--laser.diffuser",nargs='+',default=('none',0),help="laser diffuser mode: (exp,sigma) or (cone, angle)")

    parser.add('--telescope.name', dest='telescope_name', type=str, default='Example1Telescope', help='Telescope to use')
    parser.add('--telescope.Example1.radius', type=float, default=1, help='sensitive_detector radius')
    parser.add('--telescope.Example1.photocathode_unit_vector', type=float, nargs=3, default=[0, 0, -1], help='unit vector of the  sensitive detector photocathode ')
    parser.add('--telescope.Example1.n_clusters_x', type=int, default=1, help='Number of clusters in x direction')
    parser.add('--telescope.Example1.n_clusters_y', type=int, default=1, help='Number of clusters in y direction')
    parser.add('--telescope.Example1.n_strings_x', type=int, default=1, help='Number of strings in x direction within a cluster')
    parser.add('--telescope.Example1.n_strings_y', type=int, default=1, help='Number of strings in y direction within a cluster')
    parser.add('--telescope.Example1.z_spacing', type=float, default=1, help='Spacing in z direction')
    parser.add('--telescope.Example1.n_detectors_z', type=int, default=1, help='Number of detectors in z direction per string')
    parser.add('--telescope.Example1.x_string_spacing', type=float, default=1, help='Spacing between strings in x direction')
    parser.add('--telescope.Example1.y_string_spacing', type=float, default=1, help='Spacing between strings in y direction')
    parser.add('--telescope.Example1.x_cluster_spacing', type=float, default=1, help='Spacing between clusters in x direction')
    parser.add('--telescope.Example1.y_cluster_spacing', type=float, default=1, help='Spacing between clusters in y direction')
    parser.add('--telescope.Example1.world_center', type=float, nargs=3, default=[0, 0, 0], help='Center of the world')

    parser.add('--detector.name', dest='sensitive_detector_name', type=str, default='Example1SensitiveDetector', help='Sensitive detector to use')

    parser.add('--profile', action='store_true', help='add cprofiler')
    parser.add('--depth', type=int, default=0, help='depth bounding boxes')


    opts = parser.parse_args(namespace=NestedNamespace())
    if opts.log_level == 'deepdebug':
        print("Logging level deepdebug not implemented, using DEBUG instead")
        log.setLevel(logging.getLevelName("DEBUG"))
        logging.root.setLevel(logging.getLevelName("DEBUG")) # set global logging level
    else:
        log.setLevel(logging.getLevelName(opts.log_level.upper()))
        logging.root.setLevel(logging.getLevelName(opts.log_level.upper()))  # set global logging level

    if opts.profile:
        profiler(opts)
    else:
        simu = simulation()
        simu.init()
        simu.configure(opts)
        simu.process()
