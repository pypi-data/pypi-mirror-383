import pyqtgraph.opengl as gl
import pyqtgraph as pg
import configargparse
import numpy as np

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

def hits_fix(detector_array, opts):
    
    assert any(map(lambda v: v in opts.hitted_detector_uids, detector_array['detector_uid']))
    
    hitted_detector_uids = opts.hitted_detector_uids
    hits_magnitude       = opts.hits_magnitude
    hits_time_ns         = opts.hits_time_ns
    
    short_hits = ShortHits()
    
    short_hits.add_hits(new_uid     = hitted_detector_uids,
                        new_time_ns = hits_time_ns,
                        new_phe     = hits_magnitude)
    
    return short_hits

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
    print(opts)
    aTelescopeFactory.configure(opts[0])
    aSensitiveDetectorFactory.configure(opts[0])
    
    Telescope = aTelescopeFactory.get_blueprint()('SunflowerTelescope')
    Telescope.configure(opts[0])
    SensitiveDetectorBlueprint = aSensitiveDetectorFactory.get_blueprint()
    
    SensitiveDetectorBlueprint.configure(SensitiveDetectorBlueprint,opts[0])
    Telescope.build(detector_blueprint=SensitiveDetectorBlueprint)
    
    _, detector_array = Telescope.flatten_nodes()
    
    parser.add('--hitted_detector_uids', type=int, nargs='+', choices=detector_array['detector_uid'], help='')
    parser.add('--hits_magnitude', type=float, nargs='+', help='')
    parser.add('--hits_time_ns', type=float, nargs='+', help='')
    
    opts = parser.parse_args()
    
    assert len(opts.hits_magnitude) == len(opts.time_window_ns) == len(opts.hitted_detector_uids)
    
    hits = hits_fix(detector_array, opts)
#    drow_hits(hits, detector_array)