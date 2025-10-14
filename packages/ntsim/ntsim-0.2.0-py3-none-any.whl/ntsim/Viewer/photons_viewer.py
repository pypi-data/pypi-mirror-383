from ntsim.Viewer.viewer_base import viewerbase
import pyqtgraph.opengl as gl
import numpy as np
from pyqtgraph.Qt import QtGui
import pyqtgraph as pg
from ntsim.Propagators.RayTracers.utils import position_numba, interpolate_numba


import logging
log = logging.getLogger('photons_viewer')
class photons_viewer(viewerbase):
    def configure(self,opts):
        self.options = opts
        self.widgets['geometry'].opts['distance'] = self.options.distance
        g = gl.GLGridItem()
        g.scale(*self.options.grid_scale)
        g.setDepthValue(10)  # draw grid after surfaces since they may be translucent
        # check if this widget is not added already
        if not self.widgets['geometry'] in self.docks['geometry'].widgets:
            self.docks['geometry'].addWidget(self.widgets['geometry'])
        # add photons object
        self.tracks_obj_static = []
        self.tracks_obj_animated = {}


    def display_static(self,vis=False):
        if len(self.tracks_obj_static):
            for item in self.tracks_obj_static:
                item.setVisible(vis)
            return
#            self.clean_static()
        x = self.data.position_m[:,:,0]
        y = self.data.position_m[:,:,1]
        z = self.data.position_m[:,:,2]
        t = self.data.time_ns
        pos = np.array([x[:,:], y[:,:], z[:,:]]).T
#        self.widgets['geometry'].show() # This is necessary since otherwise a segfault 11
        for step in range(self.data.scattering_steps):
            travel_time = self.data.time_ns[step,:]-self.data.time_ns[0,:]
            log.debug(f'travel_time={travel_time}')
            colors = self.get_absorption_colors(travel_time,self.data.absorption_time_ns)
            points = gl.GLScatterPlotItem(pos=pos[:,step,:], color = colors, size=1, pxMode=False)
            points.setVisible(vis)
            self.tracks_obj_static.append(points)
            self.widgets['geometry'].addItem(self.tracks_obj_static[step])

    def clean_static(self):
        if len(self.tracks_obj_static):
            for step in range(self.data.scattering_steps):
                self.widgets['geometry'].removeItem(self.tracks_obj_static[step])
            self.tracks_obj_static = []

    def clean_animated(self):
        for frame in self.tracks_obj_animated.keys():
            self.widgets['geometry'].removeItem(self.tracks_obj_animated[frame])
        self.tracks_obj_animated = {}

    def get_absorption_colors(self, t, ta):
        colors = np.zeros((len(t), 4))
        valid_mask = (ta > 0) & (t >= 0)

        if np.any(valid_mask):
            weight = 1.0 - np.exp(-t[valid_mask] / ta[valid_mask])

            cmap = pg.colormap.get('CET-R3')
            colors_valid = cmap.map(weight) / 255.0
            colors_valid[:, 3] = 1.0

            colors[valid_mask] = colors_valid

        return colors

    def clean_view(self):
        self.clean_static()
        self.clean_animated()

    def setVisible_photons_static(self,vis):
        for item in self.tracks_obj_static:
            item.setVisible(vis)

    def setVisible_photons_animated(self,vis):
        for frame in self.tracks_obj_animated:
            self.tracks_obj_animated[frame].setVisible(vis)

    def display_frame(self,frame,vis):
        # make all other frames invisible except the requisted frame
        for f in self.tracks_obj_animated:
            if f == frame:
                self.tracks_obj_animated[f].setVisible(vis)
            else:
                self.tracks_obj_animated[f].setVisible(False)
        # check if this frame is already computed
        if frame not in self.tracks_obj_animated:
            # this frame is not found. compute it, add to self.tracks_obj_animated

#            self.clean_view()
#            self.setVisible_photons_static(False)
            time_tick = np.array([self.frames[frame]])
            x_interp, y_interp, z_interp  = position_numba(self.data.position_m,self.data._t_ns,time_tick)
            pos = np.column_stack([x_interp, y_interp, z_interp])
            travel_time = self.frames[frame]-self.data.time_ns[0,:]
            colors = self.get_absorption_colors(travel_time,self.data.absorption_time_ns)
            mask = np.isfinite(pos[:, 0])
            mask = np.all(np.isfinite(pos), axis=1)
            pos    = pos[mask]
            colors = colors[mask]
            size = np.ones((pos.shape[1]))
            total  = len(pos)
            #log.debug(f'travel_time={travel_time[None,:][mask]}')
            if total:
                log.debug(f'frame={frame}, colors={colors}')
                self.tracks_obj_animated[frame] = gl.GLScatterPlotItem(pos=pos, color = colors, size=1, pxMode=False)
                self.widgets['geometry'].addItem(self.tracks_obj_animated[frame])
                self.tracks_obj_animated[frame].setVisible(vis)
