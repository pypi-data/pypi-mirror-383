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

#pragma once
#include "cupch.h"

__global__ void transform_path_backprop_internal_(
	const double* derivs,
	double* data_out
);

void transform_path_backprop_(
	const double* derivs,
	double* data_out,
	uint64_t batch_size_,
	uint64_t dimension_,
	uint64_t length_,
	bool time_aug_,
	bool lead_lag_,
	double end_time_
);

