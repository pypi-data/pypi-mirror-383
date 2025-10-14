import sys
import subprocess
from PyQt5.QtCore import Qt, QTimer, QCoreApplication, QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget,
    QFileDialog, QCheckBox, QTextEdit, QAction, QGridLayout, QOpenGLWidget,QRadioButton, QDockWidget)
from pyqtgraph.dockarea import *
from pyqtgraph.parametertree import Parameter, ParameterTree
import h5py
import pandas as pd
import csv

import logging
log=logging.getLogger('NTSim')
logformat='[%(name)20s ] %(levelname)8s: %(message)s'
logging.basicConfig(format=logformat)
logging.root.setLevel(logging.getLevelName('INFO'))


class Gui(QMainWindow):
    def __init__(self):
        super().__init__()
        #self.initStateWidget()
        self.initDocks()
        self.initWidgets()
        self.initNtsim()
        self.selected_params = []
        self.selected_arrays = {}
        self.makeParameters()
        self.h5viewer = None
        self.param_state = {}

    def init(self):
        """Initializes the center widget and places the docks"""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)
        self.dockPlacement()
        self.makeButtons()
        layout.addWidget(self.dockarea)

    def initDocks(self):
        """Creates docks for different areas of the interface"""
        self.dockarea = DockArea()
        self.docks = {}
        self.docks["screen1"]  = Dock("Ntsim Startup")
        self.docks["screen2"]  = Dock("h5Viewer")
        self.docks["main"]  = Dock("ntsim", size=(1,1))
        self.docks["log"]  = Dock("Logger", size=(120,100))
        self.docks["param"]  = Dock("Parameters", size=(120,100))
        self.docks["child_param"]  = Dock("Child Parameters", size=(300,100))
    
    def dockPlacement(self):
        """Places docks in the desired areas"""
        self.dockarea.addDock(self.docks["screen2"], 'top')
        self.dockarea.addDock(self.docks["screen1"],'below',self.docks["screen2"],closable=True)
    
        # Create additional areas for nested docks
        self.sc1_sub_dockarea = DockArea()
        self.docks["screen1"].addWidget(self.sc1_sub_dockarea)

        self.sc2_sub_dockarea = DockArea()
        self.docks["screen2"].addWidget(self.sc2_sub_dockarea)
        
        self.sc1_sub_dockarea.addDock(self.docks["param"], 'top')
        self.sc1_sub_dockarea.addDock(self.docks["child_param"], 'right', self.docks["param"], closable=True)
        self.sc1_sub_dockarea.addDock(self.docks["log"], 'bottom', self.docks["param"])
        self.sc1_sub_dockarea.addDock(self.docks["main"], 'bottom', self.docks["log"])

        #Resize
        #self.docks["main"].setStretch(1, 1)

    def initWidgets(self):
        """Creates and configures widgets for logging and displaying parameters"""
        self.widgets = {}

        self.widgets['log'] = QTextEdit()
        self.widgets['ptree'] = ParameterTree()
        self.widgets['child ptree'] = ParameterTree()

        self.docks["param"].addWidget(self.widgets['ptree'])
        self.docks["child_param"].addWidget(self.widgets['child ptree'])
        self.docks["log"].addWidget(self.widgets['log'])

        self.widgets['log'].setReadOnly(True)

    def initNtsim(self):
        """Initializes the Ntsim object"""
        from ntsim.__main__ import NTSim
        self.simu =  NTSim()
        parser = configargparse.ArgParser()

        parser.add_argument('-l', '--log-level',type=str,choices=('deepdebug', 'debug', 'info', 'warning', 'error', 'critical'),default='INFO',help='logging level')
        parser.add_argument('--seed',type=int, default=None, help='random generator seed')
        parser.add_argument('--show-options',action="store_true", help='show all options')
        parser.add_argument('--compute_hits',action="store_true", help='show all options')
        
        self.opts, _ = parser.parse_known_args()

        self.known_factories = self.simu.add_module_args(parser)
        parser.add_argument('--telescope.name', dest='telescope_name', type=str, choices=self.known_factories['TelescopeFactory'], default=None, help='Telescope to use')
        parser.add_argument('--detector.name', dest='sensitive_detector_name', type=str, choices=self.known_factories['SensitiveDetectorFactory'], default=None, help='Sensitive detector to use')
        parser.add_argument('--medium_prop.name', dest='medium_properties_name', type=str, choices=self.known_factories['MediumPropertiesFactory'], default='Example1MediumProperties', help='Medium properties to use')
        parser.add_argument('--medium_scat.name', dest='medium_scattering_model_name', type=str, choices=self.known_factories['MediumScatteringModelsFactory'], default='HenyeyGreenstein', help='Medium scattering to use')
        parser.add_argument('--generator.name', dest='primary_generator_name', type=str, choices=self.known_factories['PrimaryGeneratorFactory'], default='ToyGen', help='Primary Geenrator to use')
        parser.add_argument('--propagator.name', dest='particle_propagator_name', type=str, choices=self.known_factories['ParticlePropagatorFactory'], default='ParticlePropagator', help='Propagator to use')
        parser.add_argument('--photon_propagator.name', dest='photon_propagator_name', type=str, choices=self.known_factories['PhotonPropagatorFactory'], default='MCPhotonPropagator', help='Photon propagator to use')
        parser.add_argument('--ray_tracer.name', dest='ray_tracer_name', type=str, choices=self.known_factories['RayTracerFactory'], default='SmartRayTracer', help='Ray tracer to use')
        parser.add_argument('--cherenkov.name', dest='cherenkov_generator_name', type=str, choices=self.known_factories['CherenkovGeneratorFactory'], default=None, help='')
        parser.add_argument('--cloner.name', dest='clone_generator_name',type=str, choices=self.known_factories['CloneGeneratorFactory'], default=None, help='')
        parser.add_argument('--trigger.name', dest='trigger_name', type=str, choices=self.known_factories['TriggerFactory'], default=None, help='')
        parser.add_argument('--analysis.name', dest='analysis_name', type=str, choices=self.known_factories['AnalysisFactory'], default=None, help='')

        parser.add_argument('--writer.name', dest='writer_name', type=str, choices=self.known_factories['WriterFactory'], default='H5Writer', help='')

        parser.add_argument('--depth', type=int, default=0, help='depth bounding boxes')
        parser.add_argument('--n_events', type=int, default=1, help='')
        
        self.opts = parser.parse_args()

        self.max_BGVDcluster_number = max(self.opts.__dict__['BGVDTelescope.n_clusters']) + 1
        
        self.child_param_dict = parser.__dict__
        print(self.known_factories)
        
    def makeParameters(self):
        """
        Creates a parameter tree for the main and child parameters based on the passed arguments.
        Subscribes to parameter state changes and updates the opts state.
        """
        self.main_params = []
        self.factories_params = []
        
        # Handling top-level arguments
        for action in self.child_param_dict['_actions']:
                name = action.dest
                if '.' not in name:
                    if "name" in name:
                        if action.type == str and action.nargs == "+":
                            choices = [{'name': choice, 'type': 'bool', 'value': False} for choice in action.default]
                            self.factories_params.append({'name': name, 'type': 'group', 'children': choices})
                        elif hasattr(action, 'choices') and action.choices is not None:
                            choices = [{'name': choice, 'type': 'bool', 'value': False} for choice in action.choices]
                            self.factories_params.append({'name': name, 'type': 'group', 'children': choices})
                    
                    elif action.type == str and action.nargs == "+":
                        choices = [{'name': choice, 'type': 'bool', 'value': False} for choice in action.default]
                        self.main_params.append({'name': name, 'type': 'group', 'children': choices})
                    elif action.nargs is not None and action.nargs > 1:
                        sub_params = []
                        for i, v in enumerate(action.default):
                            if isinstance(v, (int, float)):
                                sub_params.append({'name': f'{name}[{i+1}]', 'type': 'float' if isinstance(v, float) else 'int', 'value': v})
                        self.main_params.append({'name': name, 'type': 'group', 'children': sub_params})
                    elif hasattr(action, 'choices') and action.choices is not None and action.nargs is None:
                        choices = [{'name': choice, 'type': 'bool', 'value': False} for choice in action.choices]
                        self.main_params.append({'name': name, 'type': 'list', 'values': action.choices})
                    elif hasattr(action, 'choices') and action.choices is not None:
                        choices = [{'name': choice, 'type': 'bool', 'value': False} for choice in action.choices]
                        self.main_params.append({'name': name, 'type': 'group', 'children': choices})
                    elif getattr(action, 'const', False) is True:
                        checkbox = {'name': name, 'type': 'bool', 'value': getattr(action, 'default', False)}
                        self.main_params.append(checkbox)
                    elif action.type == int:
                        self.main_params.append({'name': name, 'type': 'int', 'value': action.default})
                    elif action.type == str:
                        self.main_params.append({'name': name, 'type': 'str', 'value': action.default})
                    elif action.type == float:
                        self.main_params.append({'name': name, 'type': 'float', 'value': action.default})

        # Grouping parameters into two main sections: Main and Factories
        params = [
            {
                'name': 'Main',
                'type': 'group',
                'children': self.main_params
            },
            {
                'name': 'Factories',
                'type': 'group',
                'children': self.factories_params
            }
        ]

        self.p = Parameter.create(name='params', type='group', children=params)
        self.widgets['ptree'].setParameters(self.p, showTop=False)
        
        def param_changed(param, changes):
            """
            Method that reacts to changes in the main parameter tree.
            Updates the opts state and recreates the child parameter tree if necessary.
            """
            for param_obj, change, data in changes:
                f = True
                param_name = param_obj.name()
                for main_param in self.main_params:
                    if main_param['name'] == param_name or main_param['name'] == param_obj.parent().name():
                        f = False
                        self._update_opts_from_main_params(param, changes)
                if f:
                    if data:
                        for child_param in param_obj.parent().children():
                            if child_param.name() != param_name:
                                child_param.setValue(False)
                                if child_param.name() in self.selected_params:
                                    self.selected_params.remove(child_param.name())
                                    setattr(self.opts, param_obj.parent().name(), None)
                        for name in self.known_factories:
                            for choice in self.known_factories[name]:
                                if choice == param_name:
                                    self.selected_params.append(param_name)
                                    setattr(self.opts, param_obj.parent().name(), param_name)
                                    self.widgets['log'].append(f"{param_obj.parent().name()} was changed to {param_name} in opts")
                    else:
                        for child_param in param_obj.parent().children():
                            if child_param.name() in self.selected_params:
                                self.selected_params.remove(child_param.name())
                                setattr(self.opts, param_obj.parent().name(), None)
            
            self.group_params_dict = {}

            for action in self.child_param_dict['_actions']:
                name = action.dest
                
                if name.split('.')[0] in self.selected_params:
                    group_name = name.split('.')[0]
                    
                    if group_name not in self.group_params_dict:
                        self.group_params_dict[group_name] = []
                    
                    if group_name in self.selected_params:
                        try:
                            if (name == 'BGVDTelescope.n_clusters'):
                                self.cluster_array = action.choices
                                choices = [{'name': f'{i}', 'type': 'bool', 'value': True} for i in range(1, self.max_BGVDcluster_number)]
                                self.group_params_dict[group_name].append({'name': name, 'type': 'group', 'children': choices})
                            elif (name == 'BGVDTelescope.position_m') and action.choices is None:
                                self.group_params_dict[group_name].append({'name': name, 'type': 'str', 'value': "Not specified", 'readonly': True})
                            elif action.nargs == "+" and action.type == tuple:
                                choices = [{'name': choice, 'type': 'bool', 'value': False} for choice in action.choices]
                                self.group_params_dict[group_name].append({'name': name, 'type': 'list', 'values': action.choices})
                            elif (action.nargs == "+" and isinstance(action.default, list) and all(isinstance(x, (int, float)) for x in action.default)) and len(action.default) <= 3:
                                sub_params = []
                                for i, v in enumerate(action.default):
                                    if isinstance(v, (int, float)):
                                        sub_params.append({'name': f'{name}[{i+1}]', 'type': 'float' if isinstance(v, float) else 'int', 'value': v})
                                self.group_params_dict[group_name].append({'name': name, 'type': 'group', 'children': sub_params})
                            elif action.type == str and action.nargs == "+":
                                choices = [{'name': choice, 'type': 'bool', 'value': False} for choice in action.default]
                                self.group_params_dict[group_name].append({'name': name, 'type': 'group', 'children': choices})
                            elif action.nargs is not None and int(action.nargs) > 1 and action.type == tuple:
                                tuple_choices=[]
                                for choice in action.choices:
                                    tuple_choice = [{'name': choice, 'type': 'str', 'value': element} for i, element in enumerate(choice)]
                                    tuple_choices.append({'name': name, 'type': 'group', 'children': tuple_choice})
                                self.group_params_dict[group_name].append(tuple_choices)
                                
                            elif action.nargs is not None and action.nargs > 1:
                                sub_params = []
                                for i, v in enumerate(action.default):
                                    if isinstance(v, (int, float)):
                                        sub_params.append({'name': f'{name}[{i+1}]', 'type': 'float' if isinstance(v, float) else 'int', 'value': v})
                                self.group_params_dict[group_name].append({'name': name, 'type': 'group', 'children': sub_params})
                            elif hasattr(action, 'choices') and action.choices is not None:
                                choices = [{'name': choice, 'type': 'bool', 'value': False} for choice in action.choices]
                                self.group_params_dict[group_name].append({'name': name, 'type': 'group', 'children': choices})
                            elif getattr(action, 'const', False) is True:
                                checkbox = {'name': name, 'type': 'bool', 'value': getattr(action, 'default', False)}
                                self.group_params_dict[group_name].append(checkbox)
                            elif action.type == int:
                                self.group_params_dict[group_name].append({'name': name, 'type': 'int', 'value': action.default})
                            elif action.type == str:
                                self.group_params_dict[group_name].append({'name': name, 'type': 'str', 'value': action.default})
                            elif action.type == float:
                                self.group_params_dict[group_name].append({'name': name, 'type': 'float', 'value': action.default})
                        except Exception as e:
                            log.error("Error constructing child parameter '%s': %s", name, e)
                            self.widgets['log'].append(f"Error constructing child parameter '{name}': {e}")

            self.params = []
            
            for group_name, group_params in self.group_params_dict.items():
                self.params.append({
                    'name': group_name,
                    'type': 'group',
                    'children': group_params
                })

            def update_params_from_state(params, param_state) -> None:
                def update_param(param, state_key, state_value):
                    if isinstance(state_value, list):
                        if state_key.endswith('n_clusters'):
                            for child in param['children']:
                                cluster_id = int(child['name'])
                                if cluster_id in state_value:
                                    child['value'] = True
                                else:
                                    child['value'] = False
                    else:
                        param['value'] = state_value

                def recursive_update(params, param_state):
                    for param in params:
                        param_name = param['name']
                        if param_name in param_state:
                            update_param(param, param_name, param_state[param_name])
                        elif 'children' in param:
                            recursive_update(param['children'], param_state)

                recursive_update(params, param_state)

            update_params_from_state(self.params, self.param_state)

            self.pc = Parameter.create(name='selected_params', type='group', children=self.params)

            self.widgets['child ptree'].setParameters(self.pc, showTop=False)
            try:
                for param_name in self.selected_params:
                    self.pc.child(param_name).setOpts(expanded=(param_name == self.selected_params[-1]))
            except:
                None

            self.pc.sigTreeStateChanged.connect(self._update_opts_from_children_params)    

        self.p.sigTreeStateChanged.connect(param_changed)

    def _update_opts_from_children_params(self, param, changes) -> None:
        """
        Processes changes in the child parameter tree and updates the opts
        """
        for param, change, data in changes:
            if change:
                param_name = param.name()
                param_value = param.value()
                if '[' in param_name:
                    # Handling parameters specified as arrays
                    parent_name = param_name.split('[', 1)
                    child_array = []
                    # Searching for a value from the already set parameters
                    if hasattr(self.opts, parent_name[0]):
                        for param in self.params:
                            if param['name'] == parent_name[0].split('.', 1)[0]:
                                for child_param in param['children']:
                                    if child_param['name'] == parent_name[0]:
                                        if child_param['type'] == 'group':
                                            for array_param in child_param['children']:
                                                child_array.append(array_param['value'])
                    self._add_to_dict(parent_name[0],child_array,int(parent_name[1].replace(']', ''))-1,data)
                    setattr(self.opts, parent_name[0], self.selected_arrays[parent_name[0]])
                    self.param_state[param_name] = data
                    self.widgets['log'].append(f"{param_name} was changed to {data} in opts")
                elif param_name == 'BGVDTelescope.geometry_csv_file':
                    setattr(self.opts, param_name, param_value)
                    self.param_state[param_name] = data
                    self.widgets['log'].append(f"{param_name} was changed to {data} in opts")
                    # Update parameter with a check mark
                    self.p.child('Factories').child('telescope_name').child('BGVDTelescope').setValue(False)
                    self.p.child('Factories').child('telescope_name').child('BGVDTelescope').setValue(True)
                    self.p.child('Factories').child('telescope_name').setOpts(expanded=False)
                elif param.parent().name() == 'BGVDTelescope.n_clusters':
                    if data:
                        self.cluster_array.append(int(param_name))
                        self.cluster_array.sort()
                    else:
                        self.cluster_array.remove(int(param_name))
                    setattr(self.opts, param.parent().name(), self.cluster_array)
                    self.param_state[param.parent().name()] = self.cluster_array
                    self.widgets['log'].append(f"{param.parent().name()} was changed to {self.cluster_array} in opts")
                else:
                    setattr(self.opts, param_name, param_value)
                    self.param_state[param_name] = data
                    self.widgets['log'].append(f"{param_name} was changed to {data} in opts")
            
    def _update_opts_from_main_params(self, param, changes) -> None:
        """
        Processes changes to the main parameters and updates the opts
        """
        for param, change, data in changes:
            if change:
                param_name = param.name()
                param_value = param.value()
                if '[' in param_name:
                    parent_name = param_name.split('[', 1)
                    child_array = []
                    if hasattr(self.opts, parent_name[0]):
                        for param in self.main_params:
                            if param['name'] == parent_name[0]:
                                for child_param in param['children']:
                                    child_array.append(child_param['value'])

                    self._add_to_dict(parent_name[0],child_array,int(param_name.split('[')[1].split(']')[0])-1,data)
                    setattr(self.opts, parent_name[0], self.selected_arrays[parent_name[0]])
                    self.widgets['log'].append(f"{param_name} was changed to {data} in opts")
                else:
                    setattr(self.opts, param_name, param_value)
                    self.widgets['log'].append(f"{param_name} was changed to {data} in opts")

    def _add_to_dict(self, name, array, index, value) -> None:
        """
        Updates or initializes the dictionary for storing the values ​​of the parameter arrays
        """
        if name not in self.selected_arrays:
            self.selected_arrays[name] = array
        self.selected_arrays[name][index] = value

    def makeButtons(self) -> None:
        """Creates buttons and connects them to the appropriate methods"""
        self.buttons = {}
        self.buttons['load_config'] =  QPushButton("Load Config")
        self.buttons["run_ntsim"] =    QPushButton("Run Ntsim")
        self.buttons["run_h5viewer"] =    QPushButton("Run h5Viewer")

        self.buttons['run_ntsim'].clicked.connect(self.run_ntsim)
        self.buttons['load_config'].clicked.connect(self.load_config)
        self.buttons['run_h5viewer'].clicked.connect(self.run_h5viewer)

        self.docks["main"].addWidget(self.buttons['run_ntsim'])
        self.docks["main"].addWidget(self.buttons['load_config'])
        self.docks["main"].addWidget(self.buttons['run_h5viewer'])

    def configure(self,opts) -> None:
        self.options       = opts

    def load_config(self):
        """
        Loads a configuration from a CSV file and updates the corresponding parameters.
        Not developed for now.
        """
        fileName = QFileDialog.getOpenFileName()
        with open(fileName[0], 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                paramName = str(row[0])
                paramValue = str(row[1])
                for children in self.param.children():
                    for child in children:
                        if child.name() == paramName:
                            child.setValue(paramValue)

    def get_cluster_value(self):
        """
        Determines the number of clusters by reading a CSV file for BGVDTelescope.
        Returns the number of clusters or 0 on error.
        """
        csv_file_path = getattr(self.opts, 'BGVDTelescope.geometry_csv_file', None)
        if not csv_file_path:
            return 0
        try:
            with open(csv_file_path, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                rows = list(reader)
                if rows:
                    last_row = rows[-1]
                    if 'cluster' in last_row:
                        num_clusters = int(last_row['cluster'])
                        self.cluster_array = list(range(1, num_clusters + 1))
                        return num_clusters
        except Exception as e:
            log.error("Error reading cluster value from CSV: %s", e)
            return 0
        return 0
        
    def run_ntsim(self) -> None:
        """
        Configures the NTSim and starts the simulation process.
        """
        try:
            self.simu.configure(self.opts)
            self.simu.process(self.opts)
            self.widgets['log'].append("Simulation completed successfully.")
        except Exception as e:
            log.error("Error running Ntsim: %s", e)
            self.widgets['log'].append(f"Error running Ntsim: {e}")

    def run_h5viewer(self) -> None:
        """
        Launches the h5Viewer viewer.
        """
        try:
            from ntsim.Viewer.__main__ import h5Viewer, parser
            opts = parser.parse_args()
            
            self.h5viewer = h5Viewer()
            self.h5viewer.configure(opts)
            self.h5viewer.init()
            self.h5viewer.addDocksToArea(self.sc2_sub_dockarea)

            self.widgets['log'].append("h5Viewer Opened")
        except Exception as e:
            log.error("Error running h5Viewer: %s", e)
            self.widgets['log'].append(f"Error running h5Viewer: {e}")

    def update_output_label(self, text) -> None:
        """Updates the log by adding a new line of text"""
        self.widgets['log'].append(text)

def run(opts) -> None:
    app = QApplication(sys.argv)
    gui_ntsim = Gui()
    gui_ntsim.configure(opts)
    gui_ntsim.init()
    gui_ntsim.setWindowTitle('GUI2')
    gui_ntsim.resize(1600, 880)
    screen_resolution = app.desktop().screenGeometry()
    #width, height = screen_resolution.width(), screen_resolution.height()
    #width, height = width*opts.screen_fraction[0], height*opts.screen_fraction[1]
    #gui_ntsim.resize(int(width), int(height))
    gui_ntsim.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    import configargparse
    p = configargparse.get_argument_parser()
    
    #p.add_argument()
    opts = p.parse_args()
    run(opts)