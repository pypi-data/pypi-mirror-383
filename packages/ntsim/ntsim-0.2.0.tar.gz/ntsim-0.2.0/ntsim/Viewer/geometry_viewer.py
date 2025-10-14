from ntsim.Viewer.viewer_base import viewerbase
import pyqtgraph.opengl as gl
import numpy as np
from pyqtgraph.Qt import QtGui

import logging
log = logging.getLogger('geometry_viewer')
class geometry_viewer(viewerbase):
    def configure(self,opts):
        self.options = opts
        self.widgets['geometry'].opts['distance'] = self.options.distance
        g = gl.GLGridItem()
        g.scale(*self.options.grid_scale)
        g.setDepthValue(10)  # draw grid after surfaces since they may be translucent
        # check if this widget is not added already
        if not self.widgets['geometry'] in self.docks['geometry'].widgets:
            self.docks['geometry'].addWidget(self.widgets['geometry'])
        ax = gl.GLAxisItem()
#        self.widgets['geometry'].addItem(ax)
        self.widgets['geometry'].addItem(g)
        self.om_positions   = {}
        self.om_normals     = {}
        self.om_prod_radius = {}
        self.om_true_radius = {}
        self.om_list = []
        self.bb_list = []

    def display_static(self):
        self.display_om()
        self.display_bounding_boxes()

    def display_bounding_boxes(self,vis=False):
        if len(self.bb_list):
            self.setVisible_bb(vis)
            return
        if self.data is None:
            return
        bb_entries = self.data['Bounding_Surfaces']
        for entry in bb_entries:
            self.draw_shape(entry, vis)
        
    def clear_om(self):
        for item in self.om_list:
            self.widgets['geometry'].removeItem(item)
        self.om_list = []

    def clear_bounding_boxes(self):
        for item in self.bb_list:
            self.widgets['geometry'].removeItem(item)
        self.bb_list = []

    def setVisible_om(self,vis):
        for item in self.om_list:
            item.setVisible(vis)

    def setVisible_bb(self,vis):
        for item in self.bb_list:
            item.setVisible(vis)
    '''
    def display_om(self,vis=False):
        if len(self.om_list):
            self.setVisible_om(vis)
            return
        (n_clusters,n_strings,n_om,n_vars) = self.data['geom'].shape
        for icluster in range(n_clusters):
            for istring in range(n_strings):
                for iom in range(n_om):
                    vars = self.data['geom'][icluster,istring,iom]
                    uid = vars[0]
                    x   = vars[1]
                    y   = vars[2]
                    z   = vars[3]
                    dir_x = vars[4]
                    dir_y = vars[5]
                    dir_z = vars[6]
                    prod_radius = vars[7]
                    true_radius = vars[8]
                    self.om_positions[uid]   = np.array([x,y,z])
                    self.om_normals[uid]     = np.array([dir_x,dir_y,dir_z])
                    self.om_prod_radius[uid] = prod_radius
                    self.om_true_radius[uid] = true_radius
                    #
                    sphere = gl.MeshData.sphere(rows=4, cols=8, radius=prod_radius)
                    opticalModule = gl.GLMeshItem(meshdata=sphere,smooth=False,drawFaces=False, drawEdges=True,color=[0.7, 0.7, 0.9, 0.8])
                    self.widgets['geometry'].show() # This is necessary since otherwise a segfault 11
                    self.widgets['geometry'].addItem(opticalModule)
                    # make spot instead of sphere
#                    opticalModule = gl.GLScatterPlotItem(pos=self.om_positions[uid], size=true_radius, color=(0.7, 0.7, 0.9, 0.8), pxMode=True)
                    self.om_list.append(opticalModule)
#                    self.widgets['geometry'].addItem(opticalModule)
                    opticalModule.translate(x,y,z)
                    opticalModule.setVisible(vis)
    '''
    
    def display_om(self,vis=False):
        if self.data is None:
            return
        detector_uid = self.data['Geometry']['detector_uid']
        position = self.data['Geometry']['position']
        radius = self.data['Geometry']['radius']
        for i_om,uid in enumerate(detector_uid):
            sphere = gl.MeshData.sphere(rows=4, cols=8, radius=radius[i_om])
            opticalModule = gl.GLMeshItem(meshdata=sphere,smooth=False,drawFaces=False, drawEdges=True,color=[0.7, 0.7, 0.9, 0.8])
            self.widgets['geometry'].show() # This is necessary since otherwise a segfault 11
            self.widgets['geometry'].addItem(opticalModule)
            self.om_list.append(opticalModule)
            opticalModule.translate(position[i_om,0],position[i_om,1],position[i_om,2])
            opticalModule.setVisible(vis)
        return

        if len(self.om_list):
            self.setVisible_om(vis)
            return
        n_clusters = len(np.unique(self.data['geom'][:,1]))
        n_strings  = len(np.unique(self.data['geom'][:,2]))
        n_om       = len(np.unique(self.data['geom'][:,0]))
        for icluster in range(n_clusters):
            for istring in range(n_strings):
                mask_cluster    = self.data['geom'][:,1] == icluster
                mask_subcluster = self.data['geom'][:,2] == istring
                mask            = mask_cluster & mask_subcluster
                for iom in range(n_om):
                    vars = self.data['geom'][mask][iom]
                    uid = vars[0]
                    x   = vars[3]
                    y   = vars[4]
                    z   = vars[5]
                    dir_x = vars[9]
                    dir_y = vars[10]
                    dir_z = vars[11]
                    prod_radius = vars[13]
                    true_radius = vars[12]
                    self.om_positions[uid]   = np.array([x,y,z])
                    self.om_normals[uid]     = np.array([dir_x,dir_y,dir_z])
                    self.om_prod_radius[uid] = prod_radius
                    self.om_true_radius[uid] = true_radius
                    #
                    sphere = gl.MeshData.sphere(rows=4, cols=8, radius=prod_radius)
                    opticalModule = gl.GLMeshItem(meshdata=sphere,smooth=False,drawFaces=False, drawEdges=True,color=[0.7, 0.7, 0.9, 0.8])
                    self.widgets['geometry'].show() # This is necessary since otherwise a segfault 11
                    self.widgets['geometry'].addItem(opticalModule)
                    # make spot instead of sphere
#                    opticalModule = gl.GLScatterPlotItem(pos=self.om_positions[uid], size=true_radius, color=(0.7, 0.7, 0.9, 0.8), pxMode=True)
                    self.om_list.append(opticalModule)
#                    self.widgets['geometry'].addItem(opticalModule)
                    opticalModule.translate(x,y,z)
                    opticalModule.setVisible(vis)
    
    def display_bounding_boxes_test(self):
        gx = gl.GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-10, 0, 0)
        self.widgets['geometry'].addItem(gx)
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)

        gy.translate(0, -10, 0)
        self.widgets['geometry'].addItem(gy)
        gz = gl.GLGridItem()
        gz.translate(0, 0, -10)
        self.widgets['geometry'].addItem(gz)

    def draw_shape(self,bb_entry,vis):
        params = bb_entry[0]
        shape_type = bb_entry[-1].decode('utf-8')

        if shape_type == 'BoundingCylinder':
            self.draw_cylinder(params, vis)
        elif shape_type == 'BoundingSphere':
            self.draw_sphere(params, vis)
        elif shape_type == 'BoundingBox':
            self.draw_box(params, vis)
        else:
            log.warning(f"Unknown body type: {shape_type}")

    def draw_cylinder(self, params, vis):
        position = params[:3]
        radius = params[3]
        height = params[4]
        cylinder = gl.GLMeshItem(meshdata=gl.MeshData.cylinder(rows=10, cols=20), 
                                 smooth=False, drawFaces=False, drawEdges=True, color=[1, 0, 0, 0.3])
        cylinder.scale(radius, radius, 2*height)
        cylinder.translate(position[0], position[1], position[2]-height)

        self.widgets['geometry'].addItem(cylinder)
        self.bb_list.append(cylinder)
        cylinder.setVisible(vis)
        
    def draw_sphere(self, params, vis):
        position = params[:3]
        radius = params[3]
        sphere = gl.GLMeshItem(meshdata=gl.MeshData.sphere(rows=10, cols=20), 
                               smooth=False, drawFaces=False, drawEdges=True, color=[1, 0, 0, 0.3])
        sphere.scale(radius, radius, radius)
        sphere.translate(position[0], position[1], position[2])
        self.widgets['geometry'].addItem(sphere)
        self.bb_list.append(sphere)
        sphere.setVisible(vis)

    def draw_box(self, params, vis):
        position = params[:3]
        width = params[3]
        length = params[4]
        height = params[5]
        box = gl.GLBoxItem(color=[1, 0, 0, 0.3])
        box.setSize(width, length, height)
        box.translate(*np.array(position) - np.array([width, length, height]) / 2)
        self.widgets['geometry'].addItem(box)
        self.bb_list.append(box)
        box.setVisible(vis)

    def display_frame(self,frame):
        return
