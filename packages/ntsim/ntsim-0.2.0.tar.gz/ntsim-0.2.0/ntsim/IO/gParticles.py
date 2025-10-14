import numpy as np
import numpy.typing as npt
from ntsim.IO.Base.StructData import StructData

class gParticles(StructData):
    uid: np.int64                  = 0 #Unique identifier of the track vertex.
    pdgid: np.int64                = 0 #Particle Data Group identifier of the particle.
    pos_m: npt.NDArray[np.float64] = (0,0,0) #Position of the track vertex in meters.
    t_ns: np.float64               = 0 #Time of the track vertex in nanoseconds.
    direction: npt.NDArray[np.float64] = (0,0,0) #Direction of the particle
    Etot_GeV: np.float64           = 0 #Total energy of the particle in GeV
    
    #additional flags   
    to_propagate = True
    gen_cher = False
