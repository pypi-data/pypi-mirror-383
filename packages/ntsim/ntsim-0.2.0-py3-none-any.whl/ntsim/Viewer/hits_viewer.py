from ntsim.Viewer.viewer_base import viewerbase
import pyqtgraph.opengl as gl
import numpy as np
from pyqtgraph.Qt import QtGui
import pyqtgraph as pg

import logging
log = logging.getLogger('hits_viewer')

clickedPen = pg.mkPen('b', width=2)
lastClicked = []

def clicked(plot, points):
    global lastClicked
    for p in lastClicked:
        p.resetPen()
    print("clicked points", points)
    for p in points:
        p.setPen(clickedPen)
    lastClicked = points

class hits_viewer(viewerbase):
    def configure(self,opts):
        self.options = opts
        self.widgets['geometry'].opts['distance'] = self.options.distance
        g = gl.GLGridItem()
        g.scale(*self.options.grid_scale)
        g.setDepthValue(10)  # draw grid after surfaces since they may be translucent
        # check if this widget is not added already
        if not self.widgets['geometry'] in self.docks['geometry'].widgets:
            self.docks['geometry'].addWidget(self.widgets['geometry'])
        self.om_list = {}
        self.om_id_list = {}
        self.om_z_list = {}
        self.om_positions   = {}
        self.om_radius = {}
        self.colormap = pg.colormap.get('CET-R3')

    def hits_analysis(self):
        self.hits_time_histos = {}
        self.hits_cumulative = {}
        self.n_om_hitted = 0 # number of hitted OM with npe above opts.threshold
        self.npe_total = 0   # total npe above opts.threshold
        self.npe_max   = 0   # maximum npe in OM
        evtHeader = self.data['event_header']
        photons_sampling_weight = evtHeader['photons_sampling_weight']
#        log.debug(f'frames={self.frames}')
        hits = self.data['hits']
        #print(hits)
        for i_om,uid in enumerate(hits):
            weights = hits[uid]['self_weight']*hits[uid]['w_noabs']*hits[uid]['pde']*hits[uid]['gel_transmission']*hits[uid]['angular_dependence'] #*photons_sampling_weight*om_area_weight
            time_ns = hits[uid]['time_ns']
            self.hits_time_histos[uid], bin_edges = np.histogram(time_ns,bins=self.frames,weights=weights)
            
            hits_cumulative = np.cumsum(self.hits_time_histos[uid])
#            log.debug(f'uid={uid}, hits time.ns = {hits.time_ns}')
        #    self.hits_time_histos[uid], bin_edges = np.histogram(hits.time_ns,bins=self.frames,weights=weights)
        #    hits_cumulative = np.cumsum(self.hits_time_histos[uid])
#            print(uid, '\t', hits_cumulative, '\t', self.data['hits'][uid]['cluster'])
#            log.debug(f'hits_cumulative={hits_cumulative}')
            n_total = hits_cumulative[-1]
            if n_total>=self.npe_max:
                self.npe_max = n_total
            if n_total>= self.options.threshold:
                self.n_om_hitted+=1
                self.npe_total+=n_total
                self.hits_cumulative[uid] = hits_cumulative
        
        if 'geom' in self.data:
            self.read_geometry()
        self.build_om_list()
        self.histogram_z()

    def histogram_id(self, scale_factor = 2):
        om_colors = {}
        for frame in range(len(self.frames) - 1):
            self.om_id_list[frame] = []
            colors = np.zeros((len(self.hits_cumulative),4), dtype=np.float32)
            om_id = np.zeros(len(self.hits_cumulative), dtype = np.float32)
            r = np.zeros(len(self.hits_cumulative), dtype=np.float32)
            i_om = 0
            for uid in self.hits_cumulative:
                rmin = self.om_radius[uid]
                npe  = self.hits_cumulative[uid][frame]
                if self.npe_max>self.options.threshold:
                    om_id[i_om] = uid
                    r_uid = scale_factor*(rmin + (self.options.rmax-rmin)/np.log(2.0)*np.log(1.0+npe/self.npe_max))
                    if uid not in om_colors:
                        color = self.colormap.map(1e0*frame/(len(self.frames)-1))/255
                        color[3] = 1.0
                        om_colors[uid] = color
                    r[i_om] =r_uid
                    colors[i_om] = om_colors[uid]
                    i_om+=1
            self.om_x_list[frame] = om_id
            color_frame = self.colormap.map(1e0*frame/(len(self.frames)-1))
            self.hist_om_x = (self.om_x_list, self.frames[:-1])
            hist_hits_id = pg.ScatterPlotItem(np.tile(frame, np.shape(self.hist_om_x[0][frame][self.hist_om_x[0][frame] != 0])), self.hist_om_x[0][frame][self.hist_om_x[0][frame] != 0],size=r[r != 0], pen=pg.mkPen(None), brush=pg.mkBrush(color_frame))
            self.om_id_list[frame] = hist_hits_id
            hist_hits_id.setPointsVisible(False)
#            self.hist_hits_x.addPoints(np.tile(frame, np.shape(self.hist_om_x[0][frame][self.hist_om_x[0][frame] != 0])), self.hist_om_x[0][frame][self.hist_om_x[0][frame] != 0])
            self.widgets['histograms.response'].addItem(hist_hits_id)

    def histogram_z(self, scale_factor = 2):
        om_colors = {}
        for frame in range(len(self.frames) - 1):
            self.om_z_list[frame] = []
#            colors = np.zeros((len(self.hits_cumulative),4), dtype = np.float32)
#            om_z = np.zeros(len(self.hits_cumulative), dtype = np.float32)
#            r = np.zeros(len(self.hits_cumulative), dtype=np.float32)
            colors = np.zeros((len(self.hits_time_histos),4), dtype = np.float32)
            om_z = np.zeros(len(self.hits_time_histos), dtype = np.float32)
            r = np.zeros(len(self.hits_time_histos), dtype=np.float32)
            i_om = 0
#            for uid in self.hits_cumulative:
            for uid in self.hits_time_histos:
                rmin = self.om_radius[uid]
#                npe  = self.hits_cumulative[uid][frame]
                npe  = self.hits_time_histos[uid][frame]
                if npe > self.options.threshold:
                    om_z[i_om] = self.om_positions[uid][2]
                    r_uid = scale_factor * (rmin + (self.options.rmax - rmin) / np.log(2.0) * np.log(1.0 + npe / self.npe_max))
                    if uid not in om_colors:
                        color = self.colormap.map(1e0 * frame/(len(self.frames)-1)) / 255
                        om_colors[uid] = color
                    r[i_om] = r_uid
                    colors[i_om] = om_colors[uid]
                    i_om += 1
            color_frame = self.colormap.map(1e0 * frame / (len(self.frames) - 1))
            x = np.tile(self.frames[frame], np.shape(om_z))
            y = om_z
            hist_hits_z = pg.ScatterPlotItem(pen = pg.mkPen(None), brush=pg.mkBrush(color_frame), hoverable=True, hoverPen=pg.mkPen('g'))
            hist_hits_z.addPoints(x = x, y = y, size = r, data = r)
            self.om_z_list[frame] = hist_hits_z
            hist_hits_z.sigClicked.connect(clicked)
            hist_hits_z.setPointsVisible(False)
            self.widgets['histograms.response'].addItem(hist_hits_z)


    def build_om_list(self,scale_factor=2):
        # based on hits_cumulative we build OM list for every time frame.
        # The last time frame corresponds to the static picture

        # each OM has a color according to the earliest hit above the threshold
        # make dict of uid for which the color is determined
        om_colors = {}
        # iterate over hitted OM
        for frame in range(len(self.frames)-1):
            self.om_list[frame] = []

            colors = np.zeros((len(self.hits_cumulative),4), dtype=np.float32)
            pos = np.zeros((len(self.hits_cumulative),3), dtype=np.float32)
            r   = np.zeros(len(self.hits_cumulative), dtype=np.float32)

            i_om=0
            for uid in self.hits_cumulative:
                rmin = self.om_radius[uid]
                npe  = self.hits_cumulative[uid][frame]

                if npe>self.options.threshold:
                    r_uid = scale_factor*(rmin + (self.options.rmax-rmin)/np.log(2.0)*np.log(1.0+npe/self.npe_max))
                    if uid not in om_colors:
                        #
                        color = self.colormap.map(1e0*frame/(len(self.frames)-1))/255
                        color[3] = 1.0
                        om_colors[uid] = color
                    r[i_om] =r_uid
                    pos[i_om] = self.om_positions[uid]
                    colors[i_om] = om_colors[uid]
                    i_om+=1
            opticalModules = gl.GLScatterPlotItem(pos=pos, color = colors, size=r, pxMode=False)
#            log.debug(f'colors={colors}, size={r}')
            self.om_list[frame] = opticalModules
            opticalModules.setVisible(False)
            self.widgets['geometry'].addItem(opticalModules)
            log.debug(f'frame={frame}, number of om: {i_om}')
    '''
    def read_geometry(self):
        (n_clusters,n_strings,n_om,n_vars) = self.data['geom'].shape
        for icluster in range(n_clusters):
            for istring in range(n_strings):
                for iom in range(n_om):
                    vars = self.data['geom'][icluster,istring,iom]
                    uid = vars[0]
                    x   = vars[1]
                    y   = vars[2]
                    z   = vars[3]
                    prod_radius = vars[7]
                    true_radius = vars[8]
                    self.om_positions[uid]   = np.array([x,y,z])
                    self.om_prod_radius[uid] = prod_radius
                    self.om_true_radius[uid] = true_radius
    '''
    def read_geometry(self):
        detector_uid = self.data['geom']['detector_uid']
        position = self.data['geom']['position']
        radius = self.data['geom']['radius']
        for i_om,uid in enumerate(detector_uid):
            self.om_positions[uid] = (position[i_om,0],position[i_om,1],position[i_om,2])
            self.om_radius[uid] = radius[i_om]

    def display_static(self,vis=False):
        self.setVisible_hits_static(vis)

    def display_frame(self,frame,vis):
        log.debug(f'display_frame number {frame}')
        self.setVisible_hits_static(False)
        for f in self.om_list:
            if f == frame:
                self.om_list[f].setVisible(vis)
            else:
                self.om_list[f].setVisible(False)
        for f in self.om_list:
            if f <= frame:
                self.om_z_list[f].setPointsVisible(vis)
            else:
                self.om_z_list[f].setPointsVisible(False)

    def setVisible_hits_static(self,vis):
        if len(self.om_list):
            opticalModules = self.om_list[len(self.frames)-2]
            opticalModules.setVisible(vis)
            hist_hits_id = [self.om_z_list[key].setPointsVisible(vis) for key in self.om_z_list]

    def setVisible_hits_animated(self,vis):
        if len(self.om_list) and len(self.om_z_list):
            for frame in self.om_list:
                self.om_list[frame].setVisible(vis)
                self.om_z_list[frame].setPointsVisible(vis)

    def clean_view(self):
        for frame, item in self.om_list.items():
            self.widgets['geometry'].removeItem(item)
        for frame, item in self.om_z_list.items():
            self.widgets['histograms.response'].removeItem(item)
        self.om_list = {}
        self.om_z_list = {}
