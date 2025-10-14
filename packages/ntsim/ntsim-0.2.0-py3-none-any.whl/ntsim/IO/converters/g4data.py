"This module contains methods for conversion from g4camp data to ontsim.IO classes"

from ntsim.IO.gTracks import gTracks
from ntsim.IO.gParticles import gParticles
from ntsim.IO.gPhotons import gPhotons
import numpy as np

def to_Tracks(g4data)->gTracks:
    position = np.column_stack([g4data[name] for name in ['x_m', 'y_m', 'z_m']])
    return gTracks(size = len(g4data),
                    uid =   g4data['uid'],
                    pdgid = g4data['pdgid'],
                    pos_m = position,
                    t_ns =  g4data['t_ns'],
                    Etot_GeV = g4data['Etot_GeV'],
                    step_length_m = g4data['step_length_m'],
                   )

def to_Photons(g4data)->gPhotons:
    position = np.column_stack([g4data[name] for name in ['x_m', 'y_m', 'z_m']])
    direction = np.column_stack([g4data[name] for name in ['dir_x', 'dir_y', 'dir_z']])
    return gPhotons(size = len(g4data),
               pos_m = position,
               t_ns =  g4data['t_ns'],
               direction = direction,
               wl_nm =   g4data['wl_nm']
              )


def to_Particles(g4data)->gParticles:
    position = np.column_stack([g4data[name] for name in ['x_m', 'y_m', 'z_m']])
    direction = np.column_stack([g4data[name] for name in ['dir_x', 'dir_y', 'dir_z']])
    return gParticles(size = len(g4data),
               uid = g4data['uid'],
               pos_m = position,
               pdgid = g4data['pdgid'],
               t_ns = g4data['t_ns'],
               Etot_GeV = g4data['Etot_GeV'],
               direction = direction,
              )