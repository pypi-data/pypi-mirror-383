# SPDX-FileCopyrightText: 2025-present Ye Joo Park <subwaymatch@gmail.com>
#
# SPDX-License-Identifier: MIT
from .__about__ import __version__
from .grader import grade_notebooks, grade_single_notebook
from .models.grading_dataclasses import GradedResult, TestCaseResult
from .notebook_operations import (
    extract_test_case_metadata_from_code,
    extract_test_cases_metadata_from_notebook,
    remove_code_cells_that_contain,
    does_cell_contain_test_case,
    is_manually_graded_test_case,
    extract_user_code_from_notebook,
    remove_comments,
    get_test_cases_hash,
)
from .generate_assignment import generate_assignment

__all__ = [
    "__version__",
    "grade_notebooks",
    "grade_single_notebook",
    "GradedResult",
    "TestCaseResult",
    "extract_test_case_metadata_from_code",
    "extract_test_cases_metadata_from_notebook",
    "remove_code_cells_that_contain",
    "does_cell_contain_test_case",
    "is_manually_graded_test_case",
    "extract_user_code_from_notebook",
    "remove_comments",
    "get_test_cases_hash",
    "generate_assignment",
]
