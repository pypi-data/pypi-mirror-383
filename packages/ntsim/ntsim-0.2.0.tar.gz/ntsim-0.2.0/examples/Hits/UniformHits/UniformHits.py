import pyqtgraph.opengl as gl
import pyqtgraph as pg
import configargparse
import numpy as np
import random

from ntsim.SensitiveDetectors.Factory.SensitiveDetectorFactory import SensitiveDetectorFactory
from ntsim.Telescopes.Factory.TelescopeFactory import TelescopeFactory
from ntsim.IO.ShortHits import ShortHits

from PyQt5.QtWidgets import QApplication
from pyqtgraph.opengl import GLViewWidget, GLAxisItem
import pyqtgraph.opengl as gl

def drow_hits(hits, detectors):
    
    app = QApplication([])
    view = GLViewWidget()
    view.setBackgroundColor('black')
    view.show()
    
    axis = GLAxisItem()
    view.addItem(axis)
    
    colormap = pg.colormap.get('CET-R3')
    
    hits_data = hits.get_named_data()
    
    n_hits = len(hits_data['uid'])
    hit_positions_m = np.empty(shape=(0,3))
    colors          = np.empty(shape=(0,4), dtype=np.float32)
    radius_m        = np.empty(shape=(0))
    
    for n in range(n_hits):
        hit_positions_m = np.row_stack((hit_positions_m, detectors['position'][np.where(detectors['detector_uid'] == hits_data['uid'][n])]))
        colors = np.row_stack((colors,[1.,1.,0.,1.]))
        radius_m = np.append(radius_m, hits_data['phe'][n])
    viewer_hits = gl.GLScatterPlotItem(pos=hit_positions_m, color = colors, size=radius_m, pxMode=False)
    view.addItem(viewer_hits)
    viewer_hits.setVisible(True)
    app.exec_()

def hits_uniform_distribution(detectors, opts):
    n_hits         = opts.n_hits
    hits_magnitude = opts.hits_magnitude
    time_window_ns = opts.time_window_ns
    
    short_hits = ShortHits()
    detectors_uids = detectors['detector_uid']
    
    hit_uids        = random.choices(detectors_uids, k=n_hits)
    hits_times_ns   = np.random.uniform(low  = time_window_ns[0],
                                        high = time_window_ns[1],
                                        size = n_hits)
    hits_magnitudes = np.random.uniform(low  = hits_magnitude[0],
                                        high = hits_magnitude[1],
                                        size = n_hits)
    
    short_hits.add_hits(new_uid     = hit_uids,
                        new_time_ns = hits_times_ns,
                        new_phe     = hits_magnitudes)
    
    return short_hits

if __name__ == '__main__':
    parser = configargparse.get_argument_parser()
    parser.add('--telescope.name', dest='telescope_name', type=str, default='SunflowerTelescope', help='Telescope to use')
    parser.add('--detector.name', dest='sensitive_detector_name', type=str, default='BGVDSensitiveDetector', help='Sensitive detector to use')
    
    parser.add('--n_hits', type=int, default=100, help='')
    parser.add('--hits_magnitude', type=float, nargs=2, default=[1,2], help='')
    parser.add('--time_window_ns', type=float, nargs=2, default=[0,100], help='')
    
    aTelescopeFactory = TelescopeFactory()
    aSensitiveDetectorFactory = SensitiveDetectorFactory()
    
    aTelescopeFactory.known_instances['SunflowerTelescope'].add_args(parser)
    aSensitiveDetectorFactory.known_instances['Fly_Eye_PMT'].add_args(parser)
    
    opts = parser.parse_args()
        
    aTelescopeFactory.configure(opts)
    aSensitiveDetectorFactory.configure(opts)
    
    Telescope = aTelescopeFactory.get_blueprint()('SunflowerTelescope')
    Telescope.configure(opts)
    SensitiveDetectorBlueprint = aSensitiveDetectorFactory.get_blueprint()
    
    SensitiveDetectorBlueprint.configure(SensitiveDetectorBlueprint,opts)
    Telescope.build(detector_blueprint=SensitiveDetectorBlueprint)
    
    _, detector_array = Telescope.flatten_nodes()
    
    hits = hits_uniform_distribution(detector_array, opts)
    drow_hits(hits, detector_array)