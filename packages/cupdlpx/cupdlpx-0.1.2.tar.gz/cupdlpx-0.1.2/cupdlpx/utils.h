/*
Copyright 2025 Haihao Lu

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

#pragma once

#include "struct.h"
#include <stdbool.h>
#include <cuda_runtime.h>
#include <cusparse.h>
#include <cublas_v2.h>
#ifdef __cplusplus
extern "C"
{
#endif

#define CUDA_CHECK(call)                                           \
    do                                                             \
    {                                                              \
        cudaError_t err = call;                                    \
        if (err != cudaSuccess)                                    \
        {                                                          \
            fprintf(stderr, "CUDA Error at %s:%d: %s\n", __FILE__, \
                    __LINE__, cudaGetErrorName(err));              \
            exit(EXIT_FAILURE);                                    \
        }                                                          \
    } while (0)

#define CUBLAS_CHECK(call)                                           \
    do                                                               \
    {                                                                \
        cublasStatus_t status = call;                                \
        if (status != CUBLAS_STATUS_SUCCESS)                         \
        {                                                            \
            fprintf(stderr, "cuBLAS Error at %s:%d: %s\n", __FILE__, \
                    __LINE__, cublasGetStatusName(status));          \
            exit(EXIT_FAILURE);                                      \
        }                                                            \
    } while (0)

#define CUSPARSE_CHECK(call)                                           \
    do                                                                 \
    {                                                                  \
        cusparseStatus_t status = call;                                \
        if (status != CUSPARSE_STATUS_SUCCESS)                         \
        {                                                              \
            fprintf(stderr, "cuSPARSE Error at %s:%d: %s\n", __FILE__, \
                    __LINE__, cusparseGetErrorName(status));           \
            exit(EXIT_FAILURE);                                        \
        }                                                              \
    } while (0)

#define THREADS_PER_BLOCK 256

    extern const double HOST_ONE;
    extern const double HOST_ZERO;

    void *safe_malloc(size_t size);
    
    void *safe_calloc(size_t num, size_t size);

    void *safe_realloc(void *ptr, size_t new_size);


    double estimate_maximum_singular_value(
        cusparseHandle_t sparse_handle,
        cublasHandle_t blas_handle,
        const cu_sparse_matrix_csr_t *A,
        const cu_sparse_matrix_csr_t *AT,
        int max_iterations,
        double tolerance);

    void compute_interaction_and_movement(
        pdhg_solver_state_t *solver_state,
        double *interaction,
        double *movement);

    bool should_do_adaptive_restart(
        pdhg_solver_state_t *solver_state,
        const restart_parameters_t *restart_params,
        int termination_evaluation_frequency);

    void check_termination_criteria(
        pdhg_solver_state_t *solver_state,
        const termination_criteria_t *criteria);

    void print_initial_info(const pdhg_parameters_t *params, const lp_problem_t *problem);

    void pdhg_final_log(
        const pdhg_solver_state_t *solver_state,
        bool verbose,
        termination_reason_t termination_reason);

    void display_iteration_stats(const pdhg_solver_state_t *solver_state, bool verbose);

    const char *termination_reason_to_string(termination_reason_t reason);

    int get_print_frequency(int iter);

    void compute_residual(pdhg_solver_state_t *state);

    void compute_infeasibility_information(pdhg_solver_state_t *state);

#ifdef __cplusplus
}

#endif
