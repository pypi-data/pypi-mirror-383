import pyqtgraph as pg
import pyqtgraph.opengl as gl
import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QGridLayout, QLabel, QVBoxLayout,
                            QMainWindow, QWidget, QOpenGLWidget, QPushButton, QRadioButton)
#from PyQt6.QtWidgets import (QApplication, QFileDialog, QGridLayout, QLabel, QVBoxLayout,
#                            QMainWindow, QWidget, QPushButton, QRadioButton)
from pyqtgraph.dockarea import *
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import LayoutWidget
import pyqtgraph.console
import pyqtgraph.parametertree as ptree
import pyqtgraph.console

import numpy as np
import os
from collections import OrderedDict

from ntsim.Viewer.viewer_base import viewerbase
from ntsim.Viewer.geometry_viewer import geometry_viewer
from ntsim.Viewer.photons_viewer import photons_viewer
from ntsim.Viewer.hits_viewer import hits_viewer
from ntsim.Viewer.tracks_viewer import tracks_viewer
from ntsim.Viewer.legend_viewer import GLPainterItem
from ntsim.Viewer.histograms_viewer import histograms_viewer
from ntsim.Viewer.intersection2D_viewer import intersection_viewer

from ntsim.IO.h5Reader import h5Reader
import logging
log=logging.getLogger('h5viewer')
logformat='[%(name)20s ] %(levelname)8s: %(message)s'
logging.basicConfig(format=logformat)

import numpy as np

def open_file_dialog()->str:
    return QFileDialog.getOpenFileName(caption='Select data file', filter='*.h5')[0]
    
class h5Viewer(QMainWindow):
    sigKeyPress = QtCore.pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.initStateWidget()
        self.initReader()
        self.initDocks()
        self.initWidgets()
        self.createViewers()

    def init(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)
        self.dockPlacement()
        self.makeButtons()
        layout.addWidget(self.dockarea)
        self.initTimer()
        if not self.openFile():
            self.FileDialog()


    def initStateWidget(self):
        self.state_dict          = OrderedDict()
        self.state_hits          = OrderedDict()
        self.state_tracks        = OrderedDict()
        self.state_photons       = OrderedDict()
        self.state_cascades      = OrderedDict()
        self.state_tree          = pg.DataTreeWidget()
        self.state_tree_hits     = pg.DataTreeWidget()
        self.state_tree_tracks   = pg.DataTreeWidget()
        self.state_tree_photons  = pg.DataTreeWidget()
        self.state_tree_cascades = pg.DataTreeWidget()

    def initDocks(self):
        self.dockarea = DockArea()
        self.docks = {}
        self.docks["geometry"]  = Dock("geometry", size=(300,300))
        self.docks["histograms.response"]  = Dock("histograms.response", size=(200,300))
        self.docks["primary_energy"]  = Dock("primary energy", size=(200,300))
        self.docks["particle_legend"] = Dock("particle_legend", size=(200,300))
        self.docks["distributions"]   = Dock("distributions", size=(200,300))
        self.docks["events"]          = Dock("events", size=(10,10))
        self.docks["production"]      = Dock("production", size=(50,100))
        self.docks["tracks_info"]     = Dock("tracks info", size=(50,100))
        self.docks["particles_info"]  = Dock("particles info", size=(50,100))
        self.docks["photons_info"]    = Dock("photons info", size=(50,100))
        self.docks["hits_info"]       = Dock("hits info", size=(50,100))

#        self.docks["iconsole"]   = Dock("interactive console", size=(50,100))
        self.docks["Parameters"]= Dock("Parameters", size=(10,120))

    def addDocksToArea(self, dock_area):
        dock_area.addDock(self.docks["geometry"],'top')
        dock_area.addDock(self.docks["histograms.response"],'right',self.docks["geometry"],closable=True)
        dock_area.addDock(self.docks["primary_energy"],'below',self.docks["histograms.response"],closable=True)
        dock_area.addDock(self.docks["particle_legend"],'below',self.docks["histograms.response"],closable=True)
        dock_area.addDock(self.docks["distributions"],'below',self.docks["histograms.response"],closable=True)

        dock_area.addDock(self.docks["production"],'bottom')
        dock_area.addDock(self.docks["tracks_info"],'below',self.docks["production"])
        dock_area.addDock(self.docks["particles_info"],'below',self.docks["tracks_info"])
        dock_area.addDock(self.docks["photons_info"],'below',self.docks["particles_info"])
        dock_area.addDock(self.docks["hits_info"],'below',self.docks["photons_info"])

#        dockarea.addDock(self.docks["iconsole"],'right',self.docks["console"], closable=True)
        dock_area.addDock(self.docks["Parameters"],'right',self.docks["production"])
        dock_area.addDock(self.docks["events"],'right',self.docks["Parameters"])

    def dockPlacement(self):
        self.dockarea.addDock(self.docks["geometry"],'top')
        self.dockarea.addDock(self.docks["histograms.response"],'right',self.docks["geometry"],closable=True)
        self.dockarea.addDock(self.docks["primary_energy"],'below',self.docks["histograms.response"],closable=True)
        self.dockarea.addDock(self.docks["particle_legend"],'below',self.docks["histograms.response"],closable=True)
        self.dockarea.addDock(self.docks["distributions"],'below',self.docks["histograms.response"],closable=True)

        self.dockarea.addDock(self.docks["production"],'bottom')
        self.dockarea.addDock(self.docks["tracks_info"],'below',self.docks["production"])
        self.dockarea.addDock(self.docks["particles_info"],'below',self.docks["tracks_info"])
        self.dockarea.addDock(self.docks["photons_info"],'below',self.docks["particles_info"])
        self.dockarea.addDock(self.docks["hits_info"],'below',self.docks["photons_info"])

#        self.dockarea.addDock(self.docks["iconsole"],'right',self.docks["console"], closable=True)
        self.dockarea.addDock(self.docks["Parameters"],'right',self.docks["production"])
        self.dockarea.addDock(self.docks["events"],'right',self.docks["Parameters"])

    def initWidgets(self):
        self.widgets = {}
        self.widgets['geometry'] = gl.GLViewWidget()
        self.widgets['geometry'].show()
        self.initParametersWidget()
#        self.initConsoleWidget()
        self.initHistogramsWidget()

    def initHistogramsWidget(self):
        self.widgets['histograms.response'] = pg.PlotWidget(name='Plot1')
        self.docks['histograms.response'].addWidget(self.widgets['histograms.response'])
        self.widgets['primary_energy'] = pg.PlotWidget(name='Plot2')
        self.docks['primary_energy'].addWidget(self.widgets['primary_energy'])
        self.widgets['particle_legend'] = pg.PlotWidget(name='Plot3')
        self.docks['particle_legend'].addWidget(self.widgets['particle_legend'])
        
        self.widgets['distributions'] = pg.GraphicsLayoutWidget()
        self.widgets['up-left'] = self.widgets['distributions'].addPlot(row=0, col=0)
        self.widgets['up-right'] = self.widgets['distributions'].addPlot(row=0, col=1)
        self.widgets['down-left'] = self.widgets['distributions'].addPlot(row=1, col=0)
        self.widgets['down-right'] = self.widgets['distributions'].addPlot(row=1, col=1)
        self.docks['distributions'].addWidget(self.widgets['distributions'])
        
    def initConsoleWidget(self):
        # FIXME a tmp attempt
        namespace = {'pg': pg, 'np': np}
        text = "Interactive console"
        self.widgets['iconsole'] =  pg.console.ConsoleWidget(namespace=namespace, text=text)

    def configure(self,opts):
        self.options       = opts
        self.h5_file       = opts.h5_file or open_file_dialog()
        self.anim_status   = 'stop'
        self.event_number  = opts.event_number
        self.timerDelay    = opts.timerDelay
        self.n_frames_anim = int(opts.animation_frames[0])
        self.t_min_anim    = opts.animation_frames[1]
        self.t_max_anim    = opts.animation_frames[2]
        self.frames        = np.linspace(self.t_min_anim,self.t_max_anim,self.n_frames_anim)
        self.frame_number  = 0
        self.geometry_viewer.configure(opts)
        self.photons_viewer.configure(opts)
        self.hits_viewer.configure(opts)
        self.tracks_viewer.configure(opts)
        self.histograms_viewer.configure(opts)
        self.h5reader.configure(opts)

    def initReader(self):
        self.h5reader = h5Reader()    

    def openFile(self):
        if not os.path.exists(self.h5_file):
            log.warning(f'file {self.h5_file} does not exist. Click open file')
            return False
        self.h5reader.open(self.h5_file)
        self.h5reader.uid_current = self.event_number-1 # prepare to read event_number with next method
        self.readProductionHeader()
        self.readGeometry()
        self.initGeometryViewer()
        self.next()
        return True

    def readGeometry(self):
        self.geometry = self.h5reader.read_geometry()

    def readProductionHeader(self):
        self.productionHeader = self.h5reader.read_prod_header()
        self.add_state_info('ProductionHeader')



    def add_state_info(self,key):
        if key == 'ProductionHeader':
            self.state_dict['ProductionHeader'] = {'n_events': self.productionHeader.n_events_total,
                'anisotropy': self.productionHeader.medium_anisotropy,
                'scattering_model':str(self.productionHeader.medium_scattering_model)}

        elif key == 'EventHeader':
            self.state_dict['EventHeader'] = {'event number': self.event_number,
                                              'photons_sampling_weight': self.eventHeader.photons_sampling_weight}
#                                              'event_weight':self.eventHeader.event_weight}
        
        elif key == 'Cascades':
            self.state_cascades['Cascades'] = {'n_cascades':0}
            if self.particles.any():
                try:
                    self.state_cascades['Tracks'] = self.legend_viewer.state_info('Cascades')
                except:
                    print(f"Error retrieving Cascades info")
                

        elif key == 'Photons':
            try:
                self.state_photons['Photons'] = {'n_total': self.photons.n_photons, 'n_steps': self.photons.n_steps}
            except:
                None

        elif key == 'Tracks':
            if len(self.tracks):
                self.state_tracks['Tracks'] = self.legend_viewer.state_info('Tracks')
            else:
                self.state_tracks['Tracks'] = {'n_tracks':0}

        elif key == 'Hits':
            if len(self.hits):
                self.state_hits['Hits'] = {'n_om_hitted':self.hits_viewer.n_om_hitted,
                                           'npe_total':self.hits_viewer.npe_total}
            else:
                self.state_hits['Hits'] = {'n_om_hitted':0,
                                           'npe_total':0}


    def updateStateTree(self):
        self.add_state_info('ProductionHeader')
        self.add_state_info('EventHeader')
        self.add_state_info('Cascades')
        self.add_state_info('Photons')
        self.add_state_info('Tracks')
        self.add_state_info('Hits')
        self.state_tree.setData(self.state_dict)
        self.state_tree_hits.setData(self.state_hits)
        self.state_tree_tracks.setData(self.state_tracks)
        self.state_tree_photons.setData(self.state_photons)
        self.state_tree_cascades.setData(self.state_cascades)

    def update_data(self):
        self.eventHeader = self.h5reader.gEvent._evtHeader
        self.photons     = self.h5reader.gEvent._photons
        self.hits        = self.h5reader.gEvent._hits
        self.particles   = self.h5reader.gEvent._particles
        self.tracks      = self.h5reader.gEvent._tracks
        self.add_state_info('EventHeader')
        self.add_state_info('Photons')

    def makeButtons(self):
        self.buttons = {}
        self.buttons['msg']       = QLabel("")
        self.buttons['open']      = QPushButton("open h5")
        self.buttons['next']      = QPushButton("next")
        self.buttons['previous']  = QPushButton("previous")
        self.buttons['animation'] = QPushButton("start animation")
        self.buttons['pause']     = QPushButton("pause")
        self.buttons['pause'].setVisible(False)

        # connect push to class methods calls
        self.buttons['open'].clicked.connect(self.FileDialog)
        self.buttons['next'].clicked.connect(self.next)
        self.buttons['previous'].clicked.connect(self.previous)
        self.buttons['animation'].clicked.connect(self.animate)
        self.buttons['pause'].clicked.connect(self.pause)

        # add buttons to docks
        self.docks["events"].addWidget(self.buttons['open'])
        self.docks["events"].addWidget(self.buttons['next'])
        self.docks["events"].addWidget(self.buttons['previous'])
        self.docks["events"].addWidget(self.buttons['animation'])
        self.docks["events"].addWidget(self.buttons['pause'])
        self.docks["events"].addWidget(self.buttons['msg'])
        self.docks["production"].addWidget(self.state_tree)
        self.docks["hits_info"].addWidget(self.state_tree_hits)
        self.docks["tracks_info"].addWidget(self.state_tree_tracks)
        self.docks["photons_info"].addWidget(self.state_tree_photons)
        self.docks["particles_info"].addWidget(self.state_tree_cascades)
#        self.docks["iconsole"].addWidget(self.widgets['iconsole'])
    
    def FileDialog(self):
        self.anim_status = 'stop'
        self.timer.stop()
        self.frame_number  = 0
        self.h5_file = open_file_dialog()
        self.openFile()
#        self.next()

    def update_event(self):
        self.clean_view()
        self.update_data()
        self.initPhotonsViewer()
        self.initHitsViewer()
        self.initTracksViewer()
        self.initHistogramsViewer()
        self.updateStateTree()
        self.drawEvent()
        self.update_msg()

    def update_msg(self):
        event = self.h5reader.event_current
        clone = self.h5reader.clone_current
        if clone:
            self.buttons['msg'].setText(f'file={self.h5_file:<20}\n event={event:<}, clone={clone:<}')
        else:
            self.buttons['msg'].setText(f'file={self.h5_file:<20}\n event={event:<}')

    def next(self):
        self.h5reader.next()
        self.update_event()

    def previous(self):
        self.h5reader.prev()
        self.update_event()

    def animate(self):
        self.change_timer_status()
        self.drawEvent()

    def pause(self):
        if self.timer.isActive():
            self.timer.stop()
            self.buttons['pause'].setText("continue")
        else:
            self.timer.start(self.timerDelay)
            self.buttons['pause'].setText("pause")


    def setVisible_pause_button(self,vis):
        self.buttons['pause'].setVisible(vis)
        if vis == True:
            self.buttons['pause'].setText("pause")


    def change_timer_status(self):
        if self.anim_status == 'stop':
            self.anim_status = 'start'
            self.buttons['animation'].setText("stop animation")
            self.setVisible_pause_button(True)
            self.timer.start(self.timerDelay)
        elif self.anim_status == 'start':
            self.anim_status = 'stop'
            self.buttons['animation'].setText("start animation")
            self.setVisible_pause_button(False)
            self.timer.stop()

    def initTimer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.drawEventAnimated)

    def createViewers(self):
        # geometry viewer
        self.geometry_viewer = geometry_viewer()
        self.geometry_viewer.set_docks(self.docks)
        self.geometry_viewer.set_widgets(self.widgets)
        # photons viewer
        self.photons_viewer  = photons_viewer()
        self.photons_viewer.set_docks(self.docks)
        self.photons_viewer.set_widgets(self.widgets)
        # hits viewer
        self.hits_viewer = hits_viewer()
        self.hits_viewer.set_docks(self.docks)
        self.hits_viewer.set_widgets(self.widgets)
        # tracks viewer
        self.tracks_viewer = tracks_viewer()
        self.tracks_viewer.set_docks(self.docks)
        self.tracks_viewer.set_widgets(self.widgets)
        # histograms viewer
        self.histograms_viewer = histograms_viewer()
        self.histograms_viewer.set_docks(self.docks)
        self.histograms_viewer.set_widgets(self.widgets)
        # legend viewer
        self.legend_viewer = GLPainterItem()

    def initGeometryViewer(self):
        self.geometry_viewer.set_data(self.geometry)

    def initPhotonsViewer(self):
        self.photons_viewer.set_data(self.photons)
        self.photons_viewer.set_frames(self.frames)

    def initHitsViewer(self):
        data = {}
        data['hits'] = self.hits
        data['event_header'] = self.state_dict['EventHeader']
        if self.geometry is not None:
            data['geom'] = self.geometry['Geometry']
        

        self.hits_viewer.set_data(data)
        self.hits_viewer.set_frames(self.frames)
        self.hits_viewer.hits_analysis()
        self.add_state_info('Hits')

    def initTracksViewer(self):
        self.tracks_viewer.set_data(self.tracks)
        self.tracks_viewer.set_frames(self.frames)
        if len(self.tracks):
            self.tracks_viewer.build_static_tracks()
            self.tracks_viewer.build_animated_tracks()
            self.legend_viewer.configure(self.widgets['geometry'], self.tracks_viewer.particle_id, self.particles)

    def initHistogramsViewer(self):
        data = {}
        data['tracks'] = self.tracks
        data['photons'] = self.photons
        if len(self.tracks):
            data['legend'] = self.legend_viewer.state_info('Tracks')
        self.histograms_viewer.set_data(data)
        self.histograms_viewer.set_frames(self.frames)

    def initIntersection2DViewer(self):
        pass
        '''
        data = {}
#        self.tracks = h5file["event_0/tracks/points"]
#        data['tracks'] = self.tracks
        data['photons'] = self.photons
        data['tracks'] = self.photons
        data['geom'] = self.geometry['geom']
        a = intersection_viewer()
        a.set_data(data)
        a.configure(self.options)
        a.plane_of_cherenkov_ring()
        a.plot_intersection()
        '''

    def initParametersWidget(self):
        children = []
        children.append(dict(name='show_modules',  title='show_modules', type='bool', value=False))
        children.append(dict(name='show_boxes',    title='show_boxes',   type='bool', value=False))
        children.append(dict(name='show_hits',     title='show_hits',    type='bool', value=True))
        children.append(dict(name='show_photons',  title='show_photons', type='bool', value=True))
        children.append(dict(name='show_tracks',   title='show_tracks',  type='bool', value=False))
        children.append(dict(name='min_energy',   title='min_energy',  type='float', limits=[0,1], value=0, step=0.01))

        self.params = ptree.Parameter.create(name='Display options', type='group', children=children)
        self.params.sigTreeStateChanged.connect(self.parametersChanged)

        for c in self.params.children():
            c.setDefault(c.value())
        t = ptree.ParameterTree(showHeader=False)
        t.setParameters(self.params)
        self.docks['Parameters'].addWidget(t)

    def parametersChanged(self,param, changes):

        for param, change, data in changes:
            path = self.params.childPath(param)
            if path is not None:
                childName = '.'.join(path)
            else:
                childName = param.name()
            log.debug('parameter: %s'% childName)
            log.debug('change:    %s'% change)
            log.debug('data:      %s'% str(data))
        self.update_visibility(childName,data)

    def update_visibility(self,name,value):
        if name == 'show_modules':
            self.geometry_viewer.setVisible_om(value)
        elif name == 'show_boxes':
            self.geometry_viewer.setVisible_bb(value)
        elif name == 'show_photons':
            if self.anim_status == 'start': # animation ongoing
                self.photons_viewer.setVisible_photons_animated(value)
            else:
                self.photons_viewer.setVisible_photons_static(value)
        elif name == 'show_hits':
            if self.anim_status == 'start': # animation ongoing
                self.hits_viewer.setVisible_hits_animated(value)
            else:
                self.hits_viewer.setVisible_hits_static(value)
        elif name == 'show_tracks':
            if self.anim_status == 'start': # animation ongoing
                self.tracks_viewer.setVisible_tracks_animated(value)
            else:
                self.tracks_viewer.setVisible_tracks_static(value)
        elif name == 'min_energy':
            self.options.min_energy_for_tracks = value
            self.h5reader.change()
            self.update_event()

    def setStaticVis(self,vis):
        self.photons_viewer.setVisible_photons_static(vis)
        self.hits_viewer.setVisible_hits_static(vis)
        self.tracks_viewer.setVisible_tracks_static(vis)
        self.histograms_viewer.setVisible_hist_static(vis)

    def setAnimatedVis(self,vis):
        self.photons_viewer.setVisible_photons_animated(vis)
        self.hits_viewer.setVisible_hits_animated(vis)
        self.tracks_viewer.setVisible_tracks_animated(vis)
        self.histograms_viewer.setVisible_hist_animated(vis)

    def drawEvent(self):
        if self.anim_status == 'start':
            self.setStaticVis(False)
            self.drawEventAnimated()
        elif self.anim_status == 'stop':
            self.setStaticVis(True)
            self.setAnimatedVis(False)
            self.drawEventStatic()

    def clean_view(self):
        self.photons_viewer.clean_view()
        self.hits_viewer.clean_view()
        self.tracks_viewer.clean_view()
        self.histograms_viewer.clean_view()

    def drawEventStatic(self):
        self.histograms_viewer.display_static(True)
        for par in self.params.children():
            if par.name() == 'show_modules':
                self.geometry_viewer.display_om(par.value())
            elif par.name() == 'show_boxes':
                self.geometry_viewer.display_bounding_boxes(par.value())
            elif par.name() == 'show_photons':
                if self.photons:
                    self.photons_viewer.display_static(par.value())
            elif par.name() == 'show_hits':
                if len(self.hits):
                    self.hits_viewer.display_static(par.value())
            elif par.name() == 'show_tracks':
                if len(self.tracks):
                    self.tracks_viewer.display_static(par.value())

    def drawEventAnimated(self):
        if self.frame_number >= len(self.frames):
            self.frame_number = 0
        self.histograms_viewer.display_frame(self.frame_number, True)
        for par in self.params.children():
            if par.name() == 'show_photons':
                if self.photons:
                    self.photons_viewer.display_frame(self.frame_number,par.value())
            elif par.name() == 'show_hits':
                if len(self.hits):
                    self.hits_viewer.display_frame(self.frame_number,par.value())
            elif par.name() == 'show_tracks':
                if len(self.tracks):
                    self.tracks_viewer.display_frame(self.frame_number,par.value())
        self.frame_number += 1

def run(opts) -> None:
    app = QApplication(sys.argv)
    viewer = h5Viewer()
    viewer.configure(opts)
    viewer.init()
    viewer.initIntersection2DViewer()
    viewer.setWindowTitle('ntsimViewer: a lightweight 3D visualization of events')
    viewer.setWindowTitle('Visual multi-functional interface "VIOLINE"')
    screen_resolution = app.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()
    width, height = width*opts.screen_fraction[0], height*opts.screen_fraction[1]
    viewer.resize(int(width), int(height))
    viewer.show()
    sys.exit(app.exec_())

import configargparse
parser = configargparse.get_argument_parser()
parser.add_argument("h5_file",type=str, nargs='?', default=None, help="path to h5 file")
#p.add_argument("--h5viewer-config", is_config_file=True,default='configs/h5viewer.cfg',help="Config for h5viewer and its brothers")
parser.add_argument('-prefix', '--generators_path', help='path to GENERATORS [ENV]', env_var='GENERATORS')  # this option can be set in a config file because it starts with '--'
parser.add_argument("--viewers",nargs='+',type=str,default=[],help="list of viewers to test")
parser.add_argument("--distance", type=float, default=2000, help="OpenGL view distance")
parser.add_argument("--grid_scale", nargs='+', type=int, default=[20, 20, 1], help="grid scale")
parser.add_argument("--event_number",type=int,default=0,help="event number to view")
parser.add_argument("--screen_fraction",nargs='+',type=float,default=(0.9,0.9),help="(x,y) fraction of the screen for the viewer")
parser.add_argument('-l', '--log-level', choices=('deepdebug', 'debug', 'info', 'warning', 'error', 'critical'), default='INFO', help='logging level')
parser.add_argument("--timerDelay",type=float,default=150,help="timer delay in ms")
parser.add_argument("--threshold", type=float, default=0., help="threshold for number of photoelectrons/OM to display")
parser.add_argument("--animation_frames",nargs='+',type=float,default=(100,0,3000),help="(n,t1,t2), where n = number of frames, (t1,t2) = time interval")
parser.add_argument("--rmax", type=float, default=10., help="maximum radius of OM to display")
parser.add_argument('--min_energy_for_tracks', type=float, default=0)
parser.add_argument('--min_length_for_tracks', type=float, default=0.01, help="minimal length of track to show") 

def main():
    opts = parser.parse_args()
    log.setLevel(logging.getLevelName(opts.log_level.upper()))
    logging.root.setLevel(logging.getLevelName(opts.log_level.upper()))  # set global logging level
    run(opts)

if __name__ == '__main__':
    main()
