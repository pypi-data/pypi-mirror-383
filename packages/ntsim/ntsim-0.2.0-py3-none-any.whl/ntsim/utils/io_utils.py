"""
NTSim Utilities Module
======================

This module provides core utility functions for data handling and transformation
in the NTSim framework. It includes type conversion utilities, decorators for
class configuration, and optimized numerical operations.
"""

from dataclasses import InitVar, dataclass, is_dataclass
from typing import get_origin, get_args

from ntsim.IO.Base import StructData
from numba import njit
import numpy as np

def get_dtype(annotations) -> np.dtype:
    """Convert Python type annotations to NumPy structured dtype.
    
    Handles complex type definitions including:
    - InitVar fields (skipped)
    - np.ndarray with specified element types and shapes
    - Standard NumPy scalar types
    
    Parameters
    ----------
    annotations : dict
        Class __annotations__ dictionary
    
    Returns
    -------
    np.dtype
        Structured dtype suitable for NumPy record arrays
    
    Notes
    -----
    - Special handling for 'pos_m' and 'direction' fields (assumes 3-element shape)
    """
    dtype = []
    for field_name, field_type in annotations.items():
        origin = get_origin(field_type)
        if origin is InitVar:
            continue
        if origin is np.ndarray:
            args = get_args(field_type)
            element_dtype = args[1].__args__[0] if args else np.float64
            shape = (3,) if field_name in ('pos_m', 'direction') else ()
            dtype.append((field_name, element_dtype, shape))
        else:
            dtype.append((field_name, field_type))
    return np.dtype(dtype)

def s_string(string: str) -> np.ndarray:
    """Convert string to fixed-length byte array.
    
    Parameters
    ----------
    string : str
        Input string to convert
    
    Returns
    -------
    np.ndarray
        NumPy array of dtype 'S#' where # is string length
    """
    return np.asarray(string, dtype=f'|S{len(string)}')

def list_s_strings(list_strings: list) -> np.ndarray:
    """Convert list of strings to fixed-width byte array.
    
    Parameters
    ----------
    list_strings : list[str]
        List of strings to convert
    
    Returns
    -------
    np.ndarray
        1D array of byte strings with uniform width
    """
    max_len = len(max(list_strings, key=len, default=''))
    return np.asarray(list_strings, dtype=f"|S{max_len}")

def run_command(list_args: list) -> np.ndarray:
    """Serialize command-line arguments to byte array.
    
    Parameters
    ----------
    list_args : list[str]
        Command arguments to join and serialize
    
    Returns
    -------
    np.ndarray
        Single-element byte array containing space-joined arguments
    """
    return s_string(' '.join(list_args))

@njit("float64[:,:](UniTuple(float64[:],3))", cache=True)
def combine_fields_numba(fields_to_combine: tuple) -> np.ndarray:
    """Numba-optimized equivalent of np.stack(fields, axis=1) for 1D arrays.
    
    Parameters
    ----------
    fields_to_combine : tuple of np.ndarray
        1D arrays to combine with same length (N)
    
    Returns
    -------
    np.ndarray
        2D array of shape (N, M) where:
        - N: Number of elements per field
        - M: Number of fields (input arrays)
    """
    num_rows = fields_to_combine[0].shape[0]
    num_fields = len(fields_to_combine)
    combined_data = np.empty((num_rows, num_fields), dtype=np.float64)
    for i in range(num_rows):
        for j in range(num_fields):
            combined_data[i,j] = fields_to_combine[j][i]
    return combined_data