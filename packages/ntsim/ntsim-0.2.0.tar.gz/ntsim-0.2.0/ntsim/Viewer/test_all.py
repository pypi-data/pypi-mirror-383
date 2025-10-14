import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.dockarea import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.QtWidgets import QWidget,QGridLayout

from modules.io.h5Reader import h5Reader
import logging
log=logging.getLogger('test_geometry_viewer')
logformat='[%(name)20s ] %(levelname)8s: %(message)s'
logging.basicConfig(format=logformat)

app = pg.mkQApp("Test geometry")
win = QtGui.QMainWindow()
central_widget = QWidget(win)
win.setCentralWidget(central_widget)
layout = QGridLayout(central_widget)
win.resize(800,800)

dockarea = DockArea()
docks = {}
docks["geometry"] = Dock("geometry")
dockarea.addDock(docks["geometry"],'top')
widgets = {}
widgets['geometry'] = gl.GLViewWidget()

layout.addWidget(dockarea)

win.show()
win.setWindowTitle('h5Viewer')

import configargparse

p = configargparse.get_argument_parser()
p.add_argument("--h5viewer-config", is_config_file=True,default='configs/h5viewer.cfg',help="Config for h5viewer and its brothers")
p.add_argument('-prefix', '--generators_path', help='path to GENERATORS [ENV]', env_var='GENERATORS')  # this option can be set in a config file because it starts with '--'
p.add_argument("--viewers",nargs='+',type=str,default=[],help="list of viewers to test")
p.add_argument("--distance",type=float,default=1200,help="OpenGL view distance")
p.add_argument("--grid_scale",nargs='+',type=int,help="number of steps for photons propagation")
p.add_argument("--h5_file",type=str,default='h5_output/events.h5',help="path to h5 file")
p.add_argument("--event_number",type=int,default=0,help="event number to view")

opts = p.parse_args()
reader = h5Reader()
reader.open(opts.h5_file)
geometry = reader.read_geometry()
photons  = reader.read_photons(opts.event_number)
n_frames = 100
tmin = np.amin(photons.t)
tmax = np.amax(photons.t)
frames = np.linspace(tmin,tmax,n_frames)
viewers = {}

if 'geometry' in opts.viewers:
    from viewer.test_geometry_viewer import test_geometry_viewer
    viewers['geometry'] = test_geometry_viewer(docks=docks,widgets=widgets,data=geometry,frames=frames,options=opts)
    viewers['geometry'].display_static()
if 'photons' in opts.viewers:
    from viewer.test_photons_viewer import test_photons_viewer
    viewers['photons'] = test_photons_viewer(docks=docks,widgets=widgets,data=photons,frames=frames,options=opts)
#    viewers['photons'].display_static()
    viewers['photons'].display_frame(10)
if __name__ == '__main__':
    pg.mkQApp().exec_()
