import logging
from time import time
from functools import wraps

def report_timing(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        module_name = func.__module__.split('.')[-1]
        logger = logging.getLogger(f'NTSim.{module_name}')
        tic = time()
        result = func(*args, **kwargs)
        toc = time()
        dt = toc - tic
        logger.info(f'{func.__name__} (...)'.ljust(40)+f'{dt:6.3f} s'.rjust(30))
        return result
    return func_wrapper
