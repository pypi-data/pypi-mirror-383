import pyqtgraph.opengl as gl
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
import numpy as np
import sys
import configargparse
from ntsim.SensitiveDetectors.FlyEye.FlyEyePMT import Fly_Eye_PMT, position_response
from ntsim.utils.gen_utils import segment_generator
from ntsim.utils.pyqtgraph_tricks import draw_arrow

def displaySphereandSegments(opts):
    # Create a QApplication instance (this is necessary for any PyQt application)
    app = QApplication([])
    # Create a window with a 3D graphics view
    window = gl.GLViewWidget()
    window.show()

    # Create a sphere item and add it to the view
    sphere = gl.GLMeshItem(meshdata=gl.MeshData.sphere(rows=10, cols=20), color=(1, 1, 1, 0.2), shader='shaded', glOptions='additive')
    sphere.scale(opts.radius, opts.radius, opts.radius)
    sphere.translate(*opts.center)
    window.addItem(sphere)

    # Create a SphericalSensitiveDetector for intersection checks
    detector = Fly_Eye_PMT(uid=0, position=np.array(opts.center), radius=opts.radius, photocathode_unit_vector=opts.photocathode_unit_vector, parent=None)
    start = np.array(opts.center)
    end = start + 2*opts.radius*np.array(opts.photocathode_unit_vector)
    color = np.array([1, 0, 0, 1])  # RGBA
    draw_arrow(window, start, end, color)

    def add_segments_to_view(window, detector, center, radius, num_segments, should_intersect, color_if_correct, color_if_incorrect):
        segments = segment_generator(center=center, radius=radius, num_segments=num_segments, intersect=should_intersect)
        for i in range(num_segments):
            a = segments[i, 0, :]
            b = segments[i, 1, :]
            intersection = detector.line_segment_intersection(a, b)
            hit_position_m = np.array([0,*intersection[1:4]])
            photocatode_intersection = position_response(hit_position_m,np.append(np.array(opts.center),opts.photocathode_unit_vector))
            if intersection[0] == should_intersect and photocatode_intersection:  # If the intersection result is as expected
                
                line = gl.GLLinePlotItem(pos=np.array([a, b]), color=color_if_correct, width=2, antialias=True)
            else:
                line = gl.GLLinePlotItem(pos=np.array([a, b]), color=color_if_incorrect, width=2, antialias=True)
            window.addItem(line)
            window.addItem(gl.GLScatterPlotItem(pos=np.array([a]), color=(1, 1, 1, 1), size=0.1, pxMode=False))  # White start point
            window.addItem(gl.GLScatterPlotItem(pos=np.array([b]), color=(0, 0, 1, 1), size=0.1, pxMode=False))  # Blue end point

    # Generate line segments that should intersect the sphere and add them to the view
    add_segments_to_view(window, detector, np.array(opts.center), opts.radius, opts.num_segments, True, (0, 1, 0, 1), (1, 0, 0, 1))

    # Generate line segments that should not intersect the sphere and add them to the view
    add_segments_to_view(window, detector, np.array(opts.center), opts.radius, opts.num_segments, False, (1, 1, 0, 1), (1, 0, 0, 1))

    # Start the QApplication instance's event loop
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QApplication.instance().exec_()

if __name__ == '__main__':
    # run this example as follows
    # python3 examples/Detector/exampleSphericalSensitiveDetector.py \
    #  --center 1 2 3 --radius 4 --num_segments 3
    # Parse command line arguments
    parser = configargparse.get_argument_parser()
    parser.add('--center', type=float, nargs=3, default=[0, 0, 0], help='Center of the sphere')
    parser.add('--radius', type=float, default=2, help='Radius of the sphere')
    parser.add('--photocathode_unit_vector', type=float, default=[0.,0.,1.], help='')
    parser.add('--num_segments', type=int, default=3, help='number of segments to generate')

    opts = parser.parse_args()

    displaySphereandSegments(opts)
