import numpy as np
from ntsim.IO.Base.StructData import StructData

class gHits(StructData):
    uid:  np.int64    = 0 #Unique identifier of the hit.
    t_ns: np.float64 = 0 #Time of the hit in nanoseconds.
    phe:  np.float64  = 0 #Number of photoelectrons in the hit.
    track_uid: np.int64 = -1 #Unique identifier of the track that produced the hit
