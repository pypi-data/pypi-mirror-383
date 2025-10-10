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

#include "solver.h"
#include "utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <stdbool.h>

#include <cuda_runtime.h>
#include <cublas_v2.h>
#include <cusparse.h>

__global__ void compute_next_pdhg_primal_solution_kernel(
    const double *current_primal, double *reflected_primal, const double *dual_product,
    const double *objective, const double *var_lb, const double *var_ub,
    int n, double step_size);
__global__ void compute_next_pdhg_primal_solution_major_kernel(
    const double *current_primal, double *pdhg_primal, double *reflected_primal,
    const double *dual_product, const double *objective, const double *var_lb,
    const double *var_ub, int n, double step_size, double *dual_slack);
__global__ void compute_next_pdhg_dual_solution_kernel(
    const double *current_dual, double *reflected_dual, const double *primal_product,
    const double *const_lb, const double *const_ub, int n, double step_size);
__global__ void compute_next_pdhg_dual_solution_major_kernel(
    const double *current_dual, double *pdhg_dual, double *reflected_dual,
    const double *primal_product, const double *const_lb, const double *const_ub,
    int n, double step_size);
__global__ void halpern_update_kernel(
    const double *initial_primal, double *current_primal, const double *reflected_primal,
    const double *initial_dual, double *current_dual, const double *reflected_dual,
    int n_vars, int n_cons, double weight, double reflection_coeff);
__global__ void rescale_solution_kernel(
    double *primal_solution, double *dual_solution, const double *variable_rescaling, const double *constraint_rescaling,
    const double objective_vector_rescaling, const double constraint_bound_rescaling,
    int n_vars, int n_cons);
__global__ void compute_delta_solution_kernel(
    const double *initial_primal, const double *pdhg_primal, double *delta_primal,
    const double *initial_dual, const double *pdhg_dual, double *delta_dual,
    int n_vars, int n_cons);
static void compute_next_pdhg_primal_solution(pdhg_solver_state_t *state);
static void compute_next_pdhg_dual_solution(pdhg_solver_state_t *state);
static void halpern_update(pdhg_solver_state_t *state, double reflection_coefficient);
static void rescale_solution(pdhg_solver_state_t *state);
static cupdlpx_result_t *create_result_from_state(pdhg_solver_state_t *state);
static void perform_restart(pdhg_solver_state_t *state, const pdhg_parameters_t *cudaMemsetParams);
static void initialize_step_size_and_primal_weight(pdhg_solver_state_t *state, const pdhg_parameters_t *params);
static pdhg_solver_state_t *initialize_solver_state(
    const lp_problem_t *original_problem,
    const rescale_info_t *rescale_info);
static void compute_fixed_point_error(pdhg_solver_state_t *state);
void pdhg_solver_state_free(pdhg_solver_state_t *state);
void rescale_info_free(rescale_info_t *info);

cupdlpx_result_t *optimize(const pdhg_parameters_t *params, const lp_problem_t *original_problem)
{
    print_initial_info(params, original_problem);
    rescale_info_t *rescale_info = rescale_problem(params, original_problem);
    pdhg_solver_state_t *state = initialize_solver_state(original_problem, rescale_info);

    rescale_info_free(rescale_info);
    initialize_step_size_and_primal_weight(state, params);
    clock_t start_time = clock();
    bool do_restart = false;
    while (state->termination_reason == TERMINATION_REASON_UNSPECIFIED)
    {
        if ((state->is_this_major_iteration || state->total_count == 0) || (state->total_count % get_print_frequency(state->total_count) == 0))
        {
            compute_residual(state);
            if (state->is_this_major_iteration && state->total_count < 3 * params->termination_evaluation_frequency)
            {
                compute_infeasibility_information(state);
            }

            state->cumulative_time_sec = (double)(clock() - start_time) / CLOCKS_PER_SEC;

            check_termination_criteria(state, &params->termination_criteria);
            display_iteration_stats(state, params->verbose);
        }

        if ((state->is_this_major_iteration || state->total_count == 0))
        {
            do_restart = should_do_adaptive_restart(state, &params->restart_params, params->termination_evaluation_frequency);
            if (do_restart)
                perform_restart(state, params);
        }

        state->is_this_major_iteration = ((state->total_count + 1) % params->termination_evaluation_frequency) == 0;

        compute_next_pdhg_primal_solution(state);
        compute_next_pdhg_dual_solution(state);

        if (state->is_this_major_iteration || do_restart)
        {
            compute_fixed_point_error(state);
            if (do_restart)
            {
                state->initial_fixed_point_error = state->fixed_point_error;
                do_restart = false;
            }
        }
        halpern_update(state, params->reflection_coefficient);

        state->inner_count++;
        state->total_count++;
    }

    pdhg_final_log(state, params->verbose, state->termination_reason);
    cupdlpx_result_t *results = create_result_from_state(state);
    pdhg_solver_state_free(state);
    return results;
}

static pdhg_solver_state_t *initialize_solver_state(
    const lp_problem_t *original_problem,
    const rescale_info_t *rescale_info)
{
    pdhg_solver_state_t *state = (pdhg_solver_state_t *)safe_calloc(1, sizeof(pdhg_solver_state_t));

    int n_vars = original_problem->num_variables;
    int n_cons = original_problem->num_constraints;
    size_t var_bytes = n_vars * sizeof(double);
    size_t con_bytes = n_cons * sizeof(double);

    state->num_variables = n_vars;
    state->num_constraints = n_cons;
    state->objective_constant = original_problem->objective_constant;

    state->constraint_matrix = (cu_sparse_matrix_csr_t *)safe_malloc(sizeof(cu_sparse_matrix_csr_t));
    state->constraint_matrix_t = (cu_sparse_matrix_csr_t *)safe_malloc(sizeof(cu_sparse_matrix_csr_t));

    state->constraint_matrix->num_rows = n_cons;
    state->constraint_matrix->num_cols = n_vars;
    state->constraint_matrix->num_nonzeros = original_problem->constraint_matrix_num_nonzeros;

    state->constraint_matrix_t->num_rows = n_vars;
    state->constraint_matrix_t->num_cols = n_cons;
    state->constraint_matrix_t->num_nonzeros = original_problem->constraint_matrix_num_nonzeros;

    state->termination_reason = TERMINATION_REASON_UNSPECIFIED;

    state->rescaling_time_sec = rescale_info->rescaling_time_sec;

#define ALLOC_AND_COPY(dest, src, bytes)  \
    CUDA_CHECK(cudaMalloc(&dest, bytes)); \
    CUDA_CHECK(cudaMemcpy(dest, src, bytes, cudaMemcpyHostToDevice));

    ALLOC_AND_COPY(state->constraint_matrix->row_ptr, rescale_info->scaled_problem->constraint_matrix_row_pointers, (n_cons + 1) * sizeof(int));
    ALLOC_AND_COPY(state->constraint_matrix->col_ind, rescale_info->scaled_problem->constraint_matrix_col_indices, rescale_info->scaled_problem->constraint_matrix_num_nonzeros * sizeof(int));
    ALLOC_AND_COPY(state->constraint_matrix->val, rescale_info->scaled_problem->constraint_matrix_values, rescale_info->scaled_problem->constraint_matrix_num_nonzeros * sizeof(double));

    CUDA_CHECK(cudaMalloc(&state->constraint_matrix_t->row_ptr, (n_vars + 1) * sizeof(int)));
    CUDA_CHECK(cudaMalloc(&state->constraint_matrix_t->col_ind, rescale_info->scaled_problem->constraint_matrix_num_nonzeros * sizeof(int)));
    CUDA_CHECK(cudaMalloc(&state->constraint_matrix_t->val, rescale_info->scaled_problem->constraint_matrix_num_nonzeros * sizeof(double)));

    CUSPARSE_CHECK(cusparseCreate(&state->sparse_handle));
    CUBLAS_CHECK(cublasCreate(&state->blas_handle));
    CUBLAS_CHECK(cublasSetPointerMode(state->blas_handle, CUBLAS_POINTER_MODE_HOST));

    size_t buffer_size = 0;
    void *buffer = nullptr;
    CUSPARSE_CHECK(cusparseCsr2cscEx2_bufferSize(
        state->sparse_handle, state->constraint_matrix->num_rows, state->constraint_matrix->num_cols, state->constraint_matrix->num_nonzeros,
        state->constraint_matrix->val, state->constraint_matrix->row_ptr, state->constraint_matrix->col_ind,
        state->constraint_matrix_t->val, state->constraint_matrix_t->row_ptr, state->constraint_matrix_t->col_ind,
        CUDA_R_64F, CUSPARSE_ACTION_NUMERIC, CUSPARSE_INDEX_BASE_ZERO,
        CUSPARSE_CSR2CSC_ALG_DEFAULT, &buffer_size));
    CUDA_CHECK(cudaMalloc(&buffer, buffer_size));

    CUSPARSE_CHECK(cusparseCsr2cscEx2(
        state->sparse_handle, state->constraint_matrix->num_rows, state->constraint_matrix->num_cols, state->constraint_matrix->num_nonzeros,
        state->constraint_matrix->val, state->constraint_matrix->row_ptr, state->constraint_matrix->col_ind,
        state->constraint_matrix_t->val, state->constraint_matrix_t->row_ptr, state->constraint_matrix_t->col_ind,
        CUDA_R_64F, CUSPARSE_ACTION_NUMERIC, CUSPARSE_INDEX_BASE_ZERO,
        CUSPARSE_CSR2CSC_ALG_DEFAULT, buffer));

    CUDA_CHECK(cudaFree(buffer));

    ALLOC_AND_COPY(state->variable_lower_bound, rescale_info->scaled_problem->variable_lower_bound, var_bytes);
    ALLOC_AND_COPY(state->variable_upper_bound, rescale_info->scaled_problem->variable_upper_bound, var_bytes);
    ALLOC_AND_COPY(state->objective_vector, rescale_info->scaled_problem->objective_vector, var_bytes);
    ALLOC_AND_COPY(state->constraint_lower_bound, rescale_info->scaled_problem->constraint_lower_bound, con_bytes);
    ALLOC_AND_COPY(state->constraint_upper_bound, rescale_info->scaled_problem->constraint_upper_bound, con_bytes);
    ALLOC_AND_COPY(state->constraint_rescaling, rescale_info->con_rescale, con_bytes);
    ALLOC_AND_COPY(state->variable_rescaling, rescale_info->var_rescale, var_bytes);

    state->constraint_bound_rescaling = rescale_info->con_bound_rescale;
    state->objective_vector_rescaling = rescale_info->obj_vec_rescale;

#define ALLOC_ZERO(dest, bytes)           \
    CUDA_CHECK(cudaMalloc(&dest, bytes)); \
    CUDA_CHECK(cudaMemset(dest, 0, bytes));

    ALLOC_ZERO(state->initial_primal_solution, var_bytes);
    ALLOC_ZERO(state->current_primal_solution, var_bytes);
    ALLOC_ZERO(state->pdhg_primal_solution, var_bytes);
    ALLOC_ZERO(state->reflected_primal_solution, var_bytes);
    ALLOC_ZERO(state->dual_product, var_bytes);
    ALLOC_ZERO(state->dual_slack, var_bytes);
    ALLOC_ZERO(state->dual_residual, var_bytes);
    ALLOC_ZERO(state->delta_primal_solution, var_bytes);

    ALLOC_ZERO(state->initial_dual_solution, con_bytes);
    ALLOC_ZERO(state->current_dual_solution, con_bytes);
    ALLOC_ZERO(state->pdhg_dual_solution, con_bytes);
    ALLOC_ZERO(state->reflected_dual_solution, con_bytes);
    ALLOC_ZERO(state->primal_product, con_bytes);
    ALLOC_ZERO(state->primal_slack, con_bytes);
    ALLOC_ZERO(state->primal_residual, con_bytes);
    ALLOC_ZERO(state->delta_dual_solution, con_bytes);

    if (original_problem->primal_start) {
        double *rescaled = (double *)safe_malloc(var_bytes);
        for (int i = 0; i < n_vars; ++i)
            rescaled[i] = original_problem->primal_start[i] * rescale_info->var_rescale[i] * rescale_info->con_bound_rescale;
        CUDA_CHECK(cudaMemcpy(state->initial_primal_solution, rescaled, var_bytes, cudaMemcpyHostToDevice));
        free(rescaled);
    }
    if (original_problem->dual_start) {
        double *rescaled = (double *)safe_malloc(con_bytes);
        for (int i = 0; i < n_cons; ++i)
            rescaled[i] = original_problem->dual_start[i] * rescale_info->con_rescale[i] * rescale_info->obj_vec_rescale;
        CUDA_CHECK(cudaMemcpy(state->initial_dual_solution, rescaled, con_bytes, cudaMemcpyHostToDevice));
        free(rescaled);
    }

    double *temp_host = (double *)safe_malloc(fmax(var_bytes, con_bytes));
    for (int i = 0; i < n_cons; ++i)
        temp_host[i] = isfinite(rescale_info->scaled_problem->constraint_lower_bound[i]) ? rescale_info->scaled_problem->constraint_lower_bound[i] : 0.0;
    ALLOC_AND_COPY(state->constraint_lower_bound_finite_val, temp_host, con_bytes);
    for (int i = 0; i < n_cons; ++i)
        temp_host[i] = isfinite(rescale_info->scaled_problem->constraint_upper_bound[i]) ? rescale_info->scaled_problem->constraint_upper_bound[i] : 0.0;
    ALLOC_AND_COPY(state->constraint_upper_bound_finite_val, temp_host, con_bytes);
    for (int i = 0; i < n_vars; ++i)
        temp_host[i] = isfinite(rescale_info->scaled_problem->variable_lower_bound[i]) ? rescale_info->scaled_problem->variable_lower_bound[i] : 0.0;
    ALLOC_AND_COPY(state->variable_lower_bound_finite_val, temp_host, var_bytes);
    for (int i = 0; i < n_vars; ++i)
        temp_host[i] = isfinite(rescale_info->scaled_problem->variable_upper_bound[i]) ? rescale_info->scaled_problem->variable_upper_bound[i] : 0.0;
    ALLOC_AND_COPY(state->variable_upper_bound_finite_val, temp_host, var_bytes);
    free(temp_host);

    double sum_of_squares = 0.0;

    for (int i = 0; i < n_vars; ++i)
    {
        sum_of_squares += original_problem->objective_vector[i] * original_problem->objective_vector[i];
    }
    state->objective_vector_norm = sqrt(sum_of_squares);

    sum_of_squares = 0.0;

    for (int i = 0; i < n_cons; ++i)
    {
        double lower = original_problem->constraint_lower_bound[i];
        double upper = original_problem->constraint_upper_bound[i];

        if (isfinite(lower) && (lower != upper))
        {
            sum_of_squares += lower * lower;
        }

        if (isfinite(upper))
        {
            sum_of_squares += upper * upper;
        }
    }

    state->constraint_bound_norm = sqrt(sum_of_squares);
    state->num_blocks_primal = (state->num_variables + THREADS_PER_BLOCK - 1) / THREADS_PER_BLOCK;
    state->num_blocks_dual = (state->num_constraints + THREADS_PER_BLOCK - 1) / THREADS_PER_BLOCK;
    state->num_blocks_primal_dual = (state->num_variables + state->num_constraints + THREADS_PER_BLOCK - 1) / THREADS_PER_BLOCK;

    state->best_primal_dual_residual_gap = INFINITY;
    state->best_primal_dual_residual_gap = INFINITY;
    state->last_trial_fixed_point_error = INFINITY;
    state->step_size = 0.0;
    state->is_this_major_iteration = false;

    size_t primal_spmv_buffer_size;
    size_t dual_spmv_buffer_size;

    CUSPARSE_CHECK(cusparseCreateCsr(&state->matA, state->num_constraints, state->num_variables, state->constraint_matrix->num_nonzeros, state->constraint_matrix->row_ptr, state->constraint_matrix->col_ind, state->constraint_matrix->val, CUSPARSE_INDEX_32I, CUSPARSE_INDEX_32I, CUSPARSE_INDEX_BASE_ZERO, CUDA_R_64F));

    CUDA_CHECK(cudaGetLastError());

    CUSPARSE_CHECK(cusparseCreateCsr(&state->matAt, state->num_variables, state->num_constraints, state->constraint_matrix_t->num_nonzeros, state->constraint_matrix_t->row_ptr, state->constraint_matrix_t->col_ind, state->constraint_matrix_t->val, CUSPARSE_INDEX_32I, CUSPARSE_INDEX_32I, CUSPARSE_INDEX_BASE_ZERO, CUDA_R_64F));
    CUDA_CHECK(cudaGetLastError());

    CUSPARSE_CHECK(cusparseCreateDnVec(&state->vec_primal_sol, state->num_variables, state->pdhg_primal_solution, CUDA_R_64F));
    CUSPARSE_CHECK(cusparseCreateDnVec(&state->vec_dual_sol, state->num_constraints, state->pdhg_dual_solution, CUDA_R_64F));
    CUSPARSE_CHECK(cusparseCreateDnVec(&state->vec_primal_prod, state->num_constraints, state->primal_product, CUDA_R_64F));
    CUSPARSE_CHECK(cusparseCreateDnVec(&state->vec_dual_prod, state->num_variables, state->dual_product, CUDA_R_64F));
    CUSPARSE_CHECK(cusparseSpMV_bufferSize(state->sparse_handle, CUSPARSE_OPERATION_NON_TRANSPOSE, &HOST_ONE, state->matA, state->vec_primal_sol, &HOST_ZERO, state->vec_primal_prod, CUDA_R_64F, CUSPARSE_SPMV_CSR_ALG2, &primal_spmv_buffer_size));

    CUSPARSE_CHECK(cusparseSpMV_bufferSize(state->sparse_handle, CUSPARSE_OPERATION_NON_TRANSPOSE, &HOST_ONE, state->matAt, state->vec_dual_sol, &HOST_ZERO, state->vec_dual_prod, CUDA_R_64F, CUSPARSE_SPMV_CSR_ALG2, &dual_spmv_buffer_size));
    CUDA_CHECK(cudaMalloc(&state->primal_spmv_buffer, primal_spmv_buffer_size));
    CUSPARSE_CHECK(cusparseSpMV_preprocess(state->sparse_handle, CUSPARSE_OPERATION_NON_TRANSPOSE,
                                           &HOST_ONE, state->matA, state->vec_primal_sol, &HOST_ZERO, state->vec_primal_prod,
                                           CUDA_R_64F, CUSPARSE_SPMV_CSR_ALG2, state->primal_spmv_buffer));

    CUDA_CHECK(cudaMalloc(&state->dual_spmv_buffer, dual_spmv_buffer_size));
    CUSPARSE_CHECK(cusparseSpMV_preprocess(state->sparse_handle, CUSPARSE_OPERATION_NON_TRANSPOSE,
                                           &HOST_ONE, state->matAt, state->vec_dual_sol, &HOST_ZERO, state->vec_dual_prod,
                                           CUDA_R_64F, CUSPARSE_SPMV_CSR_ALG2, state->dual_spmv_buffer));

    CUDA_CHECK(cudaMalloc(&state->ones_primal_d, state->num_variables * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&state->ones_dual_d, state->num_constraints * sizeof(double)));

    double *ones_primal_h = (double *)safe_malloc(state->num_variables * sizeof(double));
    for (int i = 0; i < state->num_variables; ++i)
        ones_primal_h[i] = 1.0;
    CUDA_CHECK(cudaMemcpy(state->ones_primal_d, ones_primal_h, state->num_variables * sizeof(double), cudaMemcpyHostToDevice));
    free(ones_primal_h);

    double *ones_dual_h = (double *)safe_malloc(state->num_constraints * sizeof(double));
    for (int i = 0; i < state->num_constraints; ++i)
        ones_dual_h[i] = 1.0;
    CUDA_CHECK(cudaMemcpy(state->ones_dual_d, ones_dual_h, state->num_constraints * sizeof(double), cudaMemcpyHostToDevice));
    free(ones_dual_h);

    return state;
}

__global__ void compute_next_pdhg_primal_solution_kernel(
    const double *current_primal, double *reflected_primal, const double *dual_product,
    const double *objective, const double *var_lb, const double *var_ub,
    int n, double step_size)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n)
    {
        double temp = current_primal[i] - step_size * (objective[i] - dual_product[i]);
        double temp_proj = fmax(var_lb[i], fmin(temp, var_ub[i]));
        reflected_primal[i] = 2.0 * temp_proj - current_primal[i];
    }
}

__global__ void compute_next_pdhg_primal_solution_major_kernel(
    const double *current_primal, double *pdhg_primal, double *reflected_primal,
    const double *dual_product, const double *objective, const double *var_lb,
    const double *var_ub, int n, double step_size, double *dual_slack)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n)
    {
        double temp = current_primal[i] - step_size * (objective[i] - dual_product[i]);
        pdhg_primal[i] = fmax(var_lb[i], fmin(temp, var_ub[i]));
        dual_slack[i] = (pdhg_primal[i] - temp) / step_size;
        reflected_primal[i] = 2.0 * pdhg_primal[i] - current_primal[i];
    }
}

__global__ void compute_next_pdhg_dual_solution_kernel(
    const double *current_dual, double *reflected_dual, const double *primal_product,
    const double *const_lb, const double *const_ub, int n, double step_size)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n)
    {
        double temp = current_dual[i] / step_size - primal_product[i];
        double temp_proj = fmax(-const_ub[i], fmin(temp, -const_lb[i]));
        reflected_dual[i] = 2.0 * (temp - temp_proj) * step_size - current_dual[i];
    }
}

__global__ void compute_next_pdhg_dual_solution_major_kernel(
    const double *current_dual, double *pdhg_dual, double *reflected_dual,
    const double *primal_product, const double *const_lb, const double *const_ub,
    int n, double step_size)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n)
    {
        double temp = current_dual[i] / step_size - primal_product[i];
        double temp_proj = fmax(-const_ub[i], fmin(temp, -const_lb[i]));
        pdhg_dual[i] = (temp - temp_proj) * step_size;
        reflected_dual[i] = 2.0 * pdhg_dual[i] - current_dual[i];
    }
}

__global__ void halpern_update_kernel(
    const double *initial_primal, double *current_primal, const double *reflected_primal,
    const double *initial_dual, double *current_dual, const double *reflected_dual,
    int n_vars, int n_cons, double weight, double reflection_coeff)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n_vars)
    {
        double reflected = reflection_coeff * reflected_primal[i] + (1.0 - reflection_coeff) * current_primal[i];
        current_primal[i] = weight * reflected + (1.0 - weight) * initial_primal[i];
    }
    else if (i < n_vars + n_cons)
    {
        int idx = i - n_vars;
        double reflected = reflection_coeff * reflected_dual[idx] + (1.0 - reflection_coeff) * current_dual[idx];
        current_dual[idx] = weight * reflected + (1.0 - weight) * initial_dual[idx];
    }
}

__global__ void rescale_solution_kernel(
    double *primal_solution, double *dual_solution, const double *variable_rescaling, const double *constraint_rescaling,
    const double objective_vector_rescaling, const double constraint_bound_rescaling,
    int n_vars, int n_cons)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n_vars)
    {
        primal_solution[i] = primal_solution[i] / variable_rescaling[i] / constraint_bound_rescaling;
    }
    else if (i < n_vars + n_cons)
    {
        int idx = i - n_vars;
        dual_solution[idx] = dual_solution[idx] / constraint_rescaling[idx] / objective_vector_rescaling;
    }
}

__global__ void compute_delta_solution_kernel(
    const double *initial_primal, const double *pdhg_primal, double *delta_primal,
    const double *initial_dual, const double *pdhg_dual, double *delta_dual,
    int n_vars, int n_cons)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n_vars)
    {
        delta_primal[i] = pdhg_primal[i] - initial_primal[i];
    }
    else if (i < n_vars + n_cons)
    {
        int idx = i - n_vars;
        delta_dual[idx] = pdhg_dual[idx] - initial_dual[idx];
    }
}

static void compute_next_pdhg_primal_solution(pdhg_solver_state_t *state)
{
    CUSPARSE_CHECK(cusparseDnVecSetValues(state->vec_dual_sol, state->current_dual_solution));
    CUSPARSE_CHECK(cusparseDnVecSetValues(state->vec_dual_prod, state->dual_product));

    CUSPARSE_CHECK(cusparseSpMV(
        state->sparse_handle, CUSPARSE_OPERATION_NON_TRANSPOSE,
        &HOST_ONE, state->matAt, state->vec_dual_sol, &HOST_ZERO, state->vec_dual_prod,
        CUDA_R_64F, CUSPARSE_SPMV_CSR_ALG2, state->dual_spmv_buffer));

    double step = state->step_size / state->primal_weight;

    if (state->is_this_major_iteration || ((state->total_count + 2) % get_print_frequency(state->total_count + 2)) == 0)
    {
        compute_next_pdhg_primal_solution_major_kernel<<<state->num_blocks_primal, THREADS_PER_BLOCK>>>(
            state->current_primal_solution, state->pdhg_primal_solution, state->reflected_primal_solution,
            state->dual_product, state->objective_vector, state->variable_lower_bound,
            state->variable_upper_bound, state->num_variables, step, state->dual_slack);
    }
    else
    {
        compute_next_pdhg_primal_solution_kernel<<<state->num_blocks_primal, THREADS_PER_BLOCK>>>(
            state->current_primal_solution, state->reflected_primal_solution, state->dual_product,
            state->objective_vector, state->variable_lower_bound, state->variable_upper_bound,
            state->num_variables, step);
    }
}

static void compute_next_pdhg_dual_solution(pdhg_solver_state_t *state)
{
    CUSPARSE_CHECK(cusparseDnVecSetValues(state->vec_primal_sol, state->reflected_primal_solution));
    CUSPARSE_CHECK(cusparseDnVecSetValues(state->vec_primal_prod, state->primal_product));

    CUSPARSE_CHECK(cusparseSpMV(
        state->sparse_handle, CUSPARSE_OPERATION_NON_TRANSPOSE,
        &HOST_ONE, state->matA, state->vec_primal_sol, &HOST_ZERO, state->vec_primal_prod,
        CUDA_R_64F, CUSPARSE_SPMV_CSR_ALG2, state->primal_spmv_buffer));

    double step = state->step_size * state->primal_weight;

    if (state->is_this_major_iteration || ((state->total_count + 2) % get_print_frequency(state->total_count + 2)) == 0)
    {
        compute_next_pdhg_dual_solution_major_kernel<<<state->num_blocks_dual, THREADS_PER_BLOCK>>>(
            state->current_dual_solution, state->pdhg_dual_solution, state->reflected_dual_solution,
            state->primal_product, state->constraint_lower_bound, state->constraint_upper_bound,
            state->num_constraints, step);
    }
    else
    {
        compute_next_pdhg_dual_solution_kernel<<<state->num_blocks_dual, THREADS_PER_BLOCK>>>(
            state->current_dual_solution, state->reflected_dual_solution, state->primal_product,
            state->constraint_lower_bound, state->constraint_upper_bound, state->num_constraints, step);
    }
}

static void halpern_update(pdhg_solver_state_t *state, double reflection_coefficient)
{
    double weight = (double)(state->inner_count + 1) / (state->inner_count + 2);
    halpern_update_kernel<<<state->num_blocks_primal_dual, THREADS_PER_BLOCK>>>(
        state->initial_primal_solution, state->current_primal_solution, state->reflected_primal_solution,
        state->initial_dual_solution, state->current_dual_solution, state->reflected_dual_solution,
        state->num_variables, state->num_constraints, weight, reflection_coefficient);
}

static void rescale_solution(pdhg_solver_state_t *state)
{
    rescale_solution_kernel<<<state->num_blocks_primal_dual, THREADS_PER_BLOCK>>>(
        state->pdhg_primal_solution, state->pdhg_dual_solution,
        state->variable_rescaling, state->constraint_rescaling,
        state->objective_vector_rescaling, state->constraint_bound_rescaling,
        state->num_variables, state->num_constraints);
}

static void perform_restart(pdhg_solver_state_t *state, const pdhg_parameters_t *params)
{
    compute_delta_solution_kernel<<<state->num_blocks_primal_dual, THREADS_PER_BLOCK>>>(
        state->initial_primal_solution, state->pdhg_primal_solution, state->delta_primal_solution,
        state->initial_dual_solution, state->pdhg_dual_solution, state->delta_dual_solution,
        state->num_variables, state->num_constraints);

    double primal_dist, dual_dist;
    CUBLAS_CHECK(cublasDnrm2_v2_64(state->blas_handle, state->num_variables, state->delta_primal_solution, 1, &primal_dist));
    CUBLAS_CHECK(cublasDnrm2_v2_64(state->blas_handle, state->num_constraints, state->delta_dual_solution, 1, &dual_dist));

    double ratio_infeas = state->relative_dual_residual / state->relative_primal_residual;

    if (primal_dist > 1e-16 && dual_dist > 1e-16 && primal_dist < 1e12 && dual_dist < 1e12 && ratio_infeas > 1e-8 && ratio_infeas < 1e8)
    {
        double error = log(dual_dist) - log(primal_dist) - log(state->primal_weight);
        state->primal_weight_error_sum *= params->restart_params.i_smooth;
        state->primal_weight_error_sum += error;
        double delta_error = error - state->primal_weight_last_error;
        state->primal_weight *= exp(params->restart_params.k_p * error +
                                    params->restart_params.k_i * state->primal_weight_error_sum +
                                    params->restart_params.k_d * delta_error);
        state->primal_weight_last_error = error;
    }
    else
    {
        state->primal_weight = state->best_primal_weight;
        state->primal_weight_error_sum = 0.0;
        state->primal_weight_last_error = 0.0;
    }

    double primal_dual_residual_gap = abs(log10(state->relative_dual_residual / state->relative_primal_residual));
    if (primal_dual_residual_gap < state->best_primal_dual_residual_gap)
    {
        state->best_primal_dual_residual_gap = primal_dual_residual_gap;
        state->best_primal_weight = state->primal_weight;
    }

    CUDA_CHECK(cudaMemcpy(state->initial_primal_solution, state->pdhg_primal_solution, state->num_variables * sizeof(double), cudaMemcpyDeviceToDevice));
    CUDA_CHECK(cudaMemcpy(state->current_primal_solution, state->pdhg_primal_solution, state->num_variables * sizeof(double), cudaMemcpyDeviceToDevice));
    CUDA_CHECK(cudaMemcpy(state->initial_dual_solution, state->pdhg_dual_solution, state->num_constraints * sizeof(double), cudaMemcpyDeviceToDevice));
    CUDA_CHECK(cudaMemcpy(state->current_dual_solution, state->pdhg_dual_solution, state->num_constraints * sizeof(double), cudaMemcpyDeviceToDevice));

    state->inner_count = 0;
    state->last_trial_fixed_point_error = INFINITY;
}

static void initialize_step_size_and_primal_weight(pdhg_solver_state_t *state, const pdhg_parameters_t *params)
{
    double max_sv = estimate_maximum_singular_value(state->sparse_handle, state->blas_handle, state->constraint_matrix, state->constraint_matrix_t, 5000, 1e-4);
    state->step_size = 0.998 / max_sv;

    if (params->bound_objective_rescaling)
    {
        state->primal_weight = 1.0;
    }
    else
    {
        state->primal_weight = (state->objective_vector_norm + 1.0) / (state->constraint_bound_norm + 1.0);
    }
    state->best_primal_weight = state->primal_weight;
}

static void compute_fixed_point_error(pdhg_solver_state_t *state)
{
    compute_delta_solution_kernel<<<state->num_blocks_primal_dual, THREADS_PER_BLOCK>>>(
        state->current_primal_solution,
        state->reflected_primal_solution,
        state->delta_primal_solution,
        state->current_dual_solution,
        state->reflected_dual_solution,
        state->delta_dual_solution,
        state->num_variables,
        state->num_constraints);

    CUSPARSE_CHECK(cusparseDnVecSetValues(state->vec_dual_sol, state->delta_dual_solution));
    CUSPARSE_CHECK(cusparseDnVecSetValues(state->vec_dual_prod, state->dual_product));

    CUSPARSE_CHECK(cusparseSpMV(
        state->sparse_handle, CUSPARSE_OPERATION_NON_TRANSPOSE,
        &HOST_ONE, state->matAt, state->vec_dual_sol, &HOST_ZERO, state->vec_dual_prod,
        CUDA_R_64F, CUSPARSE_SPMV_CSR_ALG2, state->dual_spmv_buffer));

    double interaction, movement;

    double primal_norm = 0.0;
    double dual_norm = 0.0;
    double cross_term = 0.0;

    CUBLAS_CHECK(cublasDnrm2_v2_64(state->blas_handle,
                                   state->num_constraints,
                                   state->delta_dual_solution,
                                   1,
                                   &dual_norm));
    CUBLAS_CHECK(cublasDnrm2_v2_64(state->blas_handle,
                                   state->num_variables,
                                   state->delta_primal_solution,
                                   1,
                                   &primal_norm));
    movement = primal_norm * primal_norm * state->primal_weight + dual_norm * dual_norm / state->primal_weight;

    CUBLAS_CHECK(cublasDdot(state->blas_handle, state->num_variables, state->dual_product, 1, state->delta_primal_solution, 1, &cross_term));
    interaction = 2 * state->step_size * cross_term;

    state->fixed_point_error = sqrt(movement + interaction);
}

void pdhg_solver_state_free(pdhg_solver_state_t *state)
{
    if (state == NULL)
    {
        return;
    }

    if (state->variable_lower_bound)
        CUDA_CHECK(cudaFree(state->variable_lower_bound));
    if (state->variable_upper_bound)
        CUDA_CHECK(cudaFree(state->variable_upper_bound));
    if (state->objective_vector)
        CUDA_CHECK(cudaFree(state->objective_vector));
    if (state->constraint_matrix->row_ptr)
        CUDA_CHECK(cudaFree(state->constraint_matrix->row_ptr));
    if (state->constraint_matrix->col_ind)
        CUDA_CHECK(cudaFree(state->constraint_matrix->col_ind));
    if (state->constraint_matrix->val)
        CUDA_CHECK(cudaFree(state->constraint_matrix->val));
    if (state->constraint_matrix_t->row_ptr)
        CUDA_CHECK(cudaFree(state->constraint_matrix_t->row_ptr));
    if (state->constraint_matrix_t->col_ind)
        CUDA_CHECK(cudaFree(state->constraint_matrix_t->col_ind));
    if (state->constraint_matrix_t->val)
        CUDA_CHECK(cudaFree(state->constraint_matrix_t->val));
    if (state->constraint_lower_bound)
        CUDA_CHECK(cudaFree(state->constraint_lower_bound));
    if (state->constraint_upper_bound)
        CUDA_CHECK(cudaFree(state->constraint_upper_bound));
    if (state->constraint_lower_bound_finite_val)
        CUDA_CHECK(cudaFree(state->constraint_lower_bound_finite_val));
    if (state->constraint_upper_bound_finite_val)
        CUDA_CHECK(cudaFree(state->constraint_upper_bound_finite_val));
    if (state->variable_lower_bound_finite_val)
        CUDA_CHECK(cudaFree(state->variable_lower_bound_finite_val));
    if (state->variable_upper_bound_finite_val)
        CUDA_CHECK(cudaFree(state->variable_upper_bound_finite_val));
    if (state->initial_primal_solution)
        CUDA_CHECK(cudaFree(state->initial_primal_solution));
    if (state->current_primal_solution)
        CUDA_CHECK(cudaFree(state->current_primal_solution));
    if (state->pdhg_primal_solution)
        CUDA_CHECK(cudaFree(state->pdhg_primal_solution));
    if (state->reflected_primal_solution)
        CUDA_CHECK(cudaFree(state->reflected_primal_solution));
    if (state->dual_product)
        CUDA_CHECK(cudaFree(state->dual_product));
    if (state->initial_dual_solution)
        CUDA_CHECK(cudaFree(state->initial_dual_solution));
    if (state->current_dual_solution)
        CUDA_CHECK(cudaFree(state->current_dual_solution));
    if (state->pdhg_dual_solution)
        CUDA_CHECK(cudaFree(state->pdhg_dual_solution));
    if (state->reflected_dual_solution)
        CUDA_CHECK(cudaFree(state->reflected_dual_solution));
    if (state->primal_product)
        CUDA_CHECK(cudaFree(state->primal_product));
    if (state->constraint_rescaling)
        CUDA_CHECK(cudaFree(state->constraint_rescaling));
    if (state->variable_rescaling)
        CUDA_CHECK(cudaFree(state->variable_rescaling));
    if (state->primal_slack)
        CUDA_CHECK(cudaFree(state->primal_slack));
    if (state->dual_slack)
        CUDA_CHECK(cudaFree(state->dual_slack));
    if (state->primal_residual)
        CUDA_CHECK(cudaFree(state->primal_residual));
    if (state->dual_residual)
        CUDA_CHECK(cudaFree(state->dual_residual));
    if (state->delta_primal_solution)
        CUDA_CHECK(cudaFree(state->delta_primal_solution));
    if (state->delta_dual_solution)
        CUDA_CHECK(cudaFree(state->delta_dual_solution));
    if (state->ones_primal_d)
        CUDA_CHECK(cudaFree(state->ones_primal_d));
    if (state->ones_dual_d)
        CUDA_CHECK(cudaFree(state->ones_dual_d));

    free(state);
}

void rescale_info_free(rescale_info_t *info)
{
    if (info == NULL)
    {
        return;
    }

    lp_problem_free(info->scaled_problem);
    free(info->con_rescale);
    free(info->var_rescale);

    free(info);
}

void cupdlpx_result_free(cupdlpx_result_t *results)
{
    if (results == NULL)
    {
        return;
    }

    free(results->primal_solution);
    free(results->dual_solution);
    free(results);
}

static cupdlpx_result_t *create_result_from_state(pdhg_solver_state_t *state)
{
    cupdlpx_result_t *results = (cupdlpx_result_t *)safe_calloc(1, sizeof(cupdlpx_result_t));

    rescale_solution(state);

    results->primal_solution = (double *)safe_malloc(state->num_variables * sizeof(double));
    results->dual_solution = (double *)safe_malloc(state->num_constraints * sizeof(double));

    CUDA_CHECK(cudaMemcpy(results->primal_solution, state->pdhg_primal_solution, state->num_variables * sizeof(double), cudaMemcpyDeviceToHost));
    CUDA_CHECK(cudaMemcpy(results->dual_solution, state->pdhg_dual_solution, state->num_constraints * sizeof(double), cudaMemcpyDeviceToHost));

    results->num_variables = state->num_variables;
    results->num_constraints = state->num_constraints;
    results->total_count = state->total_count;
    results->rescaling_time_sec = state->rescaling_time_sec;
    results->cumulative_time_sec = state->cumulative_time_sec;
    results->relative_primal_residual = state->relative_primal_residual;
    results->relative_dual_residual = state->relative_dual_residual;
    results->primal_objective_value = state->primal_objective_value;
    results->dual_objective_value = state->dual_objective_value;
    results->objective_gap = state->objective_gap;
    results->relative_objective_gap = state->relative_objective_gap;
    results->max_primal_ray_infeasibility = state->max_primal_ray_infeasibility;
    results->max_dual_ray_infeasibility = state->max_dual_ray_infeasibility;
    results->primal_ray_linear_objective = state->primal_ray_linear_objective;
    results->dual_ray_objective = state->dual_ray_objective;
    results->termination_reason = state->termination_reason;

    return results;
}

void set_default_parameters(pdhg_parameters_t *params)
{
    params->l_inf_ruiz_iterations = 10;
    params->has_pock_chambolle_alpha = true;
    params->pock_chambolle_alpha = 1.0;
    params->bound_objective_rescaling = true;
    params->verbose = false;
    params->termination_evaluation_frequency = 200;
    params->reflection_coefficient = 1.0;

    params->termination_criteria.eps_optimal_relative = 1e-4;
    params->termination_criteria.eps_feasible_relative = 1e-4;
    params->termination_criteria.eps_infeasible = 1e-10;
    params->termination_criteria.time_sec_limit = 3600.0;
    params->termination_criteria.iteration_limit = INT32_MAX;

    params->restart_params.artificial_restart_threshold = 0.36;
    params->restart_params.sufficient_reduction_for_restart = 0.2;
    params->restart_params.necessary_reduction_for_restart = 0.5;
    params->restart_params.k_p = 0.99;
    params->restart_params.k_i = 0.01;
    params->restart_params.k_d = 0.0;
    params->restart_params.i_smooth = 0.3;
}