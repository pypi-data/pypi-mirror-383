# A Simple Autograder for Jupyter Notebooks

<p align="center">
  <img src="https://github.com/subwaymatch/jupygrader/blob/main/docs/images/logo_jupygrader_with_text_240.png?raw=true" alt="Jupygrader Logo" width="240"/>
</p>

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/0ce9977cb9474fc0a2d7c531c988196b)](https://app.codacy.com/gh/subwaymatch/jupygrader/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

[![PyPI - Version](https://img.shields.io/pypi/v/jupygrader.svg)](https://pypi.org/project/jupygrader)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/jupygrader.svg)](https://pypi.org/project/jupygrader)

Easily grade Jupyter notebooks using test cases and generate detailed reports.

## Creating an autogradable notebook

Creating an autogradable item is as simple as adding a cell with a test case name (`_test_case`) and points ( `_points` ) to the notebook.

Assume your student is tasked to add `x` and `y`, and store the result to a new variable named `sum_xy`.

```python
# file: submissions/student1.ipynb
# Task: Calculate the sum of x and y,
# and store it to a new variable named `sum_xy`

x = 1
y = 2

# YOUR CODE BEGINS
sum_xy = x + y
# YOUR CODE ENDS
```

Add a cell with the following content after the code cell.

```python
_test_case = "calculate-sum"
_points = 2

assert sum_xy == 3
```

## Grading notebooks

```python
from jupygrader import grade_notebooks

graded_results = grade_notebooks(['submissions/student1.ipynb'])
```

This will return a `GradedResult` object. Below is a sample output of the `GradedResult` object in JSON format.

```json
{
  "filename": "student1.ipynb",
  "learner_autograded_score": 2,
  "max_autograded_score": 2,
  "max_manually_graded_score": 0,
  "max_total_score": 2,
  "num_autograded_cases": 1,
  "num_passed_cases": 1,
  "num_failed_cases": 0,
  "num_manually_graded_cases": 0,
  "num_total_test_cases": 1,
  "grading_finished_at": "2025-03-19 06:49 PM UTC",
  "grading_duration_in_seconds": 0.02,
  "test_case_results": [
    {
      "test_case_name": "sum_xy",
      "points": 2,
      "available_points": 2,
      "did_pass": true,
      "grade_manually": false,
      "message": ""
    }
  ],
  "submission_notebook_hash": "c98c747e12a0456033956759c9daf7a0",
  "test_cases_hash": "ea8037ca2aedc3c33ec7227962cc2464",
  "grader_python_version": "3.12.5",
  "grader_platform": "Linux...",
  "jupygrader_version": "..."
  // ... more fields here
}
```

## Grading Multiple Notebooks

```python
import glob
from jupygrader import grade_notebooks

# Select all Jupyter notebooks in the "submissions" folder
notebooks = glob.glob('submissions/*.ipynb')

# Grade notebooks
graded_results = grade_notebooks(notebooks)
```

## 📝 Summary

Jupygrader is a Python package for automated grading of Jupyter notebooks. It provides a framework to:

1. **Execute and grade Jupyter notebooks** containing student work and test cases
2. **Generate comprehensive reports** in multiple formats (JSON, HTML, TXT)
3. **Extract student code** from notebooks into separate Python files
4. **Verify notebook integrity** by computing hashes of test cases and submissions

## ✨ Key Features

- Executes notebooks in a controlled, temporary environment
- Preserves the original notebook while creating graded versions
- Adds grader scripts to notebooks to evaluate test cases
- Supports multiple grading modes:
  - Automatic grading via assertions and tests
  - Manual grading
  - Hybrid
- Generates detailed grading results including:
  - Individual test case scores
  - Overall scores and summaries
  - Success/failure status of each test
  - Error messages for failed test cases
- Produces multiple output formats for instructors to review:
  - CSV export for batch grading results
  - Graded notebook (.ipynb)
  - HTML report
  - JSON result data
  - Plaintext summary for quick review
  - Extracted Python code
- Includes metadata like Python version, platform, and file hashes for verification

🔒 Security Features

- Executes notebooks in isolated temporary directories
- Computes hashes of both test cases and submissions for academic integrity and duplicate prevention
- Cleanup of temporary files after grading completes
- Option to obfuscate test case code to prevent students from seeing solutions

!!! warning

    This package provides only a basic obfuscation, and students with technical knowledge can easily decode the string to reveal the original code. Supporting a password-based encryption method is planned for future releases.

!!! tip

    For extra security, consider running the grading script inside a Docker container or a virtual machine. This ensures that the grading environment is isolated from the host system.

## 📊 Output Formats

Jupygrader generates multiple output formats for each graded notebook:

1. **Graded Notebook (.ipynb)** – The original notebook with test results
2. **HTML Report** – Interactive HTML with test case navigation and results highlighting
3. **JSON Results** – Structured data with comprehensive grading metrics
4. **Text Summary** – Plain text overview of scores and test outcomes
5. **CSV Export** – Tabular data for all notebooks in a batch
6. **Extracted Code (.py)** – Pure Python code extracted from student cells

## 🚀 Advanced Usage

Batch Processing with File Dependencies

```python
from jupygrader import grade_notebooks, GradingItem

# Configure grading with dependencies
grading_configs = [
    GradingItem(
        notebook_path="assignments/hw1/student1.ipynb",
        output_path="results/hw1",
        copy_files=["data/dataset.csv", "utility_functions.py"]
    ),
    GradingItem(
        notebook_path="assignments/hw1/student2.ipynb",
        output_path="results/hw1",
        copy_files=["data/dataset.csv", "utility_functions.py"]
    )
]

# Grade all notebooks with their dependencies
results = grade_notebooks(grading_configs)

```

Jupygrader is designed for educational settings where instructors need to grade student work in Jupyter notebooks, providing automated feedback while maintaining records of submissions and grading results.
