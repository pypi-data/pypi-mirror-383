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
#include "cppch.h"

#if defined(CPSIG_EXPORTS)
	#if defined (_MSC_VER)
		#define CPSIG_API __declspec(dllexport)
	#elif defined (__GNUC__)
		#define CPSIG_API __attribute__((visibility("default")))
	#else
		#define CPSIG_API
	#endif
#else
	#if defined (_MSC_VER)
		#define CPSIG_API __declspec(dllimport)
	#elif defined (__GNUC__)
		#define CPSIG_API 
	#else
		#define CPSIG_API 
	#endif
#endif


extern "C" {

	/** @defgroup transform_path_functions Transform path functions
	* @{
	*/

	/**
	* @brief Applies time-augmentation and/or the lead-lag transformation to a path of type float.
	*
	*
	* @param data_in Pointer to input path data (row-major), size = `length * dimension`.
	* @param data_out Pointer to output buffer (row-major, preallocated), size = `transformed_length * transformed_dimension`, where
	*					`transformed_length = lead_lag ? length_ * 2 - 1` and `transformed_dimension = (lead_lag ? 2 : 1) * dimension + (time_aug ? 1 : 0)`.
	* @param dimension Dimension of the path.
	* @param length Length of the path.
	* @param time_aug Whether to add time augmentation (default = false).
	* @param lead_lag Whether to apply the lead-lag transform (default = false).
	* @param end_time End time for time augmentation (default = 1.0).
	* @return Status code (0 = success).
	*/
	CPSIG_API int transform_path_float(const float* data_in, double* data_out, uint64_t dimension, uint64_t length, bool time_aug = false, bool lead_lag = false, double end_time = 1.) noexcept;
	/** @brief */
	CPSIG_API int transform_path_double(const double* data_in, double* data_out, uint64_t dimension, uint64_t length, bool time_aug = false, bool lead_lag = false, double end_time = 1.) noexcept;
	/** @brief */
	CPSIG_API int transform_path_int32(const int32_t* data_in, double* data_out, uint64_t dimension, uint64_t length, bool time_aug = false, bool lead_lag = false, double end_time = 1.) noexcept;
	/** @brief */
	CPSIG_API int transform_path_int64(const int64_t* data_in, double* data_out, uint64_t dimension, uint64_t length, bool time_aug = false, bool lead_lag = false, double end_time = 1.) noexcept;
	/** @} */

	/** @defgroup batch_transform_path_functions Batch transform path functions
	* @{
	*/

	/**
	* @brief Applies time-augmentation and/or the lead-lag transformation to a batch of paths of type float.
	*
	*
	* @param data_in Pointer to input path data (row-major), size = `batch_size * length * dimension`.
	* @param data_out Pointer to output buffer (row-major, preallocated), size = `batch_size * transformed_length * transformed_dimension`, where
	*					`transformed_length = lead_lag ? length_ * 2 - 1` and `transformed_dimension = (lead_lag ? 2 : 1) * dimension + (time_aug ? 1 : 0)`.
	* @param batch_size Batch size of the paths.
	* @param dimension Dimension of the paths.
	* @param length Length of the paths.
	* @param time_aug Whether to add time augmentation (default = false).
	* @param lead_lag Whether to apply the lead-lag transform (default = false).
	* @param end_time End time for time augmentation (default = 1.0).
	* @param n_jobs Number of threads to run in parallel. If n_jobs = 1, the computation is run serially. If set to -1, all 
	*				available threads are used. For n_jobs below -1, (max_threads + 1 + n_jobs) threads are used. For example 
	*				if n_jobs = -2, all threads but one are used (default = 1).
	* @return Status code (0 = success).
	*/
	CPSIG_API int batch_transform_path_float(const float* data_in, double* data_out, uint64_t batch_size, uint64_t dimension, uint64_t length, bool time_aug = false, bool lead_lag = false, double end_time = 1., int n_jobs = 1) noexcept;
	/** @brief */
	CPSIG_API int batch_transform_path_double(const double* data_in, double* data_out, uint64_t batch_size, uint64_t dimension, uint64_t length, bool time_aug = false, bool lead_lag = false, double end_time = 1., int n_jobs = 1) noexcept;
	/** @brief */
	CPSIG_API int batch_transform_path_int32(const int32_t* data_in, double* data_out, uint64_t batch_size, uint64_t dimension, uint64_t length, bool time_aug = false, bool lead_lag = false, double end_time = 1., int n_jobs = 1) noexcept;
	/** @brief */
	CPSIG_API int batch_transform_path_int64(const int64_t* data_in, double* data_out, uint64_t batch_size, uint64_t dimension, uint64_t length, bool time_aug = false, bool lead_lag = false, double end_time = 1., int n_jobs = 1) noexcept;
	/** @} */

	/**
	* @brief Backpropagation through the transform_path function.
	*
	*
	* @param derivs Pointer to derivatives with respect to transformed path (row-major), size = `transformed_length * transformed_dimension`, where
	*					`transformed_length = lead_lag ? length_ * 2 - 1` and `transformed_dimension = (lead_lag ? 2 : 1) * dimension + (time_aug ? 1 : 0)`.
	* @param data_out Pointer to output buffer (row-major, preallocated), size = `length * dimension`.
	* @param dimension Dimension of the original (pre-transformation) path.
	* @param length Length of the original (pre-transformation) path.
	* @param time_aug Whether time augmentation was applied (default = false).
	* @param lead_lag Whether the lead-lag transform was applied (default = false).
	* @param end_time End time for time augmentation (default = 1.0).
	* @return Status code (0 = success).
	*/
	CPSIG_API int transform_path_backprop(const double* derivs, double* data_out, uint64_t dimension, uint64_t length, bool time_aug = false, bool lead_lag = false, double end_time = 1.) noexcept;
	
	/**
	* @brief Backpropagation through the batch_transform_path function.
	*
	*
	* @param derivs Pointer to derivatives with respect to transformed path (row-major), size = `batch_size * transformed_length * transformed_dimension`, where
	*					`transformed_length = lead_lag ? length_ * 2 - 1` and `transformed_dimension = (lead_lag ? 2 : 1) * dimension + (time_aug ? 1 : 0)`.
	* @param data_out Pointer to output buffer (row-major, preallocated), size = `batch_size * length * dimension`.
	* @param batch_size Batch size of the paths.
	* @param dimension Dimension of the original (pre-transformation) paths.
	* @param length Length of the original (pre-transformation) paths.
	* @param time_aug Whether time augmentation was applied (default = false).
	* @param lead_lag Whether the lead-lag transform was applied (default = false).
	* @param end_time End time for time augmentation (default = 1.0).
	* @param n_jobs Number of threads to run in parallel. If n_jobs = 1, the computation is run serially. If set to -1, all 
	*				available threads are used. For n_jobs below -1, (max_threads + 1 + n_jobs) threads are used. For example 
	*				if n_jobs = -2, all threads but one are used (default = 1).
	* @return Status code (0 = success).
	*/
	CPSIG_API int batch_transform_path_backprop(const double* derivs, double* data_out, uint64_t batch_size, uint64_t dimension, uint64_t length, bool time_aug = false, bool lead_lag = false, double end_time = 1., int n_jobs = 1) noexcept;

	/**
	* @brief Returns the length of a truncated signature.
	*
	*
	* @param dimension Dimension of the underlying path.
	* @param degree Truncation degree of the signature.
	* @return Length of a truncated signature. A returned value of 0 indicates integer overflow.
	*/
	CPSIG_API uint64_t sig_length(uint64_t dimension, uint64_t degree) noexcept;

	/**
	* @brief Combines two truncated signatures of the same degree and dimension into one signature.
	*
	*
	* @param sig1 Pointer to the first truncated signature, size = `sig_length(dimension, degree)`.
	* @param sig2 Pointer to the second truncated signature, size = `sig_length(dimension, degree)`. Must have the same degree and dimension as the first.
	* @param out Pointer to the output buffer (preallocated), size = `sig_length(dimension, degree)`.
	* @param dimension Dimension of the underlying paths.
	* @param degree Truncation degree of the signatures.
	* @return Status code (0 = success).
	*/
	CPSIG_API int sig_combine(const double* sig1, const double* sig2, double* out, uint64_t dimension, uint64_t degree) noexcept;

	/**
	* @brief Combines a batch of pairs of truncated signatures of the same degree and dimension.
	*
	*
	* @param sig1 Pointer to the batch of first truncated signatures (row-major), size = `batch_size * sig_length(dimension, degree)`.
	* @param sig2 Pointer to the batch of second truncated signatures (row-major), size = `batch_size * sig_length(dimension, degree)`.
	*					Must have the same batch size, degree and dimension as the first.
	* @param out Pointer to the output buffer (row-major, preallocated), size = `batch_size * sig_length(dimension, degree)`.
	* @param batch_size Batch size of sig1 and sig2.
	* @param dimension Dimension of the underlying paths.
	* @param degree Truncation degree of the signatures.
	* @param n_jobs Number of threads to run in parallel. If n_jobs = 1, the computation is run serially. If set to -1, all 
	*				available threads are used. For n_jobs below -1, (max_threads + 1 + n_jobs) threads are used. For example 
	*				if n_jobs = -2, all threads but one are used (default = 1).
	* @return Status code (0 = success).
	*/
	CPSIG_API int batch_sig_combine(const double* sig1, const double* sig2, double* out, uint64_t batch_size, uint64_t dimension, uint64_t degree, int n_jobs = 1) noexcept;

	/**
	* @brief Backpropagation through the sig_combine function.
	*
	*
	* @param sig_combined_derivs Pointer to the derivatives with respect to the combined signature, size = `sig_length(dimension, degree)`.
	* @param sig1_deriv Pointer to the output buffer for the derivatives with respect to sig1 (preallocated), size = `sig_length(dimension, degree)`.
	* @param sig2_deriv Pointer to the output buffer for the derivatives with respect to sig2 (preallocated), size = `sig_length(dimension, degree)`.
	* @param sig1 Pointer to the first truncated signature (precomputed), size = `sig_length(dimension, degree)`.
	* @param sig2 Pointer to the second truncated signature (precomputed), size = `sig_length(dimension, degree)`. Must have the same degree and dimension as the first.
	* @param dimension Dimension of the underlying path.
	* @param degree Truncation degree of the signature.
	* @return Status code (0 = success).
	*/
	CPSIG_API int sig_combine_backprop(const double* sig_combined_derivs, double* sig1_deriv, double* sig2_deriv, const double* sig1, const double* sig2, uint64_t dimension, uint64_t degree) noexcept;
	
	/**
	* @brief Backpropagation through the batch_sig_combine function.
	*
	*
	* @param sig_combined_derivs Pointer to the derivatives with respect to the combined signatures (row-major), size = `batch_size * sig_length(dimension, degree)`.
	* @param sig1_deriv Pointer to the output buffer for the derivatives with respect to sig1 (row-major, preallocated), size = `batch_size * sig_length(dimension, degree)`.
	* @param sig2_deriv Pointer to the output buffer for the derivatives with respect to sig2 (row-major, preallocated), size = `batch_size * sig_length(dimension, degree)`.
	* @param sig1 Pointer to the batch of first truncated signatures (row-major, precomputed), size = `batch_size * sig_length(dimension, degree)`.
	* @param sig2 Pointer to the batch of second truncated signatures (row-major, precomputed), size = `batch_size * sig_length(dimension, degree)`. Must have the same batch size, degree and dimension as sig1.
	* @param batch_size Batch size of the signatures.
	* @param dimension Dimension of the underlying paths.
	* @param degree Truncation degree of the signatures.
	* @param n_jobs Number of threads to run in parallel. If n_jobs = 1, the computation is run serially. If set to -1, all 
	*				available threads are used. For n_jobs below -1, (max_threads + 1 + n_jobs) threads are used. For example 
	*				if n_jobs = -2, all threads but one are used (default = 1).
	* @return Status code (0 = success).
	*/
	CPSIG_API int batch_sig_combine_backprop(const double* sig_combined_derivs, double* sig1_deriv, double* sig2_deriv, const double* sig1, const double* sig2, uint64_t batch_size, uint64_t dimension, uint64_t degree, int n_jobs = 1) noexcept;

	/** @defgroup signature_functions Signature functions
	* @{
	*/

	/**
	* @brief Computes the signature of a path of type float.
	* @param path Pointer to path data (row-major), size = `length * dimension`.
	* @param out Pointer to output buffer (preallocated), size = `sig_length(dimension, degree)`.
	* @param dimension Dimension of the path.
	* @param length Length of the path.
	* @param degree Truncation degree of the signature.
	* @param time_aug Whether to add time augmentation (default = false).
	* @param lead_lag Whether to apply lead-lag transform (default = false).
	* @param end_time End time for time augmentation (default = 1.0).
	* @param horner Whether to use Horner's scheme (default = true).
	* @return Status code (0 = success).
	*/
	CPSIG_API int signature_float(const float* path, double* out, uint64_t dimension, uint64_t length, uint64_t degree, bool time_aug = false, bool lead_lag = false, double end_time = 1., bool horner = true) noexcept; //bool time_aug = false, bool lead_lag = false, bool horner = true);
	/** @brief */
	CPSIG_API int signature_double(const double* path, double* out, uint64_t dimension, uint64_t length, uint64_t degree, bool time_aug = false, bool lead_lag = false, double end_time = 1., bool horner = true) noexcept;
	/** @brief */
	CPSIG_API int signature_int32(const int32_t* path, double* out, uint64_t dimension, uint64_t length, uint64_t degree, bool time_aug = false, bool lead_lag = false, double end_time = 1., bool horner = true) noexcept;
	/** @brief */
	CPSIG_API int signature_int64(const int64_t* path, double* out, uint64_t dimension, uint64_t length, uint64_t degree, bool time_aug = false, bool lead_lag = false, double end_time = 1., bool horner = true) noexcept;
	/** @} */


	/** @defgroup batch_signature_functions Batch signature functions
	* @{
	*/

	/**
	* @brief Computes the signature of a path of type float.
	* @param path Pointer to path batch data (row-major), size = `batch_size * length * dimension`.
	* @param out Pointer to output buffer (row-major, preallocated), size = `batch_size * sig_length(dimension, degree)`.
	* @param batch_size Batch size of the paths.
	* @param dimension Dimension of the path.
	* @param length Length of the path.
	* @param degree Truncation degree of the signature.
	* @param time_aug Whether to add time augmentation (default = false).
	* @param lead_lag Whether to apply lead-lag transform (default = false).
	* @param end_time End time for time augmentation (default = 1.0).
	* @param horner Whether to use Horner's scheme (default = true).
	* @param n_jobs Number of threads to run in parallel. If n_jobs = 1, the computation is run serially. If set to -1, all 
	*				available threads are used. For n_jobs below -1, (max_threads + 1 + n_jobs) threads are used. For example 
	*				if n_jobs = -2, all threads but one are used (default = 1).
	* @return Status code (0 = success).
	*/
	CPSIG_API int batch_signature_float(const float* path, double* out, uint64_t batch_size, uint64_t dimension, uint64_t length, uint64_t degree, bool time_aug = false, bool lead_lag = false, double end_time = 1., bool horner = true, int n_jobs = 1) noexcept;
	/** @brief */
	CPSIG_API int batch_signature_double(const double* path, double* out, uint64_t batch_size, uint64_t dimension, uint64_t length, uint64_t degree, bool time_aug = false, bool lead_lag = false, double end_time = 1., bool horner = true, int n_jobs = 1) noexcept;
	/** @brief */
	CPSIG_API int batch_signature_int32(const int32_t* path, double* out, uint64_t batch_size, uint64_t dimension, uint64_t length, uint64_t degree, bool time_aug = false, bool lead_lag = false, double end_time = 1., bool horner = true, int n_jobs = 1) noexcept;
	/** @brief */
	CPSIG_API int batch_signature_int64(const int64_t* path, double* out, uint64_t batch_size, uint64_t dimension, uint64_t length, uint64_t degree, bool time_aug = false, bool lead_lag = false, double end_time = 1., bool horner = true, int n_jobs = 1) noexcept;
	/** @} */


	/** @defgroup sig_backprop_functions Signature backprop functions
	* @{
	*/

	/**
	* @brief Backpropagation through the signature_float function.
	* 
	* @param path Pointer to path data (row-major), size = `length * dimension`.
	* @param out Pointer to output buffer (preallocated), size = `sig_length(dimension, degree)`.
	* @param sig_derivs Pointer to derivatives with respect to the signature, size = `sig_length(dimension, degree)`.
	* @param sig Pointer to signature of the path (precomputed), size = `sig_length(dimension, degree)`.
	* @param dimension Dimension of the path.
	* @param length Length of the path.
	* @param degree Truncation degree of the signature.
	* @param time_aug Whether time augmentation was applied (default = false).
	* @param lead_lag Whether the lead-lag transform was applied (default = false).
	* @param end_time End time for time augmentation (default = 1.0).
	* @return Status code (0 = success).
	*/
	CPSIG_API int sig_backprop_float(const float* path, double* out, const double* sig_derivs, const double* sig, uint64_t dimension, uint64_t length, uint64_t degree, bool time_aug = false, bool lead_lag = false, double end_time = 1.) noexcept;
	/** @brief */
	CPSIG_API int sig_backprop_double(const double* path, double* out, const double* sig_derivs, const double* sig, uint64_t dimension, uint64_t length, uint64_t degree, bool time_aug = false, bool lead_lag = false, double end_time = 1.) noexcept;
	/** @brief */
	CPSIG_API int sig_backprop_int32(const int32_t* path, double* out, const double* sig_derivs, const double* sig, uint64_t dimension, uint64_t length, uint64_t degree, bool time_aug = false, bool lead_lag = false, double end_time = 1.) noexcept;
	/** @brief */
	CPSIG_API int sig_backprop_int64(const int64_t* path, double* out, const double* sig_derivs, const double* sig, uint64_t dimension, uint64_t length, uint64_t degree, bool time_aug = false, bool lead_lag = false, double end_time = 1.) noexcept;
	/** @} */


	/** @defgroup batch_sig_backprop_functions Signature backprop functions
	* @{
	*/

	/**
	* @brief Backpropagation through the batch_signature_float function.
	*
	* @param path Pointer to path batch data (row-major), size = `batch_size * length * dimension`.
	* @param out Pointer to output buffer (row-major, preallocated), size = `batch_size * sig_length(dimension, degree)`.
	* @param sig_derivs Pointer to derivatives with respect to the signatures (row-major), size = `batch_size * sig_length(dimension, degree)`.
	* @param sig Pointer to signatures of the paths (row-major, precomputed), size = `batch_size * sig_length(dimension, degree)`.
	* @param batch_size Batch size of the paths.
	* @param dimension Dimension of the path.
	* @param length Length of the path.
	* @param degree Truncation degree of the signature.
	* @param time_aug Whether time augmentation was applied (default = false).
	* @param lead_lag Whether the lead-lag transform was applied (default = false).
	* @param end_time End time for time augmentation (default = 1.0).
	* @param n_jobs Number of threads to run in parallel. If n_jobs = 1, the computation is run serially. If set to -1, all 
	*				available threads are used. For n_jobs below -1, (max_threads + 1 + n_jobs) threads are used. For example 
	*				if n_jobs = -2, all threads but one are used (default = 1).
	* @return Status code (0 = success).
	*/
	CPSIG_API int batch_sig_backprop_float(const float* path, double* out, const double* sig_derivs, const double* sig, uint64_t batch_size, uint64_t dimension, uint64_t length, uint64_t degree, bool time_aug = false, bool lead_lag = false, double end_time = 1., int n_jobs = 1) noexcept;
	/** @brief */
	CPSIG_API int batch_sig_backprop_double(const double* path, double* out, const double* sig_derivs, const double* sig, uint64_t batch_size, uint64_t dimension, uint64_t length, uint64_t degree, bool time_aug = false, bool lead_lag = false, double end_time = 1., int n_jobs = 1) noexcept;
	/** @brief */
	CPSIG_API int batch_sig_backprop_int32(const int32_t* path, double* out, const double* sig_derivs, const double* sig, uint64_t batch_size, uint64_t dimension, uint64_t length, uint64_t degree, bool time_aug = false, bool lead_lag = false, double end_time = 1., int n_jobs = 1) noexcept;
	/** @brief */
	CPSIG_API int batch_sig_backprop_int64(const int64_t* path, double* out, const double* sig_derivs, const double* sig, uint64_t batch_size, uint64_t dimension, uint64_t length, uint64_t degree, bool time_aug = false, bool lead_lag = false, double end_time = 1., int n_jobs = 1) noexcept;
	/** @} */


	/**
	* @brief Computes the signature kernel of two paths from their gram matrix.
	*
	* @param gram Pointer to gram matrix data (row-major), size = `(length1 - 1) * (length2 - 1)`.
	* @param out Pointer to output buffer (row-major, preallocated), size = `return_grid ? (((length1 - 1) << dyadic_order_1) + 1) * (((length2 - 1) << dyadic_order_2) + 1) : 1`.
	* @param dimension Dimension of the path.
	* @param length1 Length of the first path.
	* @param length2 Length of the second path.
	* @param dyadic_order_1 Dyadic refinement for the first path.
	* @param dyadic_order_2 Dyadic refinement for the second path.
	* @param return_grid Whether to return the entire PDE grid (default = false).
	* @return Status code (0 = success).
	*/
	CPSIG_API int sig_kernel(const double* gram, double* out, uint64_t dimension, uint64_t length1, uint64_t length2, uint64_t dyadic_order_1, uint64_t dyadic_order_2, bool return_grid = false) noexcept;
	
	/**
	* @brief Computes signature kernels of a batch of paths from their gram matrices.
	*
	* @param gram Pointer to batch gram matrix data (row-major), size = `batch_size * (length1 - 1) * (length2 - 1)`.
	* @param out Pointer to output buffer (row-major, preallocated), size = `batch_size * (return_grid ? (((length1 - 1) << dyadic_order_1) + 1) * (((length2 - 1) << dyadic_order_2) + 1) : 1)`.
	* @param batch_size Batch size of the paths.
	* @param dimension Dimension of the path.
	* @param length1 Length of the first path.
	* @param length2 Length of the second path.
	* @param dyadic_order_1 Dyadic refinement for the first path.
	* @param dyadic_order_2 Dyadic refinement for the second path.
	* @param n_jobs Number of threads to run in parallel. If n_jobs = 1, the computation is run serially. If set to -1, all 
	*				available threads are used. For n_jobs below -1, (max_threads + 1 + n_jobs) threads are used. For example 
	*				if n_jobs = -2, all threads but one are used (default = 1).
	* @param return_grid Whether to return the entire PDE grid (default = false).
	* @return Status code (0 = success).
	*/
	CPSIG_API int batch_sig_kernel(const double* gram, double* out, uint64_t batch_size, uint64_t dimension, uint64_t length1, uint64_t length2, uint64_t dyadic_order_1, uint64_t dyadic_order_2, int n_jobs = 1, bool return_grid = false) noexcept;

	/**
	* @brief Backpropagation through sig_kernel.
	*
	* @param gram Pointer to gram matrix data (row-major), size = `(length1 - 1) * (length2 - 1)`.
	* @param out Pointer to output buffer (row-major, preallocated), size = `(length1 - 1) * (length2 - 1)`.
	* @param deriv Derivative with respect to the signature kernel.
	* @param k_grid Pointer to signature kernel PDE grid (row-major, precomputed), size = `(((length1 - 1) << dyadic_order_1) + 1) * (((length2 - 1) << dyadic_order_2) + 1)`.
	* @param dimension Dimension of the path.
	* @param length1 Length of the first path.
	* @param length2 Length of the second path.
	* @param dyadic_order_1 Dyadic refinement for the first path.
	* @param dyadic_order_2 Dyadic refinement for the second path.
	* @return Status code (0 = success).
	*/
	CPSIG_API int sig_kernel_backprop(const double* gram, double* out, double deriv, const double* k_grid, uint64_t dimension, uint64_t length1, uint64_t length2, uint64_t dyadic_order_1, uint64_t dyadic_order_2) noexcept;
	
	/**
	* @brief Backpropagation through batch_sig_kernel.
	*
	* @param gram Pointer to batch gram matrix data (row-major), size = `batch_size * (length1 - 1) * (length2 - 1)`.
	* @param out Pointer to output buffer (row-major, preallocated), size = `batch_size * (length1 - 1) * (length2 - 1)`.
	* @param derivs Pointer to derivatives with respect to the signature kernels, size = `batch_size`.
	* @param k_grid Pointer to batch of signature kernel PDE grids (row-major, precomputed), size = `batch_size * (((length1 - 1) << dyadic_order_1) + 1) * (((length2 - 1) << dyadic_order_2) + 1)`.
	* @param batch_size Batch size of the paths.
	* @param dimension Dimension of the paths.
	* @param length1 Length of the first paths.
	* @param length2 Length of the second paths.
	* @param dyadic_order_1 Dyadic refinement for the first paths.
	* @param dyadic_order_2 Dyadic refinement for the second paths.
	* @param n_jobs Number of threads to run in parallel. If n_jobs = 1, the computation is run serially. If set to -1, all 
	*				available threads are used. For n_jobs below -1, (max_threads + 1 + n_jobs) threads are used. For example 
	*				if n_jobs = -2, all threads but one are used (default = 1).
	* @return Status code (0 = success).
	*/
	CPSIG_API int batch_sig_kernel_backprop(const double* gram, double* out, const double* derivs, const double* k_grid, uint64_t batch_size, uint64_t dimension, uint64_t length1, uint64_t length2, uint64_t dyadic_order_1, uint64_t dyadic_order_2, int n_jobs = 1) noexcept;
}


