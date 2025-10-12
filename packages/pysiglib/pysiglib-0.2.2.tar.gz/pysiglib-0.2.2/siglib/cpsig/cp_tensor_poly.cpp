/* Copyright 2025 Daniil Shmelev
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ========================================================================= */

#include "cppch.h"
#include "cpsig.h"
#include "cp_tensor_poly.h"
#include "multithreading.h"
#include "macros.h"

uint64_t power(uint64_t base, uint64_t exp) noexcept {
    uint64_t result = 1;
    while (exp > 0) {
        if (exp % 2 == 1) {
            const auto _res = result * base;
            if (_res < result)
                return 0; // overflow
            result = _res;
        }
        const auto _base = base * base;
        if (_base < base)
            return 0; // overflow
        base = _base;
        exp /= 2;
    }
    return result;
}

extern "C" CPSIG_API uint64_t sig_length(uint64_t dimension, uint64_t degree) noexcept {
    if (dimension == 0) {
        return 1;
    }
    else if (dimension == 1) {
        return degree + 1;
    }
    else {
        const auto pwr = power(dimension, degree + 1);
        if (pwr)
            return (pwr - 1) / (dimension - 1);
        else
            return 0; // overflow
    }
}


void sig_combine_(
	const double* sig1,
	const double* sig2,
	double* out, 
	uint64_t dimension, 
	uint64_t degree
)
{
	if (dimension == 0) { throw std::invalid_argument("sig_combine received dimension 0"); }

	auto level_index_uptr = std::make_unique<uint64_t[]>(degree + 2);
	uint64_t* level_index = level_index_uptr.get();

	level_index[0] = 0;
	for (uint64_t i = 1; i <= degree + 1; i++)
		level_index[i] = level_index[i - 1] * dimension + 1;

    std::memcpy(out, sig1, sizeof(double) * level_index[degree + 1]);

	sig_combine_inplace_(out, sig2, degree, level_index);
}

void batch_sig_combine_(
	const double* sig1,
	const double* sig2,
	double* out, 
	uint64_t batch_size,
	uint64_t dimension, 
	uint64_t degree, 
	int n_jobs = 1
)
{
	if (dimension == 0) { throw std::invalid_argument("sig_combine received dimension 0"); }

	const uint64_t siglength = ::sig_length(dimension, degree);
	const double* const sig1_end = sig1 + siglength * batch_size;

	std::function<void(const double*, const double*, double*)> sig_combine_func;

	sig_combine_func = [&](const double* sig1_ptr, const double* sig2_ptr, double* out_ptr) {
		sig_combine_(sig1_ptr, sig2_ptr, out_ptr, dimension, degree);
		};

	if (n_jobs != 1) {
		multi_threaded_batch_2(sig_combine_func, sig1, sig2, out, batch_size, siglength, siglength, siglength, n_jobs);
	}
	else {
		const double* sig1_ptr = sig1;
		const double* sig2_ptr = sig2;
		double* out_ptr = out;
		for (;
			sig1_ptr < sig1_end;
			sig1_ptr += siglength,
			sig2_ptr += siglength,
			out_ptr += siglength) {

			sig_combine_func(sig1_ptr, sig2_ptr, out_ptr);
		}
	}
	return;
}

void sig_combine_backprop_(
	const double* sig_combined_deriv,
	double* sig1_deriv, 
	double* sig2_deriv, 
	const double* sig1,
	const double* sig2,
	uint64_t dimension,
	uint64_t degree
)
{
	if (dimension == 0) { throw std::invalid_argument("sig_combine_backprop received dimension 0"); }

	auto level_index_uptr = std::make_unique<uint64_t[]>(degree + 2);
	uint64_t* level_index = level_index_uptr.get();

	level_index[0] = 0;
	for (uint64_t i = 1; i <= degree + 1; i++)
		level_index[i] = level_index[i - 1] * dimension + 1;

	std::memcpy(sig1_deriv, sig_combined_deriv, sizeof(double) * level_index[degree + 1]);

	uncombine_sig_deriv(sig1, sig2, sig1_deriv, sig2_deriv, dimension, degree, level_index);
	return;
}

void batch_sig_combine_backprop_(
	const double* sig_combined_deriv,
	double* sig1_deriv, 
	double* sig2_deriv, 
	const double* sig1,
	const double* sig2,
	uint64_t batch_size,
	uint64_t dimension, 
	uint64_t degree,
	int n_jobs = 1
)
{
	if (dimension == 0) { throw std::invalid_argument("sig_combine_backprop received dimension 0"); }

	auto level_index_uptr = std::make_unique<uint64_t[]>(degree + 2);
	uint64_t* level_index = level_index_uptr.get();

	level_index[0] = 0;
	for (uint64_t i = 1; i <= degree + 1; i++)
		level_index[i] = level_index[i - 1] * dimension + 1;

	const uint64_t siglength = level_index[degree + 1];

	std::memcpy(sig1_deriv, sig_combined_deriv, sizeof(double) * siglength * batch_size);

	std::function<void(const double*, double*, double*, const double*, const double*)> sig_combine_backprop_func;

	sig_combine_backprop_func = [&](const double* sig_combined_deriv_ptr, double* sig1_deriv_ptr, double* sig2_deriv_ptr, const double* sig1_ptr, const double* sig2_ptr) {
		sig_combine_backprop_(sig_combined_deriv_ptr, sig1_deriv_ptr, sig2_deriv_ptr, sig1_ptr, sig2_ptr, dimension, degree);
		};

	if (n_jobs != 1) {
		multi_threaded_batch_4(sig_combine_backprop_func, sig_combined_deriv, sig1_deriv, sig2_deriv, sig1, sig2, batch_size, siglength, siglength, siglength, siglength, siglength, n_jobs);
	}
	else {
		const double* sig_combined_derivs_ptr = sig_combined_deriv;
		double* sig1_deriv_ptr = sig1_deriv;
		double* sig2_deriv_ptr = sig2_deriv;
		const double* sig1_ptr = sig1;
		const double* sig2_ptr = sig2;
		const double* sig1_end = sig1 + batch_size * siglength;
		for (;
			sig1_ptr < sig1_end;
			sig_combined_derivs_ptr += siglength,
			sig1_deriv_ptr += siglength,
			sig2_deriv_ptr += siglength,
			sig1_ptr += siglength,
			sig2_ptr += siglength
			) {

			sig_combine_backprop_func(sig_combined_derivs_ptr, sig1_deriv_ptr, sig2_deriv_ptr, sig1_ptr, sig2_ptr);
		}
	}
	return;
}

extern "C" {

	CPSIG_API int sig_combine(const double* sig1, const double* sig2, double* out, uint64_t dimension, uint64_t degree) noexcept {
		SAFE_CALL(sig_combine_(sig1, sig2, out, dimension, degree));
	}

	CPSIG_API int batch_sig_combine(const double* sig1, const double* sig2, double* out, uint64_t batch_size, uint64_t dimension, uint64_t degree, int n_jobs) noexcept {
		SAFE_CALL(batch_sig_combine_(sig1, sig2, out, batch_size, dimension, degree, n_jobs));
	}

	CPSIG_API int sig_combine_backprop(const double* sig_combined_deriv, double* sig1_deriv, double* sig2_deriv, const double* sig1, const double* sig2, uint64_t dimension, uint64_t degree) noexcept {
		SAFE_CALL(sig_combine_backprop_(sig_combined_deriv, sig1_deriv, sig2_deriv, sig1, sig2, dimension, degree));
	}

	CPSIG_API int batch_sig_combine_backprop(const double* sig_combined_deriv, double* sig1_deriv, double* sig2_deriv, const double* sig1, const double* sig2, uint64_t batch_size, uint64_t dimension, uint64_t degree, int n_jobs) noexcept {
		SAFE_CALL(batch_sig_combine_backprop_(sig_combined_deriv, sig1_deriv, sig2_deriv, sig1, sig2, batch_size, dimension, degree, n_jobs));
	}
}
