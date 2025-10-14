#!/bin/bash
set -e

export PYTHONPATH=/software/ntsim:$PYTHONPATH
export PYTHONPATH=/software/g4camp:$PYTHONPATH
export PYTHONPATH=/software/bgvd-model:$PYTHONPATH
export PYTHONPATH=/software/nupropagator:$PYTHONPATH
export PYTHONPATH=/software/nudisxs/_skbuild/linux-x86_64-3.10/cmake-install/nudisxs:$PYTHONPATH
export PYTHONPATH=/software/LHAPDF-6.5.3-install/lib/python3.10/site-packages:$PYTHONPATH
export LD_LIBRARY_PATH=/usr/local/lib/python3.10/dist-packages/nudisxs:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/software/LHAPDF-6.5.3-install/lib:$LD_LIBRARY_PATH
export PATH=/software/LHAPDF-6.5.3-install/bin:$PATH

source /software/geant4-v11.2.1-install/bin/geant4.sh

exec "$@"
