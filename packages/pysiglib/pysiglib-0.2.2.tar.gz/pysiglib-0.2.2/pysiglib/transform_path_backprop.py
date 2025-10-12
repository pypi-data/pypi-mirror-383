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

from typing import Union

import numpy as np
import torch

from .data_handlers import PathOutputHandler
from .load_siglib import CPSIG, CUSIG, BUILT_WITH_CUDA
from .param_checks import check_type, check_cpu
from .error_codes import err_msg
from .dtypes import CPSIG_TRANSFORM_PATH, CPSIG_BATCH_TRANSFORM_PATH

from .data_handlers import PathInputHandler

def transform_path_backprop_(data, result, length, dimension, time_aug, lead_lag, end_time):
    err_code = CPSIG.transform_path_backprop(
        data.data_ptr,
        result.data_ptr,
        dimension,
        length,
        time_aug,
        lead_lag,
        end_time
    )

    if err_code:
        raise Exception("Error in pysiglib.transform_path_backprop: " + err_msg(err_code))
    return result.data

def batch_transform_path_backprop_(data, result, length, dimension, time_aug, lead_lag, end_time, n_jobs):
    err_code = CPSIG.batch_transform_path_backprop(
        data.data_ptr,
        result.data_ptr,
        data.batch_size,
        dimension,
        length,
        time_aug,
        lead_lag,
        end_time,
        n_jobs
    )

    if err_code:
        raise Exception("Error in pysiglib.transform_path_backprop: " + err_msg(err_code))
    return result.data

def transform_path_backprop_cuda_(data, result, length, dimension, time_aug, lead_lag, end_time):
    err_code = CUSIG.transform_path_backprop_cuda(
        data.data_ptr,
        result.data_ptr,
        dimension,
        length,
        time_aug,
        lead_lag,
        end_time
    )

    if err_code:
        raise Exception("Error in pysiglib.transform_path_backprop: " + err_msg(err_code))
    return result.data

def batch_transform_path_backprop_cuda_(data, result, length, dimension, time_aug, lead_lag, end_time):
    err_code = CUSIG.batch_transform_path_backprop_cuda(
        data.data_ptr,
        result.data_ptr,
        data.batch_size,
        dimension,
        length,
        time_aug,
        lead_lag,
        end_time
    )

    if err_code:
        raise Exception("Error in pysiglib.transform_path_backprop: " + err_msg(err_code))
    return result.data

def transform_path_backprop(
    derivs : Union[np.ndarray, torch.tensor],
    time_aug : bool = False,
    lead_lag : bool = False,
    end_time : float = 1.,
    n_jobs : int = 1
) -> Union[np.ndarray, torch.tensor]:
    """
    This function is required to backpropagate through ``pysiglib.transform_path``.
    Given the derivatives of a scalar function :math:`F` with respect to the
    result of ``pysiglib.transform_path``,
    :math:`\\{\\partial F / \\partial \\tilde{x}_{t_i}\\}_{i=0}^\\tilde{L}`,
    returns the derivatives of :math:`F` with respect to the original path,
    :math:`\\{\\partial F / x_{t_i}\\}_{i=0}^L`.

    :param derivs: The derivatives with respect to the result of ``pysiglib.transform_path``,
        :math:`\\{\\partial F / \\partial \\tilde{x}_{t_i}\\}_{i=0}^\\tilde{L}`.
    :type derivs: numpy.ndarray | torch.tensor
    :param time_aug: If ``True``, assumes the derivatives are with respect to a time
        augmented path.
    :type time_aug: bool
    :param lead_lag: If ``True``, assumes the derivatives are with respect to a lead-lag
        transformed path.
    :type lead_lag: bool
    :param end_time: End time for time-augmentation, :math:`t_L`.
    :type end_time: float
    :param n_jobs: Number of threads to run in parallel. If n_jobs = 1, the computation is run serially.
        If set to -1, all available threads are used. For n_jobs below -1, (max_threads + 1 + n_jobs)
        threads are used. For example if n_jobs = -2, all threads but one are used.
    :type n_jobs: int
    :return: Derivatives with respect to the original path,
        :math:`\\{\\partial F / x_{t_i}\\}_{i=0}^L`.
    :rtype: numpy.ndarray | torch.tensor

    .. note::

        Ideally, any array passed to ``pysiglib.transform_path_backprop`` should be both contiguous and own its data.
        If this is not the case, ``pysiglib.transform_path_backprop`` will internally create a contiguous copy, which may be
        inefficient.

    """
    check_type(time_aug, "time_aug", bool)
    check_type(lead_lag, "lead_lag", bool)

    if (not time_aug) and (not lead_lag):
        return derivs

    data = PathInputHandler(derivs, False, False, end_time, "path")
    length = (data.length + 1) // 2 if lead_lag else data.length
    dimension = data.dimension - 1 if time_aug else data.dimension
    if lead_lag:
        dimension = dimension // 2
    result = PathOutputHandler(length, dimension, data)
    if data.is_batch:
        check_type(n_jobs, "n_jobs", int)
        if n_jobs == 0:
            raise ValueError("n_jobs cannot be 0")

        if data.device == "cpu":
            return batch_transform_path_backprop_(data, result, length, dimension, time_aug, lead_lag, end_time, n_jobs)
        else:
            if not BUILT_WITH_CUDA:
                raise RuntimeError("pySigLib was built without CUDA - data must be moved to CPU.")
            return batch_transform_path_backprop_cuda_(data, result, length, dimension, time_aug, lead_lag, end_time)

    if data.device == "cpu":
        return transform_path_backprop_(data, result, length, dimension, time_aug, lead_lag, end_time)
    else:
        if not BUILT_WITH_CUDA:
            raise RuntimeError("pySigLib was built without CUDA - data must be moved to CPU.")
        return transform_path_backprop_cuda_(data, result, length, dimension, time_aug, lead_lag, end_time)