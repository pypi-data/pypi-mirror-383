import pyqtgraph.opengl as gl
import configargparse
import numpy as np
import h5py
import sys

from tqdm import trange

from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore

from ntsim.SensitiveDetectors.FlyEye.FlyEyePMT import Fly_Eye_PMT
from ntsim.SensitiveDetectors.Base.SphericalSensitiveDetector import SphericalSensitiveDetector
from ntsim.utils.pyqtgraph_tricks import draw_arrow

def ReadData(opts):
    data     = opts.file_name
    n_events = opts.events2read
    file     = h5py.File(data)
    geometry = file['geometry/Geometry']
    detector_positions  = geometry['position']
    detector_directions = geometry['direction']
    detector_radius     = geometry['radius']
    for event_id in trange(n_events, desc=f'Reading data from {data}'):
        key = f'event_{event_id}'
        if key not in list(file.keys()):
            print(f'there is no {key}') 
        event = file[key]
        photons = event['photons']
        photons_positions = np.empty(shape=(5,10,3),dtype=float)
        for n_bunch, bunch in enumerate(photons):
            if photons[bunch]['r'][0].size > 0:
                for n_step, photons_step in enumerate(photons[bunch]['r']):
                    photons_positions[n_step] = photons_step
    return (detector_positions, detector_directions, detector_radius), photons_positions

def generate_sensitive_detectors(detector_quantities):
    detector_positions  = detector_quantities[0]
    detector_directions = detector_quantities[1]
    detector_radius     = detector_quantities[2]
    uid = 0
    detectors = np.empty(shape=(len(detector_positions)),dtype=object)
    for n_detector in range(len(detector_positions)):
        detectors[n_detector] = Fly_Eye_PMT(
                                            uid=uid,
                                            position=detector_positions[n_detector],
                                            radius=detector_radius[n_detector],
                                            photocathode_unit_vector=detector_directions[n_detector],
                                            parent=None
        )
        uid += 1
    return detectors

def displaySphereandSegments(detectors, photons_positions):
    app = QApplication([])
    
    window = gl.GLViewWidget()
    window.show()
    
    segments = np.empty(shape=(10,5,3))
    for n in range(10):
        segments[n] = photons_positions[:,n,:]
    
    for track in segments:
        for n_segment in range(len(track)-1):
            a = track[n_segment]
            b = track[n_segment+1]
            for detector in detectors:
#                print(detector.position)
#                print(np.array([a,b]))
                intersection = detector.line_segment_intersection(a, b)
#                print('intersection: ', intersection)
                hit_position_m = np.array([0,*intersection[1:4]])
                photocatode_intersection = SphericalSensitiveDetector.position_response(hit_position_m,np.array([0,*detector.position,*detector.photocathode_unit_vector]))
#                print(photocatode_intersection)
                if intersection[0]:  # If the intersection result is as expected
                    line = gl.GLLinePlotItem(pos=np.array([a, b]), color=(0, 1, 0, 1), width=2, antialias=True)
                    window.addItem(line)
                    txtitem1 = gl.GLTextItem(pos=intersection[1:4], text=str(intersection[1:4]))
                    window.addItem(txtitem1)
                    txtitem1 = gl.GLTextItem(pos=a, text=str(a))
                    window.addItem(txtitem1)
                    window.addItem(gl.GLScatterPlotItem(pos=np.array([a]), color=(1, 1, 1, 1), size=0.1, pxMode=False))  # White start point
                    window.addItem(gl.GLScatterPlotItem(pos=np.array([b]), color=(0, 0, 1, 1), size=0.1, pxMode=False))  # Blue end point
                else:
                    line = gl.GLLinePlotItem(pos=np.array([a, b]), color=(1, 0, 0, 1), width=2, antialias=True)
#                    window.addItem(line)
    
    for detector in detectors:
#        print(detector.position)
        sphere = gl.GLMeshItem(meshdata=gl.MeshData.sphere(rows=10, cols=20), color=(1, 1, 1, 0.2), shader='shaded', glOptions='additive')
        sphere.scale(detector.radius, detector.radius, detector.radius)
        sphere.translate(*detector.position)
        window.addItem(sphere)
        start = detector.position
        end = start + 2*detector.radius*detector.photocathode_unit_vector
        color = np.array([1, 1, 0, 1])  # RGBA
        draw_arrow(window, start, end, color)
    
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QApplication.instance().exec_()
        

if __name__ == '__main__':
    parser = configargparse.get_argument_parser()
    parser.add('--file.name', dest='file_name', type=str, default='../../work/h5_output/events.h5', help='')
    parser.add('--events2read', type=int, default=1, help='')
    
    opts = parser.parse_args()
    
    detector_quantities, photons_positions = ReadData(opts)
    
    detectors = generate_sensitive_detectors(detector_quantities)
    
    displaySphereandSegments(detectors, photons_positions)