#!/bin/env python3

#run this file from the shell, to set the variables:
#
# $source <(./set_g4data_paths.py)
#
#or run it from a python script, before calling geant4_pybind:
#
# from set_g4data_paths import set_g4data_paths
# set_g4data_paths()

import os
import sys
from pathlib import Path

dir_mapping = {
    "G4ABLADATA":"G4ABLA",
    "G4LEDATA":"G4EMLOW",
    "G4ENSDFSTATEDATA":"G4ENSDFSTATE",
    "G4INCLDATA":"G4INCL",
    "G4NEUTRONHPDATA":"G4NDL",
    "G4PARTICLEXSDATA":"G4PARTICLEXS",
    "G4PIIDATA":"G4PII",
    "G4SAIDXSDATA":"G4SAIDDATA",
    "G4LEVELGAMMADATA":"PhotonEvaporation",
    "G4RADIOACTIVEDATA":"RadioactiveDecay",
    "G4REALSURFACEDATA":"RealSurface"
}

def set_g4data_paths():
# Mapping from directory prefixes to G4*DATA variables
    base_dir = os.getenv("GEANT4_DATA_DIR", "$HOME/.geant4_pybind")
    base_path = Path(base_dir)
    new_env = {}
    #search for the matching dir in the base_dir
    for envar, dirname in dir_mapping.items():
        dirs = list(base_path.glob(f"{dirname}*"))
        if len(dirs)>0:
            new_env[envar] = dirs[-1] #base_path/dirname)
        else:
            print(f'{envar} not found in {dirname}', file=sys.stderr)

    #set the env variables
    for name,val in new_env.items():
        print(f'export {name}="{str(val)}"')
        os.environ[name] = str(val)

if __name__=="__main__":
    set_g4data_paths()
