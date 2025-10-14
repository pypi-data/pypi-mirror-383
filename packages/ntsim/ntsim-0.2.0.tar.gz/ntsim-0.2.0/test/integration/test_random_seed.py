import pytest
from ntsim.IO.h5Reader import h5Reader
import numpy as np

from setup import run_ntsim

def arrays_equal(a, b):
    return (a.data.shape==b.data.shape)and(a.dtype==b.dtype)and np.all(a==b)
    
def test_random_seeds_ToyGen(tmp_path):
    #define convenience functions

    def run_simulation(seed):
        output_file=f"test_{seed}"
        params = ["--generator ToyGen",
                  "--ToyGen.particle_pdgid 13",
                  "--ToyGen.tot_energy_GeV 10",
                  "--ToyGen.direction 0 0 1",
                  # "--ToyGen.random_position",
                  "--ToyGen.position_m -13.8 -211.9 95",
                  "--telescope BGVDTelescope --detector BGVDSensitiveDetector",
                  "--compute_hits --cherenkov=CherenkovGenerator",
                  f"--seed={seed}",
                  f"--H5Writer.h5_output_file={output_file}"]
        #run the simulation
        run_ntsim(' '.join(params), output_dir=tmp_path)
        # read the results
        with h5Reader(tmp_path/f"{output_file}.h5") as f:
            ev = f.events[0]
            tracks = ev.tracks.all()
            hits = ev.hits.all()
            photons = ev.photons.all()
        return tracks, photons, hits

    #run the simulation for two same seeds
    tracks_0, photons_0, hits_0 = run_simulation(seed=123)
    tracks_1, photons_1, hits_1 = run_simulation(seed=123)
        
    # assert arrays_equal(tracks_0, tracks_1), \
    # "Tracks for the same seed differ!"
    assert arrays_equal(photons_0.data, photons_1.data), \
    "Photons for the same seed differ!"
    if len(hits_0)!=0:
        assert arrays_equal(hits_0.data, hits_1.data), \
        "Hits for the same seed differ!"
    
    tracks_2, photons_2, hits_2 = run_simulation(seed=456)
    # assert not arrays_equal(tracks_0, tracks_2), \
    # "Tracks for the different seeds are equal!"
    assert not arrays_equal(photons_0.data, photons_2.data), \
    "Photons for the different seeds are equal!"
    if len(hits_0)!=0:
        assert not arrays_equal(hits_0.data, hits_2.data), \
        "Hits for the different seeds are equal!"
    