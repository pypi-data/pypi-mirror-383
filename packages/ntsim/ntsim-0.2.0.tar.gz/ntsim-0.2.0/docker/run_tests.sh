#!/bin/bash
source /software/setup.sh
#export LD_LIBRARY_PATH=/usr/local/lib/python3.10/dist-packages/nudisxs
#export LD_LIBRARY_PATH=/software/lhapdf-install/lib:$LD_LIBRARY_PATH

# nusidxs
python -m nudisxs.tests.test_dis
rm xs*pdf

# nuprop

# mumpropagator
#python tests/test_mumpropagator.sh

# g4camp

python -m g4camp.run_g4camp --gun_energy 10. -n 1
python -m g4camp.run_g4camp --gun_energy 10. --enable_optics -n 1

# ntsim


#

rm -rf /workdir/*
