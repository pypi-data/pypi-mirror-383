from commands.pt_init_photons import photons_custom
from commands.pt_init_kernel import pt_init_kernel
from commands.pt_propagate_photons import pt_propagate_photons
from gen_utils import position_numba
from PhotonTransport import PhotonTransport
import logging
import click_log
from time import time
import numpy as np

logger = logging.getLogger(__name__)
click_log.basic_config(logger)
pt = PhotonTransport(logger)

def init(steps=5,tracks=10,waves=(350,650),t0=0.0,r0=(0.0,0.0,0.0),dir0=(0.0,0.0,1.0),
          scattering_model='HG+Rayleigh',anisotropy=0.98):
    photons_custom(pt,steps,tracks,waves,t0,r0,dir0)
    pt_init_kernel(pt,scattering_model,anisotropy)
    pt_propagate_photons(pt)

init()
def test_numba_version(t):
    tic = time()
    x,y,z = pt.photons.position_fast(t)
    toc = time()
    print(f'test_numba_version: elapsed time {toc-tic}')
    return x,y,z

def test_numpy_version(t):
    tic = time()
    x,y,z = pt.photons.position(t)
    toc = time()
    print(f'test_numpy_version: elapsed time {toc-tic}')
    return x,y,z


test_numba_version(np.array([100,200.]))
test_numpy_version(np.array([100,200.]))
