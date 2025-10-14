import numpy as np
from ntsim.Detector.base.BoundingBoxNode import BoundingBoxNode
import numpy as np
import configargparse

def createBoundingBoxNodes(opts):
    # Step 1: Define OM box dimensions and their number along a string
    om_radius = opts.om_radius
    num_oms = opts.num_oms
    om_dimensions = [2*om_radius, 2*om_radius, 2*om_radius]

    # Step 2: Calculate string dimensions to exactly bound all OMs
    string_radius = om_radius
    string_height = num_oms * (2 * om_radius + opts.om_z_spacing) - opts.om_z_spacing
    string_dimensions = [2*string_radius, 2*string_radius, string_height]

    # Step 3: Define cluster radius and place bounding boxes of the strings uniformly along the cluster circle all on the same ground
    cluster_radius = opts.cluster_radius
    num_strings = opts.num_strings
    cluster_height = string_height
    cluster_dimensions = [2*cluster_radius, 2*cluster_radius, cluster_height]

    # Step 4: Compute the world dimension with a user defined world radius and height to bound all clusters vertically
    world_radius = opts.world_radius
    world_height = opts.z_margin + cluster_height
    world_dimensions = [2*world_radius, 2*world_radius, world_height]

    # Step 5: Place clusters uniformly in the world
    num_clusters = opts.num_clusters
    world = BoundingBoxNode(uid=0, center=[0, 0, world_height/2], dimensions=world_dimensions)

    # Distance from world center to cluster center
    cluster_distance = world_radius - cluster_radius

    # Angle between clusters on the circle
    cluster_angle = 2 * np.pi / num_clusters

    # Angle between strings in a cluster
    string_angle = 2 * np.pi / num_strings

    for i in range(num_clusters):
        # Calculate cluster position
        angle = i * cluster_angle
        x = cluster_distance * np.cos(angle)
        y = cluster_distance * np.sin(angle)
        z = cluster_height / 2  # Adjusted to make minimum z of the cluster zero

        cluster = BoundingBoxNode(uid=i+1, center=[x, y, z], dimensions=cluster_dimensions)
        world.add_child(cluster)

        for j in range(num_strings):
            # Calculate string position
            angle = j * string_angle
            string_x = x + cluster_radius * np.cos(angle)
            string_y = y + cluster_radius * np.sin(angle)
            string_z = z - cluster_height / 2 + string_height / 2  # Strings are vertical and located within the cluster

            string = BoundingBoxNode(uid=10*(i+1)+j+1, center=[string_x, string_y, string_z], dimensions=string_dimensions)
            cluster.add_child(string)

            for k in range(1, opts.num_oms + 1):
                om_z = string.center[2] - string.dimensions[2] / 2 + opts.om_radius + (2 * opts.om_radius + opts.om_z_spacing) * (k - 1)
                om = BoundingBoxNode(uid=1000 + 100*i + 10*j + k, center=[string.center[0], string.center[1], om_z], dimensions=[2 * opts.om_radius, 2 * opts.om_radius, 2 * opts.om_radius])
                string.add_child(om)

    world.print()
    return world

def displayBoundingBoxNodes(world=None):
    if world is None:
        raise ValueError(f"provide world to display it. Now world={world}.")

    import pyqtgraph.opengl as gl
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QColor
    import sys

    def draw_box(box, color):
        item = gl.GLBoxItem()
        item.setSize(*box.dimensions)
        item.translate(*np.array(box.center) - np.array(box.dimensions) / 2)
        item.setColor(color)
        return item

    app = QApplication([])
    view = gl.GLViewWidget()
    view.setBackgroundColor('black')  # Set background color to light blue
    view.show()

    view.addItem(draw_box(world, QColor(0, 0, 255, 50)))
    for cluster in world.children:
        view.addItem(draw_box(cluster, QColor(0, 255, 0, 50)))
        for string in cluster.children:
            view.addItem(draw_box(string, QColor(255, 0, 0, 50)))
            for detector in string.children:
                view.addItem(draw_box(detector, QColor(0, 255, 255, 100)))

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QApplication.instance().exec_()


if __name__ == '__main__':
    # run this example as follows
    # python3 examples/Detector/exampleBoundingBoxNodes.py \
    #  --om_radius 0.03 --num_oms 4 --cluster_radius 1.5 \
    #  --num_strings 8 --world_radius 6 --z_margin 0.5 --num_clusters 6 --display 3d-pyqtgraph
    p = configargparse.get_argument_parser()
    p.add_argument('--om_radius', type=float, default=0.02, help='Radius of an OM')
    p.add_argument('--num_oms', type=int, default=3, help='Number of OMs along a string')
    p.add_argument('--om_z_spacing', type=float, default=0.05, help='Z spacing between OMs')
    p.add_argument('--cluster_radius', type=float, default=1, help='Radius of a cluster')
    p.add_argument('--num_strings', type=int, default=3, help='Number of strings in a cluster')
    p.add_argument('--world_radius', type=float, default=5, help='Radius of the world')
    p.add_argument('--z_margin', type=float, default=1, help='Z margin for the world')
    p.add_argument('--num_clusters', type=int, default=3, help='Number of clusters in the world')
    p.add_argument('--display', action='store_true',  help='Display option')
    opts = p.parse_args()

    # Calculate the world height based on the cluster height and the z margin
    cluster_height = opts.num_oms * (2 * opts.om_radius + opts.om_z_spacing) - opts.om_z_spacing
    opts.world_height = cluster_height + opts.z_margin

    world = createBoundingBoxNodes(opts)
    if opts.display:
        displayBoundingBoxNodes(world)
