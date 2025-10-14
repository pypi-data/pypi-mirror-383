import numpy as np
import numpy.typing as npt
from ntsim.IO.Base.StructData import StructData

class gPhotons(StructData):
    pos_m: npt.NDArray[np.float64] = (0,0,0) #Position of the track vertex in meters
    t_ns: np.float64               = 0 #Time of the track vertex in nanoseconds.
    direction: npt.NDArray[np.float64] = (0,0,1) #Direction of the particle.
    wl_nm: np.float64              = 0 #Wavelength of the photon in nanometers.
    weight: np.float64             = 0 #Weight of the photon.
    ta_ns: np.float64              = 0 #Absorption time of the photon in nanoseconds.
    track_uid: np.int64            = -1 #Unique identifier of the track that produced the photon