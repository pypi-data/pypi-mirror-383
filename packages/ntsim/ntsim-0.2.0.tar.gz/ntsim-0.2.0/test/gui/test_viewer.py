import subprocess
import os
import sys
import time
from configargparse import Namespace
import pytest
from types import SimpleNamespace
from PyQt5.QtWidgets import QApplication
from ntsim.Viewer.__main__ import h5Viewer, parser

from PyQt5.QtTest import QTest

def run_ntsim(params, output_dir, check=True):
    """run the shell command. If 'check==True' check that returncode is 0"""
    cmd = [
        sys.executable, '-m', 'ntsim'
    ] + params.split() + ["--H5Writer.h5_output_dir", str(output_dir)]
    print("Running simulation:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check:
        result.check_returncode()
    return result

"""fixture for a single instance of QApplication"""
@pytest.fixture(scope="session")
def app():
    app = QApplication(sys.argv)
    return app

"""fixture for a Viewer application"""
@pytest.fixture
def create_viewer(app):
    def _create_viewer(h5_file):
        print(f'{h5_file=}')
        opts = parser.parse_args(str(h5_file))
        print(opts)
        viewer = h5Viewer()
        viewer.configure(opts)
        viewer.init()
        return viewer
    return _create_viewer

"""fixture for output dir"""
@pytest.fixture
def output_dir(tmp_path):
    return tmp_path / "h5_output"

# function to check that the viewer has loaded at least minimal data (eg. ProductionHeader)
def check_viewer_state(viewer):
    state_keys = list(viewer.state_dict.keys())
    assert 'ProductionHeader' in state_keys, "ProductionHeader not found in viewer"

# time to “display” and process events
def process_viewer_events(app, duration_ms=15000):
    QTest.qWait(duration_ms)
    app.processEvents()

"""Tests for different simulation scenarios"""
def test_run_ToyGen(output_dir, create_viewer, app):
    run_ntsim("--generator ToyGen --generator ToyGen --cherenkov CherenkovGenerator --telescope BGVDTelescope --detector BGVDSensitiveDetector --compute_hits --ToyGen.particle_pdgid 13 --ToyGen.tot_energy_GeV 100 --ToyGen.position_m 35 35 0 --n_events 2 --depth 2", output_dir)
    
    h5_file = output_dir / "events.h5"
    assert os.path.exists(h5_file), f"File {h5_file} not found for ToyGen simulation"
    
    viewer = create_viewer(h5_file)
    process_viewer_events(app)
    check_viewer_state(viewer)
    viewer.close()

def test_run_Laser(output_dir, create_viewer, app):
    run_ntsim("--generator Laser --Laser.wavelength 400 --writer H5Writer --H5Writer.h5_save_event photons",
              output_dir)
    h5_file = output_dir / "events.h5"
    assert os.path.exists(h5_file), f"File {h5_file} not found for Laser simulation"
    
    viewer = create_viewer(h5_file)
    process_viewer_events(app)
    check_viewer_state(viewer)
    viewer.close()

def test_run_SolarPhotons(output_dir, create_viewer, app):
    run_ntsim("--generator SolarPhotons --photon_propagator MCPhotonPropagator --MCPhotonPropagator.n_scatterings 20",
              output_dir)
    h5_file = output_dir / "events.h5"
    assert os.path.exists(h5_file), f"File {h5_file} not found for SolarPhotons simulation"
    
    viewer = create_viewer(h5_file)
    process_viewer_events(app)
    check_viewer_state(viewer)
    viewer.close()

def test_run_Laser_with_BGVD_compute_hits(output_dir, create_viewer, app):
    run_ntsim("--generator Laser --Laser.position_m -13.8 -211.9 95 --telescope BGVDTelescope "
             "--detector BGVDSensitiveDetector --compute_hits",
             output_dir)
    h5_file = output_dir / "events.h5"
    assert os.path.exists(h5_file), f"File {h5_file} not found for Laser_with_BGVD_compute_hits simulation"
    
    viewer = create_viewer(h5_file)
    process_viewer_events(app)
    check_viewer_state(viewer)
    viewer.close()

def test_run_Muon_with_BGVD_produces_hits(output_dir, create_viewer, app):
    run_ntsim("--generator ToyGen --ToyGen.tot_energy_GeV 1000 --ToyGen.position_m 186.75 213 95 "
             "--telescope BGVDTelescope --detector BGVDSensitiveDetector --compute_hits --cherenkov CherenkovGenerator",
             output_dir)
    h5_file = output_dir / "events.h5"
    assert os.path.exists(h5_file), f"File {h5_file} not found for Muon_with_BGVD_produces_hits simulation"
    
    viewer = create_viewer(h5_file)
    process_viewer_events(app)
    check_viewer_state(viewer)
    viewer.close()

def test_run_Laser_with_diffuser(output_dir, create_viewer, app):
    run_ntsim("--generator Laser --Laser.diffuser exp 5", output_dir)
    h5_file = output_dir / "events.h5"
    assert os.path.exists(h5_file), f"File {h5_file} not found for Laser_with_diffuser simulation"
    
    viewer = create_viewer(h5_file)
    process_viewer_events(app)
    check_viewer_state(viewer)
    viewer.close()
