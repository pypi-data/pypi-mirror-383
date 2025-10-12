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

import pytest
import numpy as np
import torch
import iisignature

import pysiglib

np.random.seed(42)
torch.manual_seed(42)
EPSILON = 1e-5

def check_close(a, b):
    a_ = np.array(a)
    b_ = np.array(b)
    assert not np.max(np.abs(a_ - b_)) > EPSILON

@pytest.mark.parametrize("deg", range(1, 6))
def test_sig_combine_backprop_random(deg):
    dimension = 5
    sig_len = pysiglib.sig_length(dimension, deg)

    sig1 = np.random.uniform(size = sig_len)
    sig2 = np.random.uniform(size = sig_len)
    derivs = np.random.uniform(size = sig_len)

    sig1_deriv, sig2_deriv = pysiglib.sig_combine_backprop(derivs, sig1, sig2, dimension, deg)
    iisig1_deriv, iisig2_deriv = iisignature.sigcombinebackprop(derivs[1:], sig1[1:], sig2[1:], dimension, deg)
    check_close(sig1_deriv[1:], iisig1_deriv)
    check_close(sig2_deriv[1:], iisig2_deriv)

@pytest.mark.skipif(not (pysiglib.BUILT_WITH_CUDA and torch.cuda.is_available()), reason="CUDA not available or disabled")
@pytest.mark.parametrize("deg", range(1, 6))
def test_sig_combine_backprop_random_cuda(deg):
    dimension = 5
    sig_len = pysiglib.sig_length(dimension, deg)

    sig1 = torch.rand(size = (sig_len,), device = "cuda", dtype = torch.float64)
    sig2 = torch.rand(size = (sig_len,), device = "cuda", dtype = torch.float64)
    derivs = torch.rand(size = (sig_len,), device = "cuda", dtype = torch.float64)

    sig1_deriv, sig2_deriv = pysiglib.sig_combine_backprop(derivs, sig1, sig2, dimension, deg)
    iisig1_deriv, iisig2_deriv = iisignature.sigcombinebackprop(derivs[1:].cpu(), sig1[1:].cpu(), sig2[1:].cpu(), dimension, deg)
    check_close(sig1_deriv[1:].cpu(), iisig1_deriv)
    check_close(sig2_deriv[1:].cpu(), iisig2_deriv)

@pytest.mark.parametrize("deg", range(1, 6))
def test_batch_sig_backprop_random(deg):
    dimension, batch_size = 5, 10
    sig_len = pysiglib.sig_length(dimension, deg)

    sig1 = np.random.uniform(size=(batch_size, sig_len))
    sig2 = np.random.uniform(size=(batch_size, sig_len))
    derivs = np.random.uniform(size=(batch_size, sig_len))

    sig1_deriv, sig2_deriv = pysiglib.sig_combine_backprop(derivs, sig1, sig2, dimension, deg, 1)
    iisig1_deriv, iisig2_deriv = iisignature.sigcombinebackprop(derivs[:, 1:], sig1[:, 1:], sig2[:, 1:], dimension, deg)
    check_close(sig1_deriv[:, 1:], iisig1_deriv)
    check_close(sig2_deriv[:, 1:], iisig2_deriv)

    sig1_deriv, sig2_deriv = pysiglib.sig_combine_backprop(derivs, sig1, sig2, dimension, deg, -1)
    check_close(sig1_deriv[:, 1:], iisig1_deriv)
    check_close(sig2_deriv[:, 1:], iisig2_deriv)
