import numpy as np

from dataclasses import dataclass, field
from typing import Dict, Iterator

from ntsim.IO.gParticles import gParticles
from ntsim.IO.gPhotons import gPhotons 
from ntsim.IO.gTracks import gTracks
from ntsim.IO.gHits import gHits
from ntsim.IO.Base.StructData import StructContainer

class gEvent(StructContainer):
    particles: Dict[str,gParticles] = field(default_factory=dict)
    photons:   Dict[str, Iterator[gPhotons]] = field(default_factory=dict)
    tracks:    Dict[str,gTracks]    = field(default_factory=dict)
    hits:      Dict[str,gHits]      = field(default_factory=dict)
    cloner_hits: Dict[str,gHits]    = field(default_factory=dict)
    # cloner_shifts: np.ndarray[np.float64] = np.empty(shape=(0,3), dtype=np.float64)