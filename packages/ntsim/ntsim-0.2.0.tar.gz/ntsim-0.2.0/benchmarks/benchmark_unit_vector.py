from gen_utils import unit_vector, unit_vector_numba
import numpy as np
from time import time
import timeit

def test_sqrt_numpy_version(n=1000000):
    t0 = time()
    v = np.array([1,1,1])
    v = np.tile(v,(n,1))
    t1 = time()
    v = np.sqrt(v)
    t2 = time()
    mask = v**2
    t3 = time()
    print(f'test_sqrt_numpy_version: initializing {t1-t0}')
    print(f'test_sqrt_numpy_version: sqrt calculation {t2-t1}')
    print(f'test_sqrt_numpy_version: mask calculation {t3-t2}')


def test_numpy_version(n=1000000):
#    t0 = time()
    v = np.array([1,1,1])
    v = np.tile(v,(n,1))
#    t1 = time()
    unit_v = unit_vector(v)
#    t2 = time()
#    print(f'test_numpy_version: initializing {t1-t0}')
#    print(f'test_numpy_version: calculation {t2-t1}')

def test_numba_version(n=1000000,log=''):
#    t0 = time()
    v = np.array([1,1,1])
    v = np.tile(v,(n,1))
#    t1 = time()
    unit_v = unit_vector_numba(v)
#    t2 = time()
#    print(log)
#    print(f'test_numba_version: initializing {t1-t0}')
#    print(f'test_numba_version: calculation {t2-t1}')
# run the tests as follows
# python -mtimeit -s'import test_unit_vector' 'test_unit_vector.test_numpy_version'
# 10000000 loops, best of 5: 33.9 nsec per loop
# python -mtimeit -s'import test_unit_vector' 'test_unit_vector.test_numba_version'
# 10000000 loops, best of 5: 31.7 nsec per loop

#test_sqrt_numpy_version()
#timeit.Timer(test_numpy_version).timeit(number=1000)
#test_numpy_version()
#test_numba_version(log='before compilation')
#test_numba_version(log='after compilation')
