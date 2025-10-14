import configargparse, argparse
import numpy as np
import itertools
import h5py
import sys

from numba import njit, types

from argparse import Namespace
from tqdm     import trange
from ntsim.IO import ShortHits

from ntsim.utils.report_timing import report_timing
from ntsim.IO.gPhotons         import gPhotons
from ntsim.IO.gEvent           import gEvent
from ntsim.IO.gHits            import gHits

from ntsim.Base.BaseFactory                                    import BaseFactory
from ntsim.Telescopes.Factory.TelescopeFactory                 import TelescopeFactory
from ntsim.SensitiveDetectors.Factory.SensitiveDetectorFactory import SensitiveDetectorFactory
from ntsim.Triggers.Factory.TriggerFactory                     import TriggerFactory
from ntsim.Analysis.Factory.AnalysisFactory                    import AnalysisFactory
from ntsim.IO.Factories.WriterFactory                          import WriterFactory
from ntsim.Propagators.RayTracers.rt_utils import ray_tracer

import cProfile

class Events2Hits():
    def __init__(self):
        self.TelescopeFactory         = TelescopeFactory()
        self.SensitiveDetectorFactory = SensitiveDetectorFactory()
        self.TriggerFactory           = TriggerFactory()
        self.AnalysisFactory          = AnalysisFactory()

        self.WriterFactory = WriterFactory()

        self.event = gEvent()

        log.info('initialized')

    def add_module_args(self, parser) -> dict:
        known_factories = {}
        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)
            if issubclass(attr_value.__class__, BaseFactory):
                known_factories[attr_value.__class__.__name__] = list(attr_value.known_instances.keys())
                for module_name in attr_value.known_instances:
                    attr_value.known_instances[module_name].add_args(parser)
        return known_factories

    def configure(self, opts: Namespace) -> None:
        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)
            if issubclass(attr_value.__class__, BaseFactory):
                attr_value.configure(opts)
                self.__dict__[f'{attr_name[:-7]}Blueprint'] = attr_value.get_blueprint()
                try:
                    self.__dict__[attr_name[:-7]] = self.__dict__[f'{attr_name[:-7]}Blueprint'](attr_name[:-7])
                    self.__dict__[attr_name[:-7]].configure(opts)
                except:
                    continue
        self.SensitiveDetectorBlueprint.configure(self.SensitiveDetectorBlueprint,opts)

        self.Telescope.build(detector_blueprint=self.SensitiveDetectorBlueprint)
        
        self.Trigger.set_triggers()
        
        self.effects = self.Telescope.sensitive_detectors[0].effects
        self.effects_options = np.array([sensitive_detector.effects_options for sensitive_detector in self.Telescope.sensitive_detectors])
        self.effects_names = np.array(self.Telescope.sensitive_detectors[0].effects_names)
    
    def ReadEvents(self, opts):
        f = h5py.File(opts.file_name)
        self.n_events = f['ProductionHeader']['n_events_original'][()]
        n_scattering  = f['ProductionHeader']['photons_n_scatterings'][()]
        self.photons_list = np.empty(shape=(self.n_events),dtype=itertools.chain)
        for event_id in trange(self.n_events, desc=f'Reading data from {opts.file_name}'):
            photons_chain = ()
            key = f'event_{event_id}'
            if key not in list(f.keys()):
                print(f'there is no {key}')
            event = f[key]
            event_photons = event['photons']
            
            for bunch in event_photons:
                photons = gPhotons('Photons')
                
                pos        = event_photons[bunch]['r'][:]
                time       = event_photons[bunch]['t'][:]
                dir        = event_photons[bunch]['dir'][:]
                wavelength = event_photons[bunch]['wavelength'][:]
                weight     = event_photons[bunch]['weight'][:]
                progenitor = event_photons[bunch]['progenitor'][:]
                absorption_time_ns = event_photons[bunch]['ta'][:]
                
                photons.add_photons(len(progenitor),n_scattering,pos,time,dir,wavelength,progenitor,absorption_time_ns,new_weight=weight)
                photons_chain = itertools.chain(photons_chain,[photons])
            self.photons_list[event_id] = photons_chain
    
    def hits_amplitude_old(self, hits):
        self.hits_time_histos = {}
        self.hits_cumulative = {}
        self.n_om_hitted = 0 # number of hitted OM with npe above opts.threshold
        self.npe_total = 0   # total npe above opts.threshold
        self.npe_max   = 0   # maximum npe in OM
        evtHeader = self.data['event_header']
        photons_sampling_weight = evtHeader['photons_sampling_weight']
#        om_area_weight = evtHeader['om_area_weight']
#        log.debug(f'frames={self.frames}')
        for uid in self.data['hits']:
            hits = self.data['hits'][uid]
            weights = hits.weight*hits.w_noabs*hits.w_pde*hits.w_gel*hits.w_angular*photons_sampling_weight
#            log.debug(f'uid={uid}, hits time.ns = {hits.time_ns}')
            self.hits_time_histos[uid], bin_edges = np.histogram(hits.time_ns,bins=self.frames,weights=weights)
            hits_cumulative = np.cumsum(self.hits_time_histos[uid])
#            print(uid, '\t', hits_cumulative, '\t', self.data['hits'][uid]['cluster'])
#            log.debug(f'hits_cumulative={hits_cumulative}')
            n_total = hits_cumulative[-1]
            if n_total>=self.npe_max:
                self.npe_max = n_total
            if n_total>= self.options.threshold:
                self.n_om_hitted+=1
                self.npe_total+=n_total
                self.hits_cumulative[uid] = hits_cumulative

    def hits_amplitude(self, event_hits):
        self.phe = np.empty(shape=(len(event_hits)),dtype=object)
        for n, event_hit in enumerate(event_hits):
            event_weight = np.empty(shape=(event_hit.n_hits))
            for hit in range(event_hit.n_hits):
                tot_weight = np.prod(event_hit.effects[hit])
                event_weight[hit] = event_hit.weight_no_absorption[hit]*event_hit.self_weight[hit]*tot_weight
            self.phe[n] = event_weight
    
    def transit_hits(self, event_hits):
        transit_time_pread_ns = 3.4
        self.cum_hits = []
        data_type = [('uid',int),('time_ns',float),('phe', float)]
        for n, event_hit in enumerate(event_hits):
            hits_data = np.empty(shape=(0,3))
            unique_hits = set(event_hit.unique_id)
            hits_array = np.sort(event_hit.get_named_data(),order='time_ns')
            for det_uid in unique_hits:
                mask_uid = hits_array['uid'] == det_uid
                hits_time_uid = hits_array['time_ns'][mask_uid]
                hits_phe_uid = hits_array['phe'][mask_uid]
                diff_hits_time_uid = np.diff(hits_time_uid)
                mask_trans_time = np.argwhere(diff_hits_time_uid > transit_time_pread_ns)
                trans_time_window = np.split(hits_time_uid,np.ravel(mask_trans_time+1))
                phe_window = np.split(hits_phe_uid,np.ravel(mask_trans_time+1))
                for i in range(len(trans_time_window)):
                    trans_time_window[i] = np.mean(trans_time_window[i])
                    phe_window[i]        = np.sum(phe_window[i])
                    hits_data = np.row_stack((hits_data,np.array([det_uid,np.mean(trans_time_window[i]),np.sum(phe_window[i])])))
            hits_data = np.array([tuple(_) for _ in hits_data],dtype=data_type)
            self.cum_hits.append(hits_data)
#        print(self.cum_hits)
        return self.cum_hits

    def hits_time_window(self, event_hits):
        time_window_ns = 5_000_000
        output_hits = []
        for n, event_hit in enumerate(event_hits):
            output_event_hits = np.empty(shape=(0,3))
            det_uids = event_hit['uid']
            n_clusters = set(det_uids // 10000)
            print('n_clusters: ', n_clusters)
            for n_cluster in n_clusters:
                min_time = 0.
                cluster_hit = event_hit[event_hit['uid'] // 10000 == n_cluster]
                hits_low  = cluster_hit[cluster_hit['phe'] >= 1.5]
                n_string_sections = set(det_uids // 100)
                for n_string_section in n_string_sections:
                    string_section_hit = hits_low[hits_low['uid'] // 100 == n_string_section]
                    if len(string_section_hit) <= 1: continue
                    print(string_section_hit)
                    for i in range(len(string_section_hit)-1):
                        hit_om = string_section_hit[i]
                        another_oms = string_section_hit[i+1:]
                        mask_om = np.abs(another_oms['uid'] - hit_om['uid']) == 1
                        mask_time = np.abs(another_oms['time_ns'] - hit_om['time_ns']) <= 100
                        if hit_om['phe'] >= 2.0:
#                            mask_phe = np.full_like(mask_om,fill_value=True,dtype=bool)
                            mask_phe = [True]*len(mask_om)
                        else:
                            mask_phe = another_oms['phe'] >= 2.0
                        print('mask_om: ', mask_om)
                        print('mask_time: ', mask_time)
                        print('mask_phe: ', mask_phe)
                        mask_total = (mask_om & mask_time & mask_phe)
                        another_oms = another_oms[mask_total]
                        if not len(another_oms): continue
                        if not min_time:
                            min_time = np.min([hit_om['time_ns'],*another_oms['time_ns']])
                        tmp_min_time = np.min([hit_om['time_ns'],*another_oms['time_ns']])
                        if tmp_min_time <= min_time:
                            min_time = tmp_min_time
                print('min_time: ', min_time)
                if not min_time: continue
#                cluster_hit['time_ns'] -= min_time
                mask_min = cluster_hit['time_ns'] >= min_time
                mask_max = cluster_hit['time_ns'] <= time_window_ns
                cluster_hit = cluster_hit[mask_min & mask_max]
                print('cluster_hit: ', cluster_hit)
                n_oms = set(det_uids)
                for n_om in n_oms:
                    mask_tot = cluster_hit['uid']==n_om
                    mean_time = np.mean(cluster_hit['time_ns'],where=mask_tot)
                    tot_phe = np.sum(cluster_hit['phe'],where=mask_tot)
                    print(np.array([n_om,mean_time,tot_phe]))
                    output_event_hits = np.row_stack((output_event_hits,np.array([n_om,mean_time,tot_phe])))
                print(output_event_hits)
            output_hits.append(output_event_hits)
            print(output_hits)
        return output_hits

    @report_timing
    def process(self):

#        self.Writer.open_file()

        bbox_array, detector_array = self.Telescope.flatten_nodes()
#        self.Writer.write_geometry(bbox_array, detector_array)
        
        target_depth = opts.depth
        bboxes_depth = self.Telescope.boxes_at_depth(bbox_array, target_depth)
        detectors_depth = self.Telescope.detectors_at_depth(bbox_array, detector_array, target_depth)
        print(bboxes_depth)
        trigger_mask = []
        for event_id in range(self.n_events):
#            self.Writer.new_event(event_id)
            self.event.reset()
            hits = gHits(f'Hits')
            for photons in self.photons_list[event_id]:
################# FIXME: to SmartRayTracer
                hits_list = ray_tracer(photons.position_m,photons.time_ns,photons.wavelength_nm,photons.weight,photons.absorption_time_ns,
                                       bboxes_depth,detectors_depth,self.effects,self.effects_options)
                if len(hits_list):
                    hits.add_hits(*list(map(list, zip(*hits_list))),new_effects_names=self.effects_names)
#################
#            self.Writer.write_data(self.event.hits, folder_name='hits')

            analysis_hits = hits.convert2short()
            #ahits = self.Trigger.apply_transit_time_spread(analysis_hits)
            ahits = self.Trigger.transit_time_spread(analysis_hits)
            ahits,mark = self.Trigger.apply_trigger_conditions(ahits)
            ahits = self.Analysis.analysis(ahits)
            if mark == True:
                trigger_mask.append(True)
            else:
                trigger_mask.append(False)
        detected_events_fraction = trigger_mask.count(True)/self.n_events
        print(detected_events_fraction)

#        self.Writer.close_file()
            

if __name__ == '__main__':
    __name__ = 'NTSim'
    import logging
    log=logging.getLogger('NTSim')
    logformat='[%(name)45s ] %(levelname)8s: %(message)s'
    logging.basicConfig(format=logformat)

    parser = configargparse.ArgParser()

    parser.add_argument('-l', '--log-level',type=str,choices=('deepdebug', 'debug', 'info', 'warning', 'error', 'critical'),default='INFO',help='logging level')
    parser.add_argument('--show-options',action="store_true", help='show all options')
    
    parser.add_argument('--file_name',type=str,default='h5_output/events.h5',help='')
    
    opts, _ = parser.parse_known_args()
    log.setLevel(logging.getLevelName(opts.log_level.upper()))

    simu= Events2Hits()

    known_factories = simu.add_module_args(parser)

    parser.add_argument('--telescope.name', dest='telescope_name', type=str, choices=known_factories['TelescopeFactory'], default='Example1Telescope', help='Telescope to use')
    parser.add_argument('--detector.name', dest='sensitive_detector_name', type=str, choices=known_factories['SensitiveDetectorFactory'], default='Example1SensitiveDetector', help='Sensitive detector to use')
    parser.add_argument('--trigger.name', dest='trigger_name', type=str, choices=known_factories['TriggerFactory'], default='BGVDTrigger', help='')
    parser.add_argument('--analysis.name', dest='analysis_name', type=str, choices=known_factories['AnalysisFactory'], default='TriggerAnalysis', help='')

    parser.add_argument('--writer.name', dest='writer_name', type=str, choices=known_factories['WriterFactory'], default='H5Writer', help='')

    parser.add_argument('--depth', type=int, default=0, help='depth bounding boxes')

    opts = parser.parse_args()
    if opts.show_options:
        print(parser.format_values())
    
    simu.configure(opts)
    
    simu.ReadEvents(opts)

    simu.process()