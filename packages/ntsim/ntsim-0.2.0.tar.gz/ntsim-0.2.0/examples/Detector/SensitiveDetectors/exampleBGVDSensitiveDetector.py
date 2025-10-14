import numpy as np
import configargparse
import logging
from ntsim.SensitiveDetectors.BGVDSensitiveDetector.BGVDSensitiveDetector import BGVDSensitiveDetector
from ntsim.utils.gen_utils import  segment_generator

def simulate_response(opts):
    # Set up logging
    logging.basicConfig(level=logging.DEBUG if opts.verbose else logging.INFO)
    logger = logging.getLogger(__name__)

    # Create a BGVDSensitiveDetector object
    detector = BGVDSensitiveDetector(uid=0, position=np.array(opts.center), radius=opts.radius, photocathode_unit_vector=opts.detector_normal)

    # Generate segments that should intersect the detector
    segments = segment_generator(center=detector.position, radius=detector.radius, num_segments=opts.num_segments)

    # Apply all effects for each segment
    hits_pos = []
    effects = []
    for i in range(opts.num_segments):
        a = segments[i, 0, :]
        b = segments[i, 1, :]
        intersection = detector.line_segment_intersection(a, b)
        if intersection[0]:  # If there is an intersection
            wavelength = np.random.uniform(opts.waves[0], opts.waves[1])
            total_effect, effects_array = detector.response(wavelength, intersection[1:-1])
            if total_effect:
                logger.debug(f"Total effect for segment {i}: {total_effect}")
                hits_pos.append([intersection[1],intersection[2],intersection[3]])
                effects.append(total_effect)

    # Visualize the detector and hits if requested
    if opts.display:
        import pyqtgraph.opengl as gl
        from PyQt5 import QtWidgets
        from ntsim.utils.pyqtgraph_tricks import draw_arrow
        app = QtWidgets.QApplication([])
        window = gl.GLViewWidget()
        window.show()
        window.setWindowTitle('Detector Visualization')
        window.setCameraPosition(distance=10)

        # Add the detector to the window
        sphere = gl.GLMeshItem(meshdata=gl.MeshData.sphere(rows=10, cols=20), color=(1, 1, 1, 0.2), shader='shaded', glOptions='additive')
        sphere.scale(opts.radius, opts.radius, opts.radius)
        sphere.translate(*opts.center)
        window.addItem(sphere)

        # add the photocathode vector
        start = detector.position+detector.radius*detector.photocathode_unit_vector
        end = start+0.1*detector.radius*detector.photocathode_unit_vector
        color = np.array([1, 0, 0, 1])  # RGBA
        draw_arrow(window, start, end, color)

        # Add the hits to the window
        # Convert hits_pos to a numpy array
        hits_pos = np.array(hits_pos)
        center = np.array(opts.center)  # Convert list to numpy array

        # Calculate the distance from each hit position to the center
        distances = np.sqrt(np.sum((hits_pos - center)**2, axis=1))

        # Check if all distances are equal to the radius
        # We use np.allclose to account for potential floating point errors
        if np.allclose(distances, opts.radius):
            print("All hits are on the surface of the sphere.")
        else:
            print("Not all hits are on the surface of the sphere.")

        # Normalize effects to the range [0, 1] for color mapping
        effects = np.array(effects)
        effects_normalized = (effects - effects.min()) / (effects.max() - effects.min())

        # Create a color map
        import matplotlib.pyplot as plt

        # Normalize the effects to the range [0, 1]
        normalized_effects = (effects - np.min(effects)) / (np.max(effects) - np.min(effects))

        # Use a colormap to map the normalized effects to colors
        cmap = plt.get_cmap('viridis')  # Or any other colormap you like
        colors = cmap(normalized_effects)

        # Now colors is a Nx4 array with RGBA values for each effect

#        print(colors)
        # Create GLScatterPlotItem
        hits = gl.GLScatterPlotItem(pos=hits_pos, color=colors, size=0.3)
        window.addItem(hits)


        # Start the Qt event loop
        QtWidgets.QApplication.instance().exec_()

if __name__ == '__main__':
    # Parse command line arguments
    parser = configargparse.get_argument_parser()
    parser.add('--center', type=float, nargs=3, default=[0, 0, 0], help='Center of the sphere')
    parser.add('--radius', type=float, default=2, help='Radius of the sphere')
    parser.add('--detector_normal', nargs='+',type=float,default=[0,0,-1], help='unit vector for photocathode top')
    parser.add("--waves",nargs='+',type=float,default=[350,600],help="wavelengths interval")
    parser.add('--radius', type=float, default=2, help='Radius of the sphere')
    parser.add('--num_segments', type=int, default=1000, help='Number of segments to generate')
    parser.add('--verbose', action='store_true', help='Print detailed debug information')
    parser.add('--display', action='store_true', help='Visualize the detector and hits')

    opts = parser.parse_args()
    simulate_response(opts)
