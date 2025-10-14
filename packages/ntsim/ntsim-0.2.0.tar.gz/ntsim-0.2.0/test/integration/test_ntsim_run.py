import pytest
import subprocess
from ntsim.IO.h5Reader import h5Reader


def run_shell(cmd, check=True):
    """run the shell command. If 'check==True' check that returncode is 0"""
    
    print(f'Running in shell: {cmd}')
    p = subprocess.run(cmd.split(), capture_output=True)
    if check:
        try:
            p.check_returncode()
        except subprocess.CalledProcessError:
            print(str(p.stdout, 'utf-8'))
            print(str(p.stderr, 'utf-8'))
            raise
    return p

def run_ntsim(params, output_dir=None, check=True):
    """run the ntsim with given output directory. 
    If 'check'==True, raises CalledProcessError, if the process exited with nonzero status.
    """
    if output_dir:
        params+=" --H5Writer.h5_output_dir "+str(output_dir)
    return run_shell("python3 -m ntsim "+params, check=check)

def test_basic_run_ToyGen(tmp_path):
    run_ntsim("--generator ToyGen --ToyGen.particle_pdgid 13 --ToyGen.tot_energy_GeV 2", output_dir=tmp_path)
    #check file contents
    with h5Reader(tmp_path/"events.h5") as f:
        #check that we have only one event
        assert list(f.keys())==['Header','event_0']
        assert len(f.events)==1
        #check the event contents
        event = f.events[0]
        assert event.particles, "Particles must not be empty"
        assert event.tracks, "Tracks must not be empty"
        assert event.photons == {}, "No photons requested"
        assert event.hits == {}, "No hits requested"
        #check the primary particle
        primaries = event.particles['Primary']
        assert len(primaries)==1, "Expect one primary particle"
        t=primaries[0]
        assert t['pdgid']==13, "Expect muon primary"
        assert t['Etot_GeV']==2.0, "Expect 2 GeV muon"
        #check that we have tracks
        tracks = event.tracks['g4_tracks_0']
        assert abs(tracks.Etot_GeV[0]-2.0)/2.0 < 1e-5, "Expect initial muon Etot is around 2 GeV"
        assert len(tracks)>0
        #check that we have specific particles' tracks in geant simulation
        particles = set(tracks.pdgid)
        assert 13 in particles, "Must have muon tracks"
        assert 11 in particles, "Must have electron tracks"
        assert 22 in particles, "Must have photon tracks"
    

def test_run_Laser(tmp_path):
    #Generate photons in (0, 0, 0,) directed up (0, 0, 1)
    run_ntsim("--generator Laser --Laser.wavelength 400 --writer H5Writer --H5Writer.h5_save_event photons", output_dir=tmp_path)
    #Result: events.h5 file which has only 'photons' folder in event (set by H5Writer)
    with h5Reader(tmp_path/"events.h5") as f:
        assert f.events[0].photons["Laser"], "Expected photons from Laser"

def test_run_IsotropicSource(tmp_path):
    run_ntsim("--generator IsotropicSource --writer H5Writer --H5Writer.h5_save_event photons", output_dir=tmp_path)
    #Result: events.h5 file which has only 'photons' folder in event (set by H5Writer)
    with h5Reader(tmp_path/"events.h5") as f:
        assert f.events[0].photons["IsotropicSource"], "Expected photons from IsotropicSource"
        

def test_run_SolarPhotons(tmp_path):
    #Generate photons from the Sun which are propagated in 20 steps. This is an example of photon propagator.
    run_ntsim("--generator SolarPhotons --photon_propagator MCPhotonPropagator --MCPhotonPropagator.n_scatterings 20", output_dir=tmp_path)
    #Result: events.h5 file with data about photons and 'event_0/photons/photons_j/r' tables has 20 horizontal strings which are coordinates of photons at each scattering step
    with h5Reader(tmp_path/"events.h5") as f:
        #loop over all photons
        for name, photons in f.events[0].photons["SolarPhotons"].items():
            assert photons.pos_m.shape[1]==20, "Expected excatly 20 scatterings"

def test_run_Laser_with_BGVD_compute_hits(tmp_path):
    #Generate photons directed up (0, 0, 1) and configure Telescope with detector's effects. --compute_hits provides option for writer to save geometry and for ray_tracer for calculating hits.
    run_ntsim("--generator Laser --Laser.position_m -13.8 -211.9 95  --telescope BGVDTelescope --detector BGVDSensitiveDetector --compute_hits", output_dir=tmp_path)
    #Result: events.h5 file with event data and geometry folder which has data about telescope's configuration
    with h5Reader(tmp_path/"events.h5") as f:
        assert 'geometry' in f['Header'], "File must have 'geometry' folder with telescope description"
        hits = f.events[0].hits['Hits']
        assert len(hits)>=7000, "We expect at least 7000 hits" 
        
def test_run_Muon_with_BGVD_produces_hits(tmp_path):
    #Generate muon and configure Telescope with detector's effects. --compute_hits provides option for writer to save geometry and for ray_tracer for calculating hits.
    run_ntsim("--generator ToyGen --ToyGen.tot_energy_GeV 1000 --ToyGen.position_m -13.8 -211.9 95  --telescope BGVDTelescope --detector BGVDSensitiveDetector --compute_hits --cherenkov=CherenkovGenerator", output_dir=tmp_path)
    #Result: events.h5 file with event data and geometry folder which has data about telescope's configuration
    with h5Reader(tmp_path/"events.h5") as f:
        assert 'geometry' in f['Header'], "File must have 'geometry' folder with telescope description"
        assert  'Hits' in f.events[0].hits, "No 'Hits' in 'event_0/hits'."
        
def test_run_Laser_with_diffuser(tmp_path):
    #Generate photons directed up (0, 0, 1) with diffuser
    run_ntsim("--generator Laser --Laser.diffuser exp 5", output_dir=tmp_path)
    #Result: events.h5 file with event data and geometry folder which has data about telescope's configuration
    with h5Reader(tmp_path/"events.h5") as f:
        assert len(f.events)==1,"File must have one event"

def test_run_Laser_with_BGVDTrigger(tmp_path):
    #Generate photons directed up (0, 0, 1) and configure Telescope with detector's effects. --compute_hits provides option for writer to save geometry and for ray_tracer for calculating hits.
    #This is a test for BGVDTrigger including BGVDElectroincs and BGVDTriggerConditions
    begin_line = "--generator Laser --Laser.position_m 186 212 97 --telescope BGVDTelescope --BGVDTelescope.position_m 0 0 0 --detector BGVDSensitiveDetector --compute_hits --photon_propagator MCPhotonPropagator --MCPhotonPropagator.n_scatterings 3 "
    #Default BGVDElectronics without BGVDTriggerConditions
    run_ntsim(begin_line + "--trigger BGVDTrigger --BGVDTrigger.electronics_preset default --BGVDTrigger.trigger_preset off", output_dir=tmp_path)
    #Result: events.h5 file with Hits and TriggerHits containg hits only after Electronics (i.e. no trigger conditions)
    with h5Reader(tmp_path/"events.h5") as f:
        event = f.events[0]
        assert 'Hits' in event.hits, "File must have 'Hits' table with original hits provided by RayTracer"
        assert 'TriggerHits' in event.hits, "File must have 'TriggerHits' table with hits went through BGVDTrigger: BGVDElectronics"
        thits = event.hits['TriggerHits']
        uid_mask = thits['uid'] == thits['uid'][0]
        dt = thits[uid_mask]['t_ns'][-1] - thits[uid_mask]['t_ns'][0]
        assert dt <= 110 and dt >= 90, "Pulse's duration in one detector must be around 100 ns"

def test_run_ToyGen_with_BGVDTrigger(tmp_path):    
    #Default BGVDElectronics with BGVDTriggerConditions with zero limits
    begin_line = "--generator ToyGen --ToyGen.position_m 186 212 50 --ToyGen.direction 0 0 1 --ToyGen.tot_energy_GeV 300 --cherenkov CherenkovGenerator --telescope BGVDTelescope --BGVDTelescope.position_m 0 0 0 --detector BGVDSensitiveDetector --compute_hits --photon_propagator MCPhotonPropagator --MCPhotonPropagator.n_scatterings 4 "
    run_ntsim(begin_line + "--trigger BGVDTrigger --BGVDTrigger.electronics_preset default --BGVDTrigger.trigger_preset zero_limits", output_dir=tmp_path)
    #Result: events.h5 file with Hits and TriggerHits containg hits only after Electronics (i.e. no trigger conditions)
    with h5Reader(tmp_path/"events.h5") as f:
        event = f.events[0]
        assert 'Hits' in event.hits, "File must have 'Hits' table with original hits provided by RayTracer"
        assert 'TriggerHits' in event.hits, "File must have 'TriggerHits' table with hits went through BGVDTrigger: BGVDElectronics"
        thits = event.hits['TriggerHits']
        hits = event.hits['Hits']
        thits_n_uid = len(set(thits['uid']))
        hits_n_uid = len(set(hits['uid']))
        assert thits_n_uid <= hits_n_uid, "Number of worked detectors must be less (or equal) with Trigger than without it"