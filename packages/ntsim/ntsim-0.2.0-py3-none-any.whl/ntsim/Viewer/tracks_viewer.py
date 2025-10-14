from ntsim.Viewer.viewer_base import viewerbase
import pyqtgraph.opengl as gl
import numpy as np
import pyqtgraph as pg
import ntsim.utils.pdg_colors as dict_colors
import logging

log = logging.getLogger('tracks_viewer')

class tracks_viewer(viewerbase):
    def configure(self, opts):
        self.options = opts
        self.widgets['geometry'].opts['distance'] = self.options.distance
        self.minL_param = self.options.min_length_for_tracks
        g = gl.GLGridItem()
        g.scale(*self.options.grid_scale)
        g.setDepthValue(10)
        if not self.widgets['geometry'] in self.docks['geometry'].widgets:
            self.docks['geometry'].addWidget(self.widgets['geometry'])
        self.tracks_list_static = []
        self.tracks_list_animated = {}

    def build_static_tracks(self):
        self.pos = {}
        self.t = {}
        self.particle_id = {}
        self.pdgid_colors = {}
        pg.setConfigOption('useOpenGL', True)
        
        for track in self.data:
            self.particle_id[track] = self.data[track]['pdgid']
            if self.particle_id[track][0] not in dict_colors.pdg_colors:
                continue
                
            self.pdgid_colors[track] = dict_colors.pdg_colors[self.particle_id[track][0]]
            x = self.data[track]['x_m']
            y = self.data[track]['y_m']
            z = self.data[track]['z_m']
            t = self.data[track]['time_ns']
            trajectory_length = np.sum(self.data[track]['step_length']) # REWRITE WITHOUT STEP_LENGTH ? 
            deltaR = np.sqrt((x[-1] - x[0])**2 + (y[-1] - y[0])**2 + (z[-1] - z[0])**2)
            if deltaR < self.minL_param and trajectory_length < self.minL_param: continue

            if np.absolute(self.particle_id[track][0]) in (12, 14, 16):
                dx = np.diff(x)
                dy = np.diff(y)
                dz = np.diff(z)
                distances = np.sqrt(dx**2 + dy**2 + dz**2).astype(int)
                
                x_segments = [np.linspace(x[i], x[i+1], d) for i, d in enumerate(distances)]
                y_segments = [np.linspace(y[i], y[i+1], d) for i, d in enumerate(distances)]
                z_segments = [np.linspace(z[i], z[i+1], d) for i, d in enumerate(distances)]
                t_segments = [np.linspace(t[i], t[i+1], d) for i, d in enumerate(distances)]

                self.pos[track] = np.column_stack((
                    np.concatenate(x_segments),
                    np.concatenate(y_segments),
                    np.concatenate(z_segments)
                ))
                self.t[track] = np.concatenate(t_segments)
            else:
                self.pos[track] = np.column_stack((x, y, z))
                self.t[track] = t
            
            sort_idx = np.argsort(self.t[track])
            self.t[track] = self.t[track][sort_idx]
            self.pos[track] = self.pos[track][sort_idx]
            
            line_width = 1 if np.absolute(self.particle_id[track][0]) in (12, 14, 16) else 2
            mode = 'lines' if line_width == 1 else 'line_strip'
            points = gl.GLLinePlotItem(
                pos=self.pos[track],
                color=pg.mkColor(self.pdgid_colors[track]),
                width=line_width,
                mode=mode
            )
            self.tracks_list_static.append(points)
            points.setVisible(False)
            self.widgets['geometry'].addItem(points)

    def build_animated_tracks(self):
        for frame in range(1, len(self.frames)):
            self.tracks_list_animated[frame] = []
            start_time = self.frames[frame-1]
            end_time = self.frames[frame]
            
            for track in self.pos:  
                t_track = self.t[track]
                start_idx = np.searchsorted(t_track, start_time, side='left')
                end_idx = np.searchsorted(t_track, end_time, side='right')
                
                if start_idx >= end_idx:
                    continue
                
                pos_t = self.pos[track][start_idx:end_idx]
                
                if start_idx > 0 and not np.array_equal(pos_t[0], self.pos[track][start_idx-1]):
                    pos_t = np.vstack([self.pos[track][start_idx-1], pos_t])
                
                line_width = 1 if np.absolute(self.particle_id[track][0]) in (12, 14, 16) else 2
                graph_track = gl.GLLinePlotItem(
                    pos=pos_t,
                    color=pg.mkColor(self.pdgid_colors[track]),
                    width=line_width,
                    mode='lines' if line_width == 1 else 'line_strip'
                )
                self.tracks_list_animated[frame].append(graph_track)
                graph_track.setVisible(False)
                self.widgets['geometry'].addItem(graph_track)

    def display_static(self, vis=False):
        self.setVisible_tracks_static(vis)

    def setVisible_tracks_static(self, vis):
        for track in self.tracks_list_static:
            track.setVisible(vis)

    def clean_static(self):
        for track in self.tracks_list_static:
            self.widgets['geometry'].removeItem(track)
        self.tracks_list_static = []

    def clean_animated(self):
        for frame in self.tracks_list_animated:
            for track in self.tracks_list_animated[frame]:
                self.widgets['geometry'].removeItem(track)
        self.tracks_list_animated = {}

    def clean_view(self):
        self.clean_static()
        self.clean_animated()

    def setVisible_tracks_animated(self, vis):
        for frame in self.tracks_list_animated:
            for track in self.tracks_list_animated[frame]:
                track.setVisible(vis)

    def display_frame(self, frame, vis):
        if frame == 0:
            self.setVisible_tracks_animated(False)
            return
            
        for f in range(frame):
            for track in self.tracks_list_animated.get(f, []):
                track.setVisible(False)
                
        for track in self.tracks_list_animated.get(frame, []):
            track.setVisible(vis)
            