# Copyright 2025 Daniil Shmelev
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========================================================================

import inspect
import warnings

import numpy as np
import torch

from .dtypes import SUPPORTED_DTYPES, SUPPORTED_DTYPES_STR

def get_type_str(type_):
    try:
        if hasattr(type_, '__name__'):
            return type_.__name__
        return str(type_)
    except:
        return "UNKNOWN"

def check_type(param, param_name, type_):
    if not isinstance(param, type_):
        raise TypeError(param_name + " must be of type " + get_type_str(type_) + ", got " + get_type_str(type(param)) + " instead")

def check_type_multiple(param, param_name, type_tuple):
    if not isinstance(param, type_tuple):
        type_tuple_str = ' or '.join(get_type_str(type_) for type_ in type_tuple)
        raise TypeError(param_name + " must be of type " + type_tuple_str + ", got " + get_type_str(type(param)) + " instead")

def check_non_neg(param, param_name):
    if param < 0:
        raise ValueError(param_name + " must be a non-negative integer, got " + param_name + " = " + str(param))

def check_dtype(arr, arr_name):
    if arr.dtype not in SUPPORTED_DTYPES:
        raise TypeError(arr_name + ".dtype must be " + SUPPORTED_DTYPES_STR + ", got " + str(arr.dtype) + " instead")

def check_dtype_double(arr, arr_name):
    if arr.dtype not in [np.float64, torch.float64]:
        raise TypeError(arr_name + ".dtype must be float64, got " + str(arr.dtype) + " instead")

def to_double(arr):
    if isinstance(arr, torch.Tensor):
        arr.to(dtype = torch.float64, copy = False)
    else:
        arr.astype(dtype = np.float64, copy = False)

def check_cpu(arr, arr_name):
    if isinstance(arr, torch.Tensor):
        if not arr.device.type == "cpu":
            raise ValueError(arr_name + " must be located on the cpu")

def warn(msg):
    frame = inspect.currentframe().f_back
    depth = 2
    while frame and frame.f_globals.get("__name__", "").startswith("pysiglib"):
        frame = frame.f_back
        depth += 1
    warnings.warn(msg, stacklevel=depth)

WARNED_ONCE_ABOUT_MEMORY = False
MEMORY_WARNING = "Detected a non-contiguous or view-based array. Such arrays will be cloned to ensure safe access. To avoid this overhead, pass arrays that are both contiguous and own their data. This warning will only appear once per session."

def ensure_own_contiguous_storage(arr):
    global WARNED_ONCE_ABOUT_MEMORY

    if isinstance(arr, torch.Tensor):
        is_view = arr._base is not None
        has_stride_0 = any(s == 0 for s in arr.stride())
        is_contiguous = arr.is_contiguous()
        if is_view or not is_contiguous or has_stride_0:
            if not WARNED_ONCE_ABOUT_MEMORY:
                warn(MEMORY_WARNING)
                WARNED_ONCE_ABOUT_MEMORY = True
            return arr.clone().contiguous()
        return arr

    if isinstance(arr, np.ndarray):
        owns_data = arr.base is None
        is_contiguous = arr.flags['C_CONTIGUOUS']
        if not owns_data or not is_contiguous:
            if not WARNED_ONCE_ABOUT_MEMORY:
                warn(MEMORY_WARNING)
                WARNED_ONCE_ABOUT_MEMORY = True
            return np.ascontiguousarray(arr.copy())
        return arr

    raise TypeError("Unexpected error in ensure_own_contiguous_storage: arr must be of type torch.Tensor or numpy.ndarray")
