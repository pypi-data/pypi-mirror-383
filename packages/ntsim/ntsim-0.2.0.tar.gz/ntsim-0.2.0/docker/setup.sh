#!/bin/bash

# LHAPDF
export LD_LIBRARY_PATH=/usr/local/lib/python3.10/dist-packages/nudisxs:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/software/lhapdf-install/lib:$LD_LIBRARY_PATH

source /software/geant4-v11.0.0-install/bin/geant4.sh

export PYTHONPATH=/software/ntsim/:/software/bgvd-model/:$PYTHONPATH
