import configargparse, argparse
import sys
import numpy as np
from argparse                  import Namespace
from tqdm                      import trange
from ntsim.utils.report_timing import report_timing

from ntsim.random import set_seed

from ntsim.Base import BaseConfig, BaseFactory, RunConfiguration
from ntsim.Telescopes.Factory.TelescopeFactory                          import TelescopeFactory
from ntsim.SensitiveDetectors.Factory.SensitiveDetectorFactory          import SensitiveDetectorFactory
from ntsim.MediumProperties.Factory.MediumPropertiesFactory             import MediumPropertiesFactory
from ntsim.MediumScatteringModels.Factory.MediumScatteringModelsFactory import MediumScatteringModelsFactory
from ntsim.PrimaryGenerators.Factory.PrimaryGeneratorFactory            import PrimaryGeneratorFactory
from ntsim.Propagators.Factories.ParticlePropagatorFactory              import ParticlePropagatorFactory
from ntsim.Propagators.Factories.PhotonPropagatorFactory                import PhotonPropagatorFactory
from ntsim.Propagators.Factories.RayTracerFactory                       import RayTracerFactory
from ntsim.CherenkovGenerators.Factory.CherenkovGeneratorFactory        import CherenkovGeneratorFactory
from ntsim.CloneGenerators.Factory.CloneGeneratorFactory                import CloneGeneratorFactory
from ntsim.Triggers.Factory.TriggerFactory                              import TriggerFactory
from ntsim.Analysis.Factory.AnalysisFactory                             import AnalysisFactory
from ntsim.IO.Factories.WriterFactory                                   import WriterFactory

from ntsim.IO import gEvent, gParticles, gPhotons, gTracks, gHits

class NTSim:
    def __init__(self):
        self.TelescopeFactory             = TelescopeFactory()
        self.SensitiveDetectorFactory     = SensitiveDetectorFactory()
        self.MediumPropertiesFactory      = MediumPropertiesFactory()
        self.MediumScatteringModelFactory = MediumScatteringModelsFactory()
        self.PrimaryGeneratorFactory      = PrimaryGeneratorFactory()
        self.ParticlePropagatorFactory    = ParticlePropagatorFactory()
        self.PhotonPropagatorFactory      = PhotonPropagatorFactory()
        self.RayTracerFactory             = RayTracerFactory()
        self.CherenkovGeneratorFactory    = CherenkovGeneratorFactory()
        self.CloneGeneratorFactory        = CloneGeneratorFactory()
        self.TriggerFactory               = TriggerFactory()
        self.AnalysisFactory              = AnalysisFactory()

        self.WriterFactory = WriterFactory()

        logger.info('Initialized NTSim')
        
    def add_module_args(self, parser) -> dict:
        known_factories = {}
        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)
            if issubclass(attr_value.__class__, BaseFactory):
                known_factories[attr_value.__class__.__name__] = list(attr_value.known_instances.keys())
                for module_name in attr_value.known_instances:
                    attr_value.known_instances[module_name].add_args(parser)
        
        gParticles.add_args(parser)
        gPhotons.add_args(parser)
        gTracks.add_args(parser)
        gHits.add_args(parser)
        
        return known_factories

    def configure_telescope_detector(self, opts: Namespace) -> None:
        if opts.compute_hits:
            
            self.SensitiveDetectorBlueprint.configure(self.SensitiveDetectorBlueprint,opts)

            self.Telescope.build(detector_blueprint = self.SensitiveDetectorBlueprint)
                        
            self.bbox_array, self.detector_array = self.Telescope.flatten_nodes()
            
            target_depth = opts.depth
            
            self.bboxes_depth    = self.Telescope.boxes_at_depth(self.bbox_array, target_depth)
            self.detectors_depth = self.Telescope.detectors_at_depth(self.bbox_array, self.detector_array, target_depth)
            
            self.effects         = self.Telescope.sensitive_detectors[0].effects
            self.effects_options = np.array([sensitive_detector.effects_options for sensitive_detector in self.Telescope.sensitive_detectors])
            self.effects_names   = np.array(self.Telescope.sensitive_detectors[0].effects_names)

    def configure(self, opts: Namespace) -> None:
        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)
            if issubclass(attr_value.__class__, BaseFactory):
                self.logger.info("Using factory %s (%s)", attr_name, attr_value.__class__)
                attr_value.configure(opts)
                name = attr_name[:-7]
                blueprint = attr_value.get_blueprint()
                if blueprint is None:
                    continue
                try:
                    instance = blueprint(blueprint.__name__)
                    setattr(self, name, instance)
                    self.logger.info('Initialized "%s"',name)
                    instance.configure(opts)
                    self.logger.info('Configured "%s"',name)
                except Exception as e:
                    self.logger.warning("Failed to config %s, cause: %s",name, e)
                    setattr(self, name+'Blueprint', blueprint)
        
        gParticles.configure_class(opts)
        gPhotons.configure_class(opts)
        gTracks.configure_class(opts)
        gHits.configure_class(opts)
        
        #FIXME: this is temporary fix, to ensure backward compatibility 
        # (i.e. now the saving properties are defined by the  Writer, not gEvent)
        gEvent.data_save = self.Writer.h5_save_event
        #when we're ready to break this backward compatibility, use just this:
        #gEvent.configure_class(opts)

        self.configure_telescope_detector(opts)
        
        if opts.compute_hits:
            self.RayTracer.configure(self.bboxes_depth, self.detectors_depth, self.effects, self.effects_options, self.effects_names)
        
        self.MediumProperties.init()
                
        self.n_events = opts.n_events
        self.compute_hits = opts.compute_hits
        self.run_configuration = RunConfiguration.from_namespace(opts)
        #remove the unused parts of the configuration
        self.run_configuration.cleanup()
        self.logger.debug(self.run_configuration.to_yaml())
    @report_timing
    def process(self) -> None:
        with self.Writer:
            #opened writer
            self.logger.info('Opened the output file...')
            #write the run configuration
            self.Writer['Header'].write({'run_configuration':self.run_configuration.to_yaml()})
            if hasattr(self, 'bbox_array'):
                self.Writer['Header/geometry'].write({'Bounding_Surfaces':self.bbox_array,
                                                      'Geometry':self.detector_array
                                              })
            for event_id in trange(self.n_events):
                self.logger.info('Starting event #%0d',event_id)
                #create an event for output
                output_event = self.Writer[f'event_{event_id}']
                #create the data
                event = gEvent()
                self.logger.info('Running primary generator...')
                self.PrimaryGenerator.make_event(event)
                self.logger.info('Running particle propagator...')
                self.ParticlePropagator.propagate(event)
                if hasattr(self,'CherenkovGenerator'): 
                    self.logger.info('Cherenkov generator...')
                    self.CherenkovGenerator.generate(event)
                if hasattr(self,'CloneGenerator'): 
                    self.logger.info('Clone generator...')
                    self.CloneGenerator.make_clones_in_event(event, event_id)

                all_hits = {}
                for photons_label, photon_bunches in event.photons.items():
                    for bunch_id,photons in enumerate(photon_bunches):
                        self.logger.info('Running photon propagator for label=%s, bunch=%d...', photons_label, bunch_id)
                        photons = self.PhotonPropagator.propagate(photons,self.MediumProperties,self.MediumScatteringModel)
                        #save the photons to output, if needed
                        if 'photons' in event.data_save:
                            self.logger.debug('Writing photons for label=%s, bunch=%d (size=%d)...', photons_label, bunch_id, photons.size)
                            output_event[f'photons/{photons_label}/{bunch_id}'].write(photons)
                        #calculate hits
                        if self.compute_hits:
                            self.logger.info('Running RayTracer for label=%s, bunch=%d (size=%d)...', photons_label, bunch_id, photons.size)
                            hits = self.RayTracer.propagate(photons)
                            
                            if hits is not None:
                                self.logger.info('RayTracer produced %d hits', hits.size)
                                all_hits[f'{photons_label}_{bunch_id}'] = hits
                #save the hits to the event
                if self.compute_hits:
                    #concatenate hits to a single array
                    self.logger.info('Concatenating hits into a single array...')
                    event.hits = {'Hits':gHits.concatenate(list(all_hits.values()))}
                #FIXME: trigger would better take event as an input and rewrite hits in event inside itself  
                if hasattr(self,'Trigger'): 
                    self.logger.info('Running Trigger...')
                    event.hits['TriggerHits'] = self.Trigger.apply_trigger(event)
                if hasattr(self,'Analysis'):
                    self.logger.info('Running Analysis...')
                    self.Analysis.analysis(event)
                
                self.logger.info('Writing event to output...')
                event.photons = []#disable writing photons - we already did it before
                output_event.write(event)
                
        #closed the writer
        self.logger.info('Closed the output file...')
        
        if hasattr(self,'Analysis'): 
            self.Analysis.save_analysis()

if __name__ == '__main__':
    __name__ = 'NTSim'
#    logformat='[%(name)45s ] %(levelname)8s: %(message)s'
#    logging.basicConfig(format=logformat)
    import logging.config
    from ntsim.utils.logger_config import logger_config
    
    logging.config.dictConfig(logger_config)
    logger = logging.getLogger('NTSim')

    parser = configargparse.ArgParser()

    parser.add_argument('-l', '--log-level',type=str,choices=('deepdebug', 'debug', 'info', 'warning', 'error', 'critical'),default='INFO',help='logging level')
    parser.add_argument('--seed',type=int, default=None, help='random generator seed')
    parser.add_argument('--show-options',action="store_true", help='show all options')
    parser.add_argument('--compute_hits',action="store_true", help='if this flag is set, the detector hits are produced in the output')
    
    opts, _ = parser.parse_known_args()
    #set the random seed for this run - do this before any other initialization is done!
    set_seed(opts.seed)
    
    logger.setLevel(logging.getLevelName(opts.log_level.upper()))

    simu= NTSim()
    simu.logger = logger
    
    known_factories = simu.add_module_args(parser)
    parser.add_argument('--telescope.name', dest='telescope_name', type=str, choices=known_factories['TelescopeFactory'], default=None, help='Telescope to use')
    parser.add_argument('--detector.name', dest='sensitive_detector_name', type=str, choices=known_factories['SensitiveDetectorFactory'], default=None, help='Sensitive detector to use')
    parser.add_argument('--medium_prop.name', dest='medium_properties_name', type=str, choices=known_factories['MediumPropertiesFactory'], default='Example1MediumProperties', help='Medium properties to use')
    parser.add_argument('--medium_scat.name', dest='medium_scattering_model_name', type=str, choices=known_factories['MediumScatteringModelsFactory'], default='HenyeyGreenstein', help='Medium scattering to use')
    parser.add_argument('--generator.name', dest='primary_generator_name', type=str, choices=known_factories['PrimaryGeneratorFactory'], default='ToyGen', help='Primary Geenrator to use')
    parser.add_argument('--propagator.name', dest='particle_propagator_name', type=str, choices=known_factories['ParticlePropagatorFactory'], default='ParticlePropagator', help='Propagator to use')
    parser.add_argument('--photon_propagator.name', dest='photon_propagator_name', type=str, choices=known_factories['PhotonPropagatorFactory'], default='MCPhotonPropagator', help='Photon propagator to use')
    parser.add_argument('--ray_tracer.name', dest='ray_tracer_name', type=str, choices=known_factories['RayTracerFactory'], default='SmartRayTracer', help='Ray tracer to use')
    parser.add_argument('--cherenkov.name', dest='cherenkov_generator_name', type=str, choices=known_factories['CherenkovGeneratorFactory'], default=None, help='')
    parser.add_argument('--cloner.name', dest='clone_generator_name',type=str, choices=known_factories['CloneGeneratorFactory'], default=None, help='')
    parser.add_argument('--trigger.name', dest='trigger_name', type=str, choices=known_factories['TriggerFactory'], default=None, help='')
    parser.add_argument('--analysis.name', dest='analysis_name', type=str, choices=known_factories['AnalysisFactory'], default=None, help='')

    parser.add_argument('--writer.name', dest='writer_name', type=str, choices=known_factories['WriterFactory'], default='H5Writer', help='')

    parser.add_argument('--depth', type=int, default=0, help='depth bounding boxes')
    parser.add_argument('--n_events', type=int, default=1, help='')

    opts = parser.parse_args()
    
    if opts.show_options:
        print(parser.format_values())
    simu.configure(opts)
    
    simu.process()