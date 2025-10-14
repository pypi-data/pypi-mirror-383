import pyqtgraph as pg
import pyqtgraph.opengl as gl
import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QGridLayout, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QPushButton, QMessageBox,
                            QMainWindow, QWidget, QOpenGLWidget, QPushButton, QRadioButton, QComboBox, QVBoxLayout,QDoubleSpinBox, QVBoxLayout,QSplitter)
from pyqtgraph.dockarea import *
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import LayoutWidget, PlotWidget
import pyqtgraph.console
import pyqtgraph.parametertree as ptree
import pyqtgraph.console

import numpy as np
import os
from collections import OrderedDict

import pyqtgraph.parametertree.parameterTypes as pTypes

import csv
import re

import logging
log=logging.getLogger('NTSim')
logformat='[%(name)20s ] %(levelname)8s: %(message)s'
logging.basicConfig(format=logformat)
logging.root.setLevel(logging.getLevelName('INFO'))  # set global logging level


class ntsim_gui(QMainWindow):
    sigKeyPress = QtCore.pyqtSignal(object)
    def __init__(self):
        super().__init__()
        from ntsim.arguments import parser
        p = parser()
        self.opts = p.parse_args()
        from ntsim.Detector.DetectorFactory import DetectorFactory
        self.detFactory = DetectorFactory()
        from ntsim.Medium.Medium import Medium
        self.medium = Medium()
        from ntsim.ntsim import NTsim
        self.simu =  NTsim()
        simu_generators = self.simu.known_primary_generators
        children = [
            dict(name='sigopts', title='Ntsim Options', type='group', children=[
                dict(name='log_level', title='Log level', type='list', limits=('deepdebug', 'debug', 'info', 'warning', 'error', 'critical'), value = 'info'),
                dict(name='geometry_config', title='Geometry config', type='str', value = 'configs/geometry.cfg'),
                dict(name='n_events', title='Number of events', type='int', value = 2),
                dict(name='multithread', title='Multithread', type='bool', value = False),
                dict(name='primary_generator', title='Primary generators', type='list', limits=simu_generators, value = self.simu.known_primary_generators['Laser']),
                #dict(name='primary_propagators', title='Primary propagators', type='list', limits=('particlePropagator','nuPropagator','muonPropagator','MUMPropagator','g4propagator'), value = 'particlePropagator'),#no default in arguments
                dict(name='photon_propagator', title='Photon propagator', type='str', value = 'mcPhotonPropagator'),
                dict(name='ray_tracer', title='Ray tracer', type='str', value = 'smartRayTracer'),
                dict(name='cloner', title='Cloner', type='str', value = 'cloneEvent'),
                dict(name='photon_suppression', title='Photon suppression', type='int', value = 1000, step=1),
                dict(name='photons_weight', title='Photons weight', type='float', limits=[-1, 1], value=1, step=0.01),
                dict(name='photons_bunches', title='Photon bunches', type='int', value = 1),
                dict(name='photons_n_scatterings', title='Photon n scatterings', type='int', value = 5),
                #dict(name='photons_wave_range', title='Photons weight', type='float', value=[350,600], step=1),
                dict(name='particle_pdgid', title='Photon bunches', type='int', value = 13),
                dict(name='energy_GeV', title='Energy (GeV)', type='float', value=100),
                #dict(name='position_m', title='Energy (GeV)', type='float', value=100),
                #dict(name='direction', title='Energy (GeV)', type='float', value=100),
                dict(name='cloner_accumulate_hits', title='Cloner accumulate hits', type='bool', value = False),
            ]),
            dict(name='NuProp options', title='NuProp options', type='group', children=[
                dict(name='model', title='Model', type='str', value = 'KM'),
                dict(name='flux_file', title='Flux file', type='str', value = 'Numu_H3a+KM_E2.DAT'),
                dict(name='flux_type', title='Flux type', type='str', value = 'model_flux'),
                dict(name='energy_min', title='Energy min', type='float', value=10, step=0.01),
                dict(name='energy_max', title='Energy max', type='float', value=10**8, step=0.01),
                dict(name='flux_indicator', title='Flux indicator', type='float', value=2.7, step=0.1),
                dict(name='N_event', title='N event', type='int', value = 100000),
                dict(name='vegas_neval', title='Vegas neval', type='int', value = 1000),
                #dict(name='fvertex', title='fvertex', type='float', value=[0.,0.,0.], step=0.01),
            ]),
            dict(name='Geometry options', title='Geometry options', type='group', children=[
                dict(name='detector_name', title='Detector', type='list', limits=self.detFactory.known_detectors, value = self.detFactory.known_detectors['GVDDetector']),
                dict(name='geometry_input', title='Geometry input', type='str', value = 'configs/geometry.csv'),
                dict(name='geometry_output', title='Geometry output', type='str', value = 'geom.csv'),
                #dict(name='geometry_time_interval', title='Detector', type='list', limits=self.detFactory.known_detectors, value = 'GVDDetector'),
                #dict(name='geometry_clusters', title='Detector', type='list', limits=self.detFactory.known_detectors, value = 'GVDDetector'),
                dict(name='geometry_true_radius', title='Optical Module true radius (m)', type='float', value=0.216, step=0.001),
                dict(name='geometry_prod_radius', title='Optical Module production radius (m)', type='float', value=1.0, step=0.1),
                dict(name='season', title='Season', type='float', value=2018, step=0.01),
            ]),
            dict(name='Medium options', title='Medium options', type='group', children=[
                dict(name='medium_scattering_model', title='Medium Scattering Model', type='list', limits=self.medium.known_models),
                dict(name='medium_anisotropy', title='Medium Anisotropy', type='float', limits=[-1, 1], value=0.99, step=0.01),
            ]),
            dict(name='h5Writer options', title='h5Writer options', type='group', children=[
                dict(name='h5_output_file', title='Output file name', type='str',  value = 'events'),
                dict(name='h5_output_dir', title='Output directory', type='str', value = 'h5_output'),
                #3
                dict(name='h5_save_vertices', title='Boolean to save vertices', type='bool', value = False),
            ]),
            dict(name='Clone options', title='Clone options', type='group', children=[
                dict(name='cloner_n', title='Number of events to clone', type='int', value = 0),
                #2
            ]),
            dict(name='LaserPrimary options', title='LaserPrimary options', type='group', children=[
                dict(name='laser_n_photons', title='Number of photons to generate', type='int', value = 10000),
                #3
            ]),
            #Corsika 3
            dict(name='Geant4 options', title='Geant4 options', type='group', children=[
                dict(name='g4_casc_max', title='g4_casc_max', type='int', value = 0.05),
                #1
                dict(name='g4_random_seed', title='g4_random_seed', type='float', value=1, step=1),
                dict(name='g4_detector_height', title='g4_detector_height', type='float', value=1360, step=1),
                dict(name='g4_detector_radius', title='g4_detector_radius', type='float', value=1000, step=1),
            ]),
            dict(name='CascadeCherenkov options', title='CascadeCherenkov options', type='group', children=[
                dict(name='casc_param_X0', title='casc_param_X0', type='float', value = 0.3608, step=0.0001),
            ]),
            dict(name='trackCherenkov options', title='TrackCherenkov options', type='group', children=[
                #1
                dict(name='refraction_index', title='Refraction index', type='float', value=1.34, step=0.01),
            ]),
            dict(name='ChargedPrimary options', title='ChargedPrimary options', type='group', children=[
                #3
                #dict(name='charged_length_m', title='Charged length (m)', type='float', value=100, step=1),# NOT WORKING!!!!!!!!!!
            ]),
            dict(name='NeutrinoPrimary options', title='NeutrinoPrimary options', type='group', children=[
                dict(name='neutrinoPrimary_pdgid', title='PDGID of neutrino', type='int', value=14),
                dict(name='neutrinoPrimary_energy_mode', title='neutrinoPrimary_energy_mode', type='list', limits=('random', 'fixed'), value = 'fixed'),
                dict(name='neutrinoPrimary_direction_mode', title='neutrinoPrimary_direction_mode', type='list', limits=('random', 'fixed'), value = 'fixed'),
                dict(name='neutrinoPrimary_target_mode', title='neutrinoPrimary_target_mode', type='list', limits=('random', 'fixed'), value = 'random'),
                dict(name='neutrinoPrimary_current_mode', title='neutrinoPrimary_current_mode', type='list', limits=('random', 'fixed'), value = 'random'),
                dict(name='neutrinoPrimary_pdf_model', title='LHAPDF model for nucleon', type='str', value = 'CT10nlo'),
                dict(name='neutrinoPrimary_energy_GeV', title='Energy of neutrino (GeV)', type='float', value=100, step=1),
                dict(name='neutrinoPrimary_target', title='NeutrinoPrimary target', type='str', value = 'proton'),
                #1
            ]),
            dict(name='SolarPhotons options', title='SolarPhotons options', type='group', children=[
                #1
                dict(name='solar_bunches', title='Bunches', type='int', value=3),
                dict(name='solar_year', title='Year', type='int', value=2021),
                dict(name='solar_month', title='Month', type='int', value=10),
                dict(name='solar_day', title='Day', type='int', value=22),
                dict(name='solar_hour', title='Hour', type='int', value=13),
                dict(name='solar_minute', title='Minute', type='int', value=7),
                dict(name='charged_length_m', title='Charged length (m)', type='float', value=100, step=1),
            ]),
        ]
        self.param = ptree.Parameter.create(name='Model options', type='group', children=children)

        #Set deafult value for param
        for c in self.param.children():
            for i in c.children():
                i.setDefault(i.value())

        pt = ptree.ParameterTree(showHeader=False)
        pt.setParameters(self.param)
        self.splitter = QSplitter(self)
        self.splitter.addWidget(pt)
        self.splitter.show()

        def exportData():
            defaultFileName = 'data.csv'
            fileName, _ = QFileDialog.getSaveFileName(None, 'Export Data', defaultFileName, 'CSV Files (*.csv)')
            with open(fileName, 'w', newline='') as f:
                writer = csv.writer(f)
                for children in self.param.children():
                    for child in children:
                        parameter = child.name()
                        value = str(child.value())
                        if value.startswith('<') and value.endswith('>'):
                            value = value.split('.')[-1][:-2]
                        writer.writerow([parameter, value])

        def importData():
            fileName = QFileDialog.getOpenFileName()
            with open(fileName[0], 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    paramName = str(row[0])
                    #print(paramName)
                    paramValue = str(row[1])
                    #print(paramValue)
                    for children in self.param.children():
                        for child in children:
                            if child.name() == paramName:
                                child.setValue(paramValue)
                                if child.type() == 'bool':
                                    child.setValue(eval(paramValue))
                                if child.name() == 'primary_generator':
                                    self.param.children()[0]['primary_generator'] = self.simu.known_primary_generators[paramValue]
                                if child.name() == 'detector_name':
                                    self.param.children()[2]['detector_name'] = self.detFactory.known_detectors[paramValue]
                                if child.name() == 'medium_scattering_model':
                                    self.param.children()[3]['medium_scattering_model'] = self.medium.known_models[paramValue]
                                #print(dir(self.param.getValues()['sigopts'][1]['primary_generator']))
                                #self.param.setValue(self.simu.known_primary_generators['SolarPhotons'])['sigopts'][1]['primary_generator'][0]
                                #self.param.children()[0]['primary_generator'] = self.simu.known_primary_generators['SolarPhotons']

        #Resetting param
        def resetParam():
            for c in self.param.children():
                for i in c.children():
                    i.setToDefault()

        #Call h5Viewer
        def callViewer():
            pass
            '''
            from ntsim.viewer.h5Viewer import h5Viewer
            from PyQt5 import QtWidgets
            self.windows = QtWidgets.QMainWindow()
            self.viewer = h5Viewer()
            self.viewer.init
            window.show()
            '''

        #Build button
        self.build_button = QPushButton("Build ntsim")
        self.build_button.clicked.connect(self.build_ntsim)
        #Reseting Data
        self.reset_button = QPushButton("Reset parameters")
        self.reset_button.clicked.connect(resetParam)
        #exportData
        self.imp_button = QPushButton("Import profile")
        self.imp_button.clicked.connect(importData)
        #importData
        self.exp_button = QPushButton("Export profile")
        self.exp_button.clicked.connect(exportData)
        #ViewerMain
        self.view_button = QPushButton("View results")
        self.view_button.clicked.connect(callViewer)
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QGridLayout(central_widget)
        self.layout.addWidget(self.splitter)
        self.layout.addWidget(self.reset_button)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.exp_button)
        button_layout.addWidget(self.imp_button)

        self.layout.addLayout(button_layout, 5, 0, 1, 1)
        self.layout.addWidget(self.build_button)
        self.layout.addWidget(self.view_button)


    #Building ntsim
    def build_ntsim(self):
        #Setting parameters in opts from param
        for child in self.param.children():
            #print(child)
            for children in child:
                #print(str(children.name()))
                #w = setattr(self.opts,children.name(),children.value())
                if children.name() == 'primary_generator':
                    value = str(children.value())
                    value = value.split('.')[-1][:-2]
                    self.opts.primary_generator = value
                else:
                    if children.name() == 'detector_name':
                        value = str(children.value())
                        value = value.split('.')[-1][:-2]
                        self.opts.detector_name = value
                    else:
                        if children.name() == 'medium_scattering_model':
                            value = str(children.value())
                            value = value.split('.')[-1][:-2]
                            self.opts.medium_scattering_model = value
                        else:
                            setattr(self.opts,children.name(),children.value())
                #print(str(children))

        #Validation of parameters in opts
        counter = 0
        for child in self.param.children():
            for children in child:
                if children.name() == 'primary_generator':
                    value = str(children.value())
                    value = value.split('.')[-1][:-2]
                    if str(getattr(self.opts,children.name()))==value:
                        #print(children.name() + " set right")
                        pass
                    else:
                        counter+=1
                        print("ERROR LIST" + children.name())
                else:
                    if children.name() == 'detector_name':
                        value = str(children.value())
                        value = value.split('.')[-1][:-2]
                        if str(getattr(self.opts,children.name()))==value:
                            #print(children.name() + " set right")
                            pass
                        else:
                            counter+=1
                            print("ERROR LIST" + children.name())
                    else:
                        if children.name() == 'medium_scattering_model':
                            value = str(children.value())
                            value = value.split('.')[-1][:-2]
                            if str(getattr(self.opts,children.name()))==value:
                                #print(children.name() + " set right")
                                pass
                            else:
                                counter+=1
                                print("ERROR LIST" + children.name())
                        else:
                            if str(getattr(self.opts,children.name()))==str(children.value()):
                                #print(children.name() + " set right")
                                pass
                            else:
                                counter+=1
                                print("ERROR " + children.name())
        if counter > 0:
            print('ERROR PARAMETER COUNTER: ' + str(counter))
            print('ntsim stopped')
            return

        #Check spelling
        pattern = r'[<>:"\|?* ]'
        for children in self.param.children():
            for child in children:
                parameter = child.name()
                value = child.value()
                if child.type() == 'str':
                    if re.search(pattern, value):
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText("Invalid name for " + parameter)
                        msg.setInformativeText(parameter + " contains invalid characters.")
                        msg.setWindowTitle("Error")
                        msg.exec_()
                        return

        #start ntsim
        self.simu.init(self.opts)
        self.simu.configure(self.opts)
        self.simu.process()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = ntsim_gui()
    main_window.show()
    #main_window.resize(540, 940)
    sys.exit(app.exec_())
