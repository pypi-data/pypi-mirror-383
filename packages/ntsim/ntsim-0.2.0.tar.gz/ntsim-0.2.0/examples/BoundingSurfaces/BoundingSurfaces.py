import numpy as np
import configargparse

from ntsim.BoundingSurfaces import *

def SetBoundingSurfaces(opts):
    
    def give_surface(opts, positions, label, shift):
        surfaces = []
        
        if label == 'Box':
            for i in range(3):
                for j in range(3):
                    for k in range(3):
                        surfaces.append(BoundingBox(shift,positions[i,j,k],opts.Box.width_x_m,opts.Box.width_y_m,opts.Box.height_m))
                        shift += 1
        elif label == 'Cylinder':
            for i in range(3):
                for j in range(3):
                    for k in range(3):
                        surfaces.append(BoundingCylinder(shift,positions[i,j,k],opts.Cylinder.radius_m,opts.Cylinder.height_m))
                        shift += 1
        elif label == 'Sphere':
            for i in range(3):
                for j in range(3):
                    for k in range(3):
                        surfaces.append(BoundingSphere(shift,positions[i,j,k],opts.Sphere.radius_m))
                        shift += 1
        return surfaces
    
    surfaces = {}
    
    for surface_name in opts.nesting_doll:
        surfaces[surface_name] = []
    
    positions = np.zeros(shape=(3,3,3,3))
    
    for i, row in enumerate([-1,0,1]):
        for j, column in enumerate([-1,0,1]):
            for k, z in enumerate([-1,0,1]):
                positions[i,j,k][0] = opts.center_position_m[0] + column*opts.distance_among_dolles
                positions[i,j,k][1] = opts.center_position_m[1] + row*opts.distance_among_dolles
                positions[i,j,k][2] = opts.center_position_m[2] + z*opts.distance_among_dolles
    
    shift = 0
    
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for n, surface_name in enumerate(opts.nesting_doll):
                    if surface_name == 'Box':
                        surface = BoundingBox(shift,positions[i,j,k],opts.Box.width_x_m,opts.Box.width_y_m,opts.Box.height_m)
                    elif surface_name == 'Cylinder':
                        surface = BoundingCylinder(shift,positions[i,j,k],opts.Cylinder.radius_m,opts.Cylinder.height_m)
                    elif surface_name == 'Sphere':
                        surface = BoundingSphere(shift,positions[i,j,k],opts.Sphere.radius_m)
                    if n != 0:
#                        print(surfaces[opts.nesting_doll[n-1]])
                        surfaces[opts.nesting_doll[n-1]][-1].add_child(surface)
                    surfaces[surface_name].append(surface)
                    shift += 1
    
    for surface in reversed(surfaces):
        for instance in surfaces[surface]:
            instance.update_critical_boundaries()
#            print(instance.quantities)
    
    return surfaces
        

def displayBoundingBoxNodes(surfaces):
    
    from PyQt5.QtWidgets import QApplication
    from pyqtgraph.opengl import GLViewWidget, GLAxisItem
    from pyqtgraph.Qt import QtGui, QtCore
    from PyQt5.QtGui import QColor, QVector3D
    import pyqtgraph.opengl as gl
    
    def draw_box(node, color):
        quantities = node.quantities
        position = quantities[:3]
        width_x = quantities[3]
        width_y = quantities[4]
        height = quantities[5]
        size = QVector3D(2*width_x, 2*width_y, 2*height)
        box = gl.GLBoxItem(size=size, color=QColor(128, 0, 128, 50), glOptions='opaque')
        box.translate(*np.array(position-[width_x,width_y,height]))
        return box
    
    def draw_cylinder(node, color):
        quantities = node.quantities
        position = quantities[:3]
        radius = quantities[3]
        height = quantities[4]
        cylinder = gl.GLMeshItem(meshdata=gl.MeshData.cylinder(rows=10, cols=20), color=color, shader='shaded', glOptions='additive')
        cylinder.scale(radius, radius, 2*height)
        cylinder.translate(position[0], position[1], position[2]-height)
        return cylinder
    
    def draw_sphere(node, color):
        quantities = node.quantities
        position = quantities[:3]
        radius = quantities[3]
        sphere = gl.GLMeshItem(meshdata=gl.MeshData.sphere(rows=10, cols=20), color=color, shader='shaded', glOptions='additive')
        sphere.scale(radius, radius, radius)
        sphere.translate(position[0], position[1], position[2])
        return sphere
    
    app = QApplication([])
    view = GLViewWidget()
    view.setBackgroundColor('black')
    view.show()
    
    axis = GLAxisItem()
    view.addItem(axis)
    
    bounding_box_items = []
    
    for surface in surfaces:
        if surface == 'Box':
            for instance in surfaces[surface]:
                surface_item = draw_box(instance, (1, 1, 1, 0.2))
                view.addItem(surface_item)
        if surface == 'Cylinder':
            for instance in surfaces[surface]:
                surface_item = draw_cylinder(instance, (1, 1, 1, 0.2))
                view.addItem(surface_item)
        if surface == 'Sphere':
            for instance in surfaces[surface]:
                surface_item = draw_sphere(instance, (1, 1, 1, 0.2))
                view.addItem(surface_item)
    
    for item in bounding_box_items:
        item.setVisible(True)
    
    app.exec_()

if __name__ == '__main__':
    from ntsim.utils.arguments_handling import NestedNamespace
    parser = configargparse.get_argument_parser()
    parser.add('--nesting_doll', type=str, nargs=3, default=['Box','Cylinder','Sphere'],help='')
    parser.add('--Box.width_x_m', type=float, default=1., help='')
    parser.add('--Box.width_y_m', type=float, default=1., help='')
    parser.add('--Box.height_m', type=float, default=1., help='')
    parser.add('--Cylinder.radius_m', type=float, default=1., help='')
    parser.add('--Cylinder.height_m', type=float, default=1., help='')
    parser.add('--Sphere.radius_m', type=float, default=1., help='')
    parser.add('--center_position_m', type=float, default=np.array([0.,0.,0.]), help='')
    parser.add('--distance_among_dolles', type=float, default=100., help='')
    
    opts = parser.parse_args(namespace=NestedNamespace())
    
    surfaces = SetBoundingSurfaces(opts)
    
    displayBoundingBoxNodes(surfaces)