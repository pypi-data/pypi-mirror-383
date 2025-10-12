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

import os
import sys
import platform
import ctypes
from ctypes import c_float, c_double, c_int, c_int32, c_int64, c_uint64, c_bool, POINTER

######################################################
# Figure out how pysiglib was built, in particular
# whether CUDA is being used
######################################################

try:
    from ._config import SYSTEM, BUILT_WITH_CUDA, BUILT_WITH_AVX
except ImportError as exc:
    raise RuntimeError("Could not import configuration properties from _config.py - package may not have been built correctly.") from exc

if SYSTEM != platform.system():
    raise RuntimeError("System on which pySigLib was built does not match the current system - package may not have been built correctly.")

######################################################
# Load the cpsig and cusig libraries
######################################################

CPSIG, CUSIG = None, None

# winmode = 0 is necessary here
# https://github.com/NVIDIA/warp/issues/24

DIR_ = os.path.dirname(sys.modules['pysiglib'].__file__)

if SYSTEM == 'Windows':
    CPSIG_PATH = os.path.join(DIR_, 'cpsig.dll')
    CPSIG = ctypes.CDLL(CPSIG_PATH, winmode = 0)

    if BUILT_WITH_CUDA:
        CUSIG_PATH = os.path.join(DIR_, 'cusig.dll')
        CUSIG = ctypes.CDLL(CUSIG_PATH, winmode=0)
elif SYSTEM == "Linux":
    CPSIG_PATH = os.path.join(DIR_, 'libcpsig.so')
    CPSIG = ctypes.CDLL(CPSIG_PATH, winmode=0)

    if BUILT_WITH_CUDA:
        CUSIG_PATH = os.path.join(DIR_, 'libcusig.so')
        CUSIG = ctypes.CDLL(CUSIG_PATH, winmode=0)
elif SYSTEM == 'Darwin':
    CPSIG_PATH = os.path.join(DIR_, 'libcpsig.dylib')
    CPSIG = ctypes.CDLL(CPSIG_PATH)
else:
    raise Exception("Unsupported OS during pysiglib.py")

######################################################
# Set argtypes and restypes for all imported functions
######################################################

######################################################
# transform_path
######################################################

CPSIG.transform_path_float.argtypes = (
    POINTER(c_float),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double
)
CPSIG.transform_path_float.restype = c_int

CPSIG.transform_path_double.argtypes = (
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double
)
CPSIG.transform_path_double.restype = c_int

CPSIG.transform_path_int32.argtypes = (
    POINTER(c_int32),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double
)
CPSIG.transform_path_int32.restype = c_int

CPSIG.transform_path_int64.argtypes = (
    POINTER(c_int64),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double
)
CPSIG.transform_path_int64.restype = c_int

######################################################
# batch_transform_path
######################################################

CPSIG.batch_transform_path_float.argtypes = (
    POINTER(c_float),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double,
    c_int
)
CPSIG.batch_transform_path_float.restype = c_int

CPSIG.batch_transform_path_double.argtypes = (
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double,
    c_int
)
CPSIG.batch_transform_path_double.restype = c_int

CPSIG.batch_transform_path_int32.argtypes = (
    POINTER(c_int32),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double,
    c_int
)
CPSIG.batch_transform_path_int32.restype = c_int

CPSIG.batch_transform_path_int64.argtypes = (
    POINTER(c_int64),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double,
    c_int
)
CPSIG.batch_transform_path_int64.restype = c_int

######################################################
# transform_path_backprop
######################################################

CPSIG.transform_path_backprop.argtypes = (
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double
)
CPSIG.transform_path_backprop.restype = c_int

######################################################
# batch_transform_path_backprop
######################################################

CPSIG.batch_transform_path_backprop.argtypes = (
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double,
    c_int
)
CPSIG.batch_transform_path_backprop.restype = c_int

if BUILT_WITH_CUDA:
    ######################################################
    # transform_path_cuda
    ######################################################

    CUSIG.transform_path_cuda_float.argtypes = (
        POINTER(c_float),
        POINTER(c_double),
        c_uint64,
        c_uint64,
        c_bool,
        c_bool,
        c_double
    )
    CUSIG.transform_path_cuda_float.restype = c_int

    CUSIG.transform_path_cuda_double.argtypes = (
        POINTER(c_double),
        POINTER(c_double),
        c_uint64,
        c_uint64,
        c_bool,
        c_bool,
        c_double
    )
    CUSIG.transform_path_cuda_double.restype = c_int

    CUSIG.transform_path_cuda_int32.argtypes = (
        POINTER(c_int32),
        POINTER(c_double),
        c_uint64,
        c_uint64,
        c_bool,
        c_bool,
        c_double
    )
    CUSIG.transform_path_cuda_int32.restype = c_int

    CUSIG.transform_path_cuda_int64.argtypes = (
        POINTER(c_int64),
        POINTER(c_double),
        c_uint64,
        c_uint64,
        c_bool,
        c_bool,
        c_double
    )
    CUSIG.transform_path_cuda_int64.restype = c_int

    ######################################################
    # batch_transform_path_cuda
    ######################################################

    CUSIG.batch_transform_path_cuda_float.argtypes = (
        POINTER(c_float),
        POINTER(c_double),
        c_uint64,
        c_uint64,
        c_uint64,
        c_bool,
        c_bool,
        c_double
    )
    CUSIG.batch_transform_path_cuda_float.restype = c_int

    CUSIG.batch_transform_path_cuda_double.argtypes = (
        POINTER(c_double),
        POINTER(c_double),
        c_uint64,
        c_uint64,
        c_uint64,
        c_bool,
        c_bool,
        c_double
    )
    CUSIG.batch_transform_path_cuda_double.restype = c_int

    CUSIG.batch_transform_path_cuda_int32.argtypes = (
        POINTER(c_int32),
        POINTER(c_double),
        c_uint64,
        c_uint64,
        c_uint64,
        c_bool,
        c_bool,
        c_double
    )
    CUSIG.batch_transform_path_cuda_int32.restype = c_int

    CUSIG.batch_transform_path_cuda_int64.argtypes = (
        POINTER(c_int64),
        POINTER(c_double),
        c_uint64,
        c_uint64,
        c_uint64,
        c_bool,
        c_bool,
        c_double
    )
    CUSIG.batch_transform_path_cuda_int64.restype = c_int

    ######################################################
    # transform_path_backprop_cuda
    ######################################################

    CUSIG.transform_path_backprop_cuda.argtypes = (
        POINTER(c_double),
        POINTER(c_double),
        c_uint64,
        c_uint64,
        c_bool,
        c_bool,
        c_double
    )
    CUSIG.transform_path_backprop_cuda.restype = c_int

    ######################################################
    # batch_transform_path_backprop_cuda
    ######################################################

    CUSIG.batch_transform_path_backprop_cuda.argtypes = (
        POINTER(c_double),
        POINTER(c_double),
        c_uint64,
        c_uint64,
        c_uint64,
        c_bool,
        c_bool,
        c_double
    )
    CUSIG.batch_transform_path_backprop_cuda.restype = c_int

######################################################
# sig_length
######################################################

CPSIG.sig_length.argtypes = (
    c_uint64,
    c_uint64
)
CPSIG.sig_length.restype = c_uint64

######################################################
# sig_combine
######################################################

CPSIG.sig_combine.argtypes = (
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64
)
CPSIG.sig_combine.restype = c_int

######################################################
# batch_sig_combine
######################################################

CPSIG.batch_sig_combine.argtypes = (
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_int
)
CPSIG.batch_sig_combine.restype = c_int

######################################################
# sig_combine_backprop
######################################################

CPSIG.sig_combine_backprop.argtypes = (
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64
)
CPSIG.sig_combine_backprop.restype = c_int

######################################################
# batch_sig_combine_backprop
######################################################

CPSIG.batch_sig_combine_backprop.argtypes = (
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_int
)
CPSIG.batch_sig_combine_backprop.restype = c_int

######################################################
# signature
######################################################

CPSIG.signature_int32.argtypes = (
    POINTER(c_int32),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double,
    c_bool
)
CPSIG.signature_int32.restype = c_int

CPSIG.signature_int64.argtypes = (
    POINTER(c_int64),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double,
    c_bool
)
CPSIG.signature_int64.restype = c_int

CPSIG.signature_float.argtypes = (
    POINTER(c_float),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double,
    c_bool
)
CPSIG.signature_float.restype = c_int

CPSIG.signature_double.argtypes = (
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double,
    c_bool
)
CPSIG.signature_double.restype = c_int

######################################################
# sig_backprop
######################################################

CPSIG.sig_backprop_float.argtypes = (
    POINTER(c_float),
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double
)
CPSIG.sig_backprop_float.restype = c_int

CPSIG.sig_backprop_double.argtypes = (
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double
)
CPSIG.sig_backprop_double.restype = c_int

CPSIG.sig_backprop_int32.argtypes = (
    POINTER(c_int32),
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double
)
CPSIG.sig_backprop_int32.restype = c_int

CPSIG.sig_backprop_int64.argtypes = (
    POINTER(c_int64),
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double
)
CPSIG.sig_backprop_int64.restype = c_int

######################################################
# batch_signature
######################################################

CPSIG.batch_signature_int32.argtypes = (
    POINTER(c_int32),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double,
    c_bool,
    c_int
)
CPSIG.batch_signature_int32.restype = c_int

CPSIG.batch_signature_int64.argtypes = (
    POINTER(c_int64),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double,
    c_bool,
    c_int
)
CPSIG.batch_signature_int64.restype = c_int

CPSIG.batch_signature_float.argtypes = (
    POINTER(c_float),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double,
    c_bool,
    c_int
)
CPSIG.batch_signature_float.restype = c_int

CPSIG.batch_signature_double.argtypes = (
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double,
    c_bool,
    c_int
)
CPSIG.batch_signature_double.restype = c_int

######################################################
# batch_sig_backprop
######################################################

CPSIG.batch_sig_backprop_float.argtypes = (
    POINTER(c_float),
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double,
    c_int
)
CPSIG.batch_sig_backprop_float.restype = c_int

CPSIG.batch_sig_backprop_double.argtypes = (
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double,
    c_int
)
CPSIG.batch_sig_backprop_double.restype = c_int

CPSIG.batch_sig_backprop_int32.argtypes = (
    POINTER(c_int32),
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double,
    c_int
)
CPSIG.batch_sig_backprop_int32.restype = c_int

CPSIG.batch_sig_backprop_int64.argtypes = (
    POINTER(c_int64),
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_uint64,
    c_bool,
    c_bool,
    c_double,
    c_int
)
CPSIG.batch_sig_backprop_int64.restype = c_int

######################################################
# batch_sig_kernel
######################################################

CPSIG.batch_sig_kernel.argtypes = (
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_uint64,
    c_uint64,
    c_uint64,
    c_int,
    c_bool
)
CPSIG.batch_sig_kernel.restype = c_int

if BUILT_WITH_CUDA:
    CUSIG.batch_sig_kernel_cuda.argtypes = (
        POINTER(c_double),
        POINTER(c_double),
        c_uint64,
        c_uint64,
        c_uint64,
        c_uint64,
        c_uint64,
        c_uint64,
        c_bool
    )
    CUSIG.batch_sig_kernel_cuda.restype = c_int

######################################################
# batch_sig_kernel_backprop
######################################################

CPSIG.batch_sig_kernel_backprop.argtypes = (
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    POINTER(c_double),
    c_uint64,
    c_uint64,
    c_uint64,
    c_uint64,
    c_uint64,
    c_uint64,
    c_int
)
CPSIG.batch_sig_kernel_backprop.restype = c_int

if BUILT_WITH_CUDA:
    CUSIG.batch_sig_kernel_backprop_cuda.argtypes = (
        POINTER(c_double),
        POINTER(c_double),
        POINTER(c_double),
        POINTER(c_double),
        c_uint64,
        c_uint64,
        c_uint64,
        c_uint64,
        c_uint64,
        c_uint64
    )
    CUSIG.batch_sig_kernel_backprop_cuda.restype = c_int
