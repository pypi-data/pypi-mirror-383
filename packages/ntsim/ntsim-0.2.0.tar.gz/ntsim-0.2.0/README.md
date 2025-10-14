# NeutrinoTelescopeSimulation

[![PyPI - Version](https://img.shields.io/pypi/v/ntsim.svg)](https://pypi.org/project/ntsim)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ntsim.svg)](https://pypi.org/project/ntsim)

-----

**Table of Contents**

- [Installation](#installation)
- [Simulation](#Simulation)
- [Output format](#Output-format)
- [3D Viewer](#3D-Viewer)
- [License](#License)

## Installation

```console
pip install ntsim
```

If you also want to run the GUI utils (see [#Viewer](#Viewer) section), you need to install the optional dependencies:
```shell
pip install ntsim[gui]

```
## Simulation

NTSim can be run as python module.

```shell
python -m ntsim -h
```
to see the basic command line arguments


### Simulate 2GeV muon in a water volume
```shell
python3 -m ntsim --generator ToyGen --ToyGen.particle_pdgid 13 --ToyGen.tot_energy_GeV 2 --H5Writer.h5_output_file="muon_sim"
```

This will produce a file `"h5_output/muon_sim.h5"` with the information about primary track, secondary produced tracks and energy loss steps of each track.

**Note**: this won't produce hits, unless you give a `--compute-hits` flag, and provide a telescope and detector for simulation 

### Simulate a 1TeV muon in an example telescope with hits
```shell
python3 -m ntsim --generator ToyGen --ToyGen.particle_pdgid 13 --ToyGen.tot_energy_GeV 1000 --H5Writer.h5_output_file="1TeV_muon_sim" --compute_hits --telescope=Example1Telescope --detector=Example1SensitiveDetector
```
This procudes a file `"h5_output/1TeV_muon_sim.h5"` which, in addition to MC track information, contains the hits, produced in the sensitive detectors.

## Output format

Currently the only output format is the hdf5 file with the following tree structure:

*  `ProductionHeader/`: describe the full information about the run configuration.
* `geometry/`
    * `Bounding_Surfaces`: dataset with the geometrical hierarchy of the telescope
    * `Geometry`: dataset describing the individual modules position and geometry
* `event_<n>/`: group for each simulated event
    * `event_header/` general event information (metadata)        
    * `hits/Hits`: dataset with the hits in the sensitive detectors
    * `particles/` information about primary particles.
        * `Primary` dataset for primary particles, to be processed by ParticlePropagator
        *  `g4_cascade_starters_<n>` datasets, containing secondary particles which start the parametrized cascades
    * `photons/photons_<n>/`  groups for photons information
        
    * `tracks/g4_tracks_<n>` results of the Geant4 propagation 

## 3D Viewer

Viewer reads `ntsim_events.h5` file and displays information from file. It allows to watch animation of particles propagation in 3D, it also can build histograms of physical parametres. Viewer helps to analyse results of simulation.

### Running

```shell
python3 -m ntsim.Viewer  
```
this will run an "open file" dialog to choose the simulation file to display.

```shell
python3 -m ntsim.Viewer h5_output/events.h5 
```
This will open defaut file named `"h5_output/events.h5"` produced by __NTSim__.

#### Some Options
If the display works slow, try to set minimal track length bigger.
```shell
python3 -m ntsim.Viewer h5_output/events.h5 --min_length_for_tracks 1
```
This will show only tracks bigger than 1 m.

To increase speed of animation try to set less amount of frames.
```shell
python3 -m ntsim.Viewer h5_output/events.h5 --animation_frames 10 0 3000
```
This will show only 10 frames in time interval from 0 to 3000


## License

`ntsim` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
