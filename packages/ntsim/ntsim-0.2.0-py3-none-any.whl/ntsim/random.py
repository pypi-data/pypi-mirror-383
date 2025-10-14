"""This module implements a global random state to be used throughout NTSim package


Usage: `rng` object is a wrapper to inner `numpy.random.default_rng` (returning `numpy.random._generator.Generator` object)

    >>> from ntsim.random import rng
    >>> rng.uniform(0,1, size=10) #generate some random numbers

Also use `set_seed` function to globally set the RNG state:
    >>> from ntsim.random import rng, set_seed
    >>> set_seed(123)
    >>> rng.uniform(size=2)
    array([0.68235186, 0.05382102])
    >>> set_seed(123)
    >>> rng.uniform(size=2) #get same numbers again
    array([0.68235186, 0.05382102])

when `set_seed` is called in one module, other modules using `rng` will use the updated random state.

Additionally `set_seed` sets the global state for numba and for numpy default random generator
"""
import numpy as np
from numba import njit
@njit
def numba_set_seed(value):
    np.random.seed(value)

_rng = np.random.default_rng()

def set_seed(value):
    """Initialize a new generator with a random seed"""
    global _rng
    _rng = np.random.default_rng(seed=value)
    #additionally set the seed for numba globally, to support the methods using np.random.* directly
    if value is not None:
        numba_set_seed(value)
    #additionally set the seed for numpy globally
    np.random.seed(value)


class _wrapper_rng:
    """A class that will redirect all calls to the global variable"""
    def __dir__(self):
        global _rng
        return dir(_rng)
    def __getattr__(self, name):
        global _rng
        return getattr(_rng,name)

rng = _wrapper_rng()