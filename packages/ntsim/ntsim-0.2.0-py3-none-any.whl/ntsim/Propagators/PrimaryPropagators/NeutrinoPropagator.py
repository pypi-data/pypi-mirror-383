from ntsim.Propagators.Base.PropagatorBase import PropagatorBase
from ntsim.IO.gTracks import gTracks
import nupropagator.flux.Flux as flux
import numpy as np

class nuPropagator(PropagatorBase):
    def __init__(self):
        self.module_type = "propagator"
        self.propagator = None
        self.name = 'nuPropagator'

    def configure(self,opts):
        from nupropagator import NuPropagator 
        self.propagator = NuPropagator.NuPropagator(opts)
        self.propagator.prepare_propagation()

    def propagate(self,event):
        tracks = gTracks("nu_tracks", gen_cher=False)
        ev = event.particles[0].get_named_data()[0]
        self.info = self.propagator.get_dragging()
        info = [0,ev['pdgid'],[ev['x_m'],ev['y_m'],ev['z_m']],ev['time_ns'],ev['E_tot_GeV'],0.]
        tracks.from_custom_array(info, tracks.data_type.names)
        self.info = self.propagator.get_dragging()
        ev = event.particles[0].get_named_data()[1]
        info = [0,ev['pdgid'],[ev['x_m'],ev['y_m'],ev['z_m']],ev['time_ns'],ev['E_tot_GeV'],np.sqrt(np.sum((fposition - iposition)**2))]
        tracks.from_custom_array(info, tracks.data_type.names)
        print(info)
        event.tracks = tracks