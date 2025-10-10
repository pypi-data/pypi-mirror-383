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
#include "utils.h"
#include <stdbool.h>

lp_problem_t *read_mps_file(const char *filename);

#ifdef __cplusplus
extern "C"
{
#endif

    void lp_problem_free(lp_problem_t *L);

    rescale_info_t *rescale_problem(
        const pdhg_parameters_t *params,
        const lp_problem_t *original_problem);

#ifdef __cplusplus
}
#endif
