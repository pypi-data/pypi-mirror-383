import configargparse

from ntsim.SensitiveDetectors.Factory.SensitiveDetectorFactory import SensitiveDetectorFactory
from ntsim.Triggers.Factory.TriggerFactory import TriggerFactory
from ntsim.Telescopes.Factory.TelescopeFactory import TelescopeFactory

from examples.Hits.UniformHits.UniformHits import hits_uniform_distribution
from examples.Hits.FixHits.FixHits import hits_fix

def apply_transit_time_spread(hits, trigger):
    spread_hits = trigger.transit_time_spread(hits)
    return spread_hits

def apply_trigger_one_cluster(hits, trigger):
    spread_hits = trigger.trigger_one_cluster(hits)
    return spread_hits

if __name__ == '__main__':
    parser = configargparse.get_argument_parser()
    parser.add('--telescope.name', dest='telescope_name', type=str, default='SunflowerTelescope', help='Telescope to use')
    parser.add('--detector.name', dest='sensitive_detector_name', type=str, default='BGVDSensitiveDetector', help='Sensitive detector to use')
    
    aTelescopeFactory = TelescopeFactory()
    aSensitiveDetectorFactory = SensitiveDetectorFactory()
    
    for module_name in aTelescopeFactory.known_instances:
        aTelescopeFactory.known_instances[module_name].add_args(parser)
    for module_name in aSensitiveDetectorFactory.known_instances:
        aSensitiveDetectorFactory.known_instances[module_name].add_args(parser)
    
    opts = parser.parse_known_args()
    
    aTelescopeFactory.configure(opts[0])
    aSensitiveDetectorFactory.configure(opts[0])
    
    Telescope = aTelescopeFactory.get_blueprint()('SunflowerTelescope')
    Telescope.configure(opts[0])
    SensitiveDetectorBlueprint = aSensitiveDetectorFactory.get_blueprint()
    
    SensitiveDetectorBlueprint.configure(SensitiveDetectorBlueprint,opts[0])
    Telescope.build(detector_blueprint=SensitiveDetectorBlueprint)
    
    _, detector_array = Telescope.flatten_nodes()
    
    parser_hits = configargparse.get_argument_parser()
    
#    parser_hits.add('--hits_type', type=str, choices=['fix','uniform'], default='fix', help='')
    subparsers = parser_hits.add_subparsers(required=True, help='')
    
    parser_fix = subparsers.add_parser('fix', help='')
    parser_fix.add('--hitted_detector_uids', type=int, nargs='+', choices=detector_array['detector_uid'], help='')
    parser_fix.add('--hits_magnitude', type=float, nargs='+', help='')
    parser_fix.add('--hits_time_ns', type=float, nargs='+', help='')
    parser_fix.set_defaults(func=hits_fix)
    
    parser_uni = subparsers.add_parser('uniform', help='')
    parser_uni.add('--n_hits', type=int, default=100, help='')
    parser_uni.add('--hits_magnitude', type=float, nargs=2, default=[1,2], help='')
    parser_uni.add('--time_window_ns', type=float, nargs=2, default=[0,100], help='')
    parser_uni.set_defaults(func=hits_uniform_distribution)
    
    parser.add('--trigger.name', dest='trigger_name', type=str, default='BGVDTrigger', help='')
    
    aTriggerFactory = TriggerFactory()
    
    for module_name in aTriggerFactory.known_instances:
        aTriggerFactory.known_instances[module_name].add_args(parser)
    
    opts = parser.parse_args()
    
    aTriggerFactory.configure(opts)
    
    Trigger = aTriggerFactory.get_blueprint()(opts.trigger_name)
    Trigger.configure(opts)
    
    opts_hits = parser_hits.parse_args()
    
    hits = opts_hits.func(detector_array, opts_hits)
    
    print(hits.get_named_data())
    
    spread_hits = apply_transit_time_spread(hits, Trigger)
    
    print('spread_hits: ', spread_hits.get_named_data(), len(spread_hits.get_named_data()))
    
    trigger_hits = apply_trigger_one_cluster(spread_hits, Trigger)
    
    print('trigger_hits: ', trigger_hits.get_named_data(), len(trigger_hits.get_named_data()))