"""
This example configurates Telescope and SensitiveDetector and opens viewer which shows chosen telescope geometry. 
It is able to configure Telescope by name and its own arguments.
Also it is able to configure SensitiveDetector as well.
"""

import configargparse
from ntsim.Telescopes.Factory.TelescopeFactory                          import TelescopeFactory
from ntsim.SensitiveDetectors.Factory.SensitiveDetectorFactory          import SensitiveDetectorFactory
from PyQt5.QtWidgets import QApplication
from pyqtgraph.opengl import GLViewWidget, GLAxisItem
from PyQt5.QtGui import QVector3D
import pyqtgraph.opengl as gl
import numpy as np

def displayBoundingVolumesNodes(world=None, show_bv=True, show_detectors=True, window=None):
    if world is None:
        raise ValueError(f"provide world to display it. Now world={world}.")
    
    def draw_volume(node):
        params = node.quantities[3:]
        nz = np.size(np.nonzero(params))
        if nz == 1:
            return draw_sphere
        elif nz == 2:
            return draw_cylinder
        else:
            return draw_box
        
    def draw_sphere(node, color):
        quantities = node.quantities
        position = quantities[:3]
        radius = quantities[3]
        sphere = gl.GLMeshItem(meshdata=gl.MeshData.sphere(rows=10, cols=20), color=color, shader='shaded', glOptions='additive')
        sphere.scale(radius, radius, radius)
        sphere.translate(position[0], position[1], position[2])
        return sphere
    
    def draw_cylinder(node, color):
        quantities = node.quantities
        position = quantities[:3]
        radius = quantities[3]
        height = quantities[4]
        cylinder = gl.GLMeshItem(meshdata=gl.MeshData.cylinder(rows=10, cols=20), color=color, shader='shaded', glOptions='additive')
        cylinder.scale(radius, radius, 2*height)
        cylinder.translate(position[0], position[1], position[2]-height)
        return cylinder
    
    def draw_box(node, color):
        quantities = node.quantities
        position = quantities[:3]
        width = quantities[3]
        length = quantities[4]
        height = quantities[5]
        size = QVector3D(width, length, height)
        box = gl.GLBoxItem(size=size, color=color)
        box.translate(*np.array(position) - np.array([width, length, height]) / 2)
        return box
    
    bounding_box_items = []
    detector_items = []
    om_items = []
    
    world_item = draw_volume(world)(world, (1, 1, 1, 0.2))
    window.addItem(world_item)
    bounding_box_items.append(world_item)
    for cluster in world.children:
        cluster_item = draw_volume(cluster)(cluster, (1, 1, 1, 0.2))
        window.addItem(cluster_item)
        bounding_box_items.append(cluster_item)
        for string in cluster.children:
            string_item = draw_volume(string)(string, (1, 1, 1, 0.2))
            window.addItem(string_item)
            bounding_box_items.append(string_item)
            for detector in string.children:
                colour = (1, 1, 1, 0.2)
                if len(detector.children) == 0:
                    colour = (1, 1, 1, 0.8)
                detector_item = draw_volume(detector)(detector, colour)
                window.addItem(detector_item)
                detector_items.append(detector_item)
                bounding_box_items.append(detector_item)
                for om in detector.children:
                    om_item = draw_volume(om)(om, (1, 1, 1, 0.8))
                    window.addItem(om_item)
                    om_items.append(om_item)
                    bounding_box_items.append(detector_item)
 
    for item in bounding_box_items:
        item.setVisible(show_bv)
    
    for item in detector_items:
        item.setVisible(show_detectors)
    
    for item in om_items:
        item.setVisible(show_detectors)

def configure_telescope(opts, parser):
    TFactory = TelescopeFactory()
    SDFactory = SensitiveDetectorFactory()
    
    TFactory.known_instances[f"{opts.telescope_name}"].add_args(parser)
    SDFactory.known_instances[f"{opts.sensitive_detector_name}"].add_args(parser)

    opts = parser.parse_args()

    TFactory.configure(opts)
    SDFactory.configure(opts)

    Telescope = TFactory.get_blueprint()(f"{opts.telescope_name}")
    SensitiveDetectorBlueprint = SDFactory.get_blueprint()

    Telescope.configure(opts)
    SensitiveDetectorBlueprint.configure(SensitiveDetectorBlueprint,opts)

    Telescope.build(detector_blueprint=SensitiveDetectorBlueprint)
    bbox_array, detector_array = Telescope.flatten_nodes()

    target_depth = 0

    bboxes_depth    = Telescope.boxes_at_depth(bbox_array, target_depth)
    detectors_depth = Telescope.detectors_at_depth(bbox_array, detector_array, target_depth)

    effects         = Telescope.sensitive_detectors[0].effects
    effects_options = np.array([sensitive_detector.effects_options for sensitive_detector in Telescope.sensitive_detectors])
    effects_names   = np.array(Telescope.sensitive_detectors[0].effects_names)
    
    geometry = {'bboxes_depth': bboxes_depth, 'detectors_depth': detectors_depth, 
                'effects': effects, 'effects_options': effects_options, 'effects_names': effects_names,
                'bbox_array': bbox_array, 'detector_array': detector_array, 'world': Telescope.world}

    return geometry

def set_viewer():
    app = QApplication([])
    window = GLViewWidget()
    window.setBackgroundColor('black')
    window.setWindowTitle('Telescope')
    window.setGeometry(100, 100, 800, 600)
    axis = GLAxisItem()
    window.addItem(axis)

    return app, window

if __name__ == "__main__":
    parser = configargparse.ArgParser()

    parser.add('--telescope.name', dest='telescope_name', type=str, default='BGVDTelescope', help='Telescope to use.')
    parser.add('--detector.name', dest='sensitive_detector_name', type=str, default='BGVDSensitiveDetector', help='Sensitive detector to use.')
    parser.add('--show-bv', action='store_true', help='Show only bounding volumes.')
    parser.add('--show-detectors', action='store_true', help='Show only detectors.')
    opts, _ = parser.parse_known_args()
    show_bv = not opts.show_detectors
    show_detectors = not opts.show_bv
    if show_bv == False and show_detectors == False:
        show_bv = True
        show_detectors = True
    geometry = configure_telescope(opts, parser)
    app, window = set_viewer()
    displayBoundingVolumesNodes(geometry['world'], show_bv=show_bv, show_detectors=show_detectors, window=window)
    window.show()
    app.exec_()
    
