import numpy as np
import numpy.typing as npt
from ntsim.IO.Base.StructData import StructData

class gTracks(StructData):
    
    uid: np.int64              = 0 #Unique identifier of the track vertex.
    pdgid: np.int64            = 0 #Particle Data Group identifier of the particle.
    pos_m: npt.NDArray[np.float64] = (0,0,0) #Position of the track vertex in meters.
    t_ns: np.float64           = 0 #Time of the track vertex in nanoseconds.
    Etot_GeV: np.float64       = 0 #Total energy of the particle in GeV.
    step_length_m: np.float64  = 0 #Step length of the track in meters.