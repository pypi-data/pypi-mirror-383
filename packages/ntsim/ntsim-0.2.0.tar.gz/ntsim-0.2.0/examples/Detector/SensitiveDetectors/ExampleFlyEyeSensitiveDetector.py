import sys
import numpy as np
import configargparse
import pyqtgraph.opengl as gl

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

from ntsim.utils.gen_utils import segment_generator
from ntsim.utils.pyqtgraph_tricks import draw_arrow
from ntsim.SensitiveDetectors.FlyEye.FlyEyeCompound import Fly_Eye_Compound
from ntsim.SensitiveDetectors.FlyEye.FlyEyePMT import position_response

def displaySphereandSegments(opts):
    app = QApplication([])
    
    window = gl.GLViewWidget()
    window.show()
    
    Fly_Eye = Fly_Eye_Compound()
    Fly_Eye.segments_nu = opts.segments_nu
    Fly_Eye.position_compound_m = np.array(opts.position_compound_m)
    Fly_Eye.radius_icosphere_m = opts.radius_icosphere_m
    Fly_Eye.unit_vector_compound = opts.unit_vector_compound
    Fly_Eye.generate_icosphere()
    Fly_Eye.place_PMTs(uid=0,parent=None)
    detectors = Fly_Eye.PMT_list
    
    start = Fly_Eye.position_compound_m
    end = start + 2*Fly_Eye.radius_icosphere_m*Fly_Eye.unit_vector_compound
    color = np.array([0, 1, 0, 1])  # RGBA
    draw_arrow(window, start, end, color)
    
    def add_segments_to_view(window, detector, center, radius, photocathode_unit_vector, num_segments, should_intersect, color_if_correct, color_if_incorrect):
        segments = segment_generator(center=center, radius=radius, num_segments=num_segments, intersect=should_intersect)
        for i in range(num_segments):
            a = segments[i, 0, :]
            b = segments[i, 1, :]
            intersection = detector.line_segment_intersection(a, b)
            hit_position_m = np.array([0,*intersection[1:4]])
            photocatode_intersection = position_response(hit_position_m,np.append(center,photocathode_unit_vector))
            if intersection[0] == should_intersect and photocatode_intersection:  # If the intersection result is as expected
                line = gl.GLLinePlotItem(pos=np.array([a, b]), color=color_if_correct, width=2, antialias=True)
            else:
                line = gl.GLLinePlotItem(pos=np.array([a, b]), color=color_if_incorrect, width=2, antialias=True)
            window.addItem(line)
            window.addItem(gl.GLScatterPlotItem(pos=np.array([a]), color=(1, 1, 1, 1), size=0.1, pxMode=False))  # White start point
            window.addItem(gl.GLScatterPlotItem(pos=np.array([b]), color=(0, 0, 1, 1), size=0.1, pxMode=False))  # Blue end point
    
    for detector in detectors:
        sphere = gl.GLMeshItem(meshdata=gl.MeshData.sphere(rows=10, cols=20), color=(1, 1, 1, 0.2), shader='shaded', glOptions='additive')
        sphere.scale(detector.radius, detector.radius, detector.radius)
        sphere.translate(*detector.position)
        window.addItem(sphere)
        
        start = detector.position
        end = start + 2*detector.radius*detector.photocathode_unit_vector
        color = np.array([1, 0, 0, 1])  # RGBA
        draw_arrow(window, start, end, color)
        
        # Generate line segments that should intersect the sphere and add them to the view
        add_segments_to_view(window, detector, np.array(detector.position), detector.radius, detector.photocathode_unit_vector, opts.num_segments, True, (0, 1, 0, 1), (1, 0, 0, 1))
        
        # Generate line segments that should not intersect the sphere and add them to the view
        add_segments_to_view(window, detector, np.array(detector.position), detector.radius, detector.photocathode_unit_vector, opts.num_segments, False, (1, 1, 0, 1), (1, 0, 0, 1))
    
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QApplication.instance().exec_()

if __name__ == '__main__':
    parser = configargparse.get_argument_parser()
    parser.add('--segments_nu', type=float, default=1, help='')
    parser.add('--position_compound_m', type=float, nargs=3, default=[0.,0.,0.], help='Center of the Fly Eye Detector')
    parser.add('--radius_icosphere_m', type=float, default=1, help='Radius of the Fly Eye Detector')
    parser.add('--unit_vector_compound', type=float, nargs=3, default=[0.,0,-1.], help='Center of the Fly Eye Detector')
    parser.add('--num_segments', type=int, default=3, help='number of segments to generate')
    
    opts = parser.parse_args()
    
    displaySphereandSegments(opts)