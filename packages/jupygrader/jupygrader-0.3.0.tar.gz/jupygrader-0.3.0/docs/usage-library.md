# Using `jupygrader` as a Python Library

## 📦 Installation

```console
pip install jupygrader
```

## 🔄 Update Jupygrader

```console
pip install --upgrade jupygrader
```

## Grade Notebooks

---

### Grade multiple notebooks

Use the `grade_notebooks()` function to grade Jupyter notebooks. You can pass a list of notebook paths or a list of dictionaries for a more detailed configuration.

```python
from jupygrader import grade_notebooks

# Grade a list of notebooks
graded_results = grade_notebooks(["path/to/notebook1.ipynb", "path/to/notebook2.ipynb"])
```

!!! info "Custom Output Path and File Copying"

    You can specify the output path and copy files to the working directory for each notebook by passing a dictionary for each notebook.

    See the example below.

```python
from jupygrader import grade_notebooks

item1 = {
    "notebook_path": "path/to/notebook1.ipynb",
    "output_path": "path/to/output1",
    "copy_files": ["data1.csv"],
}
item2 = {
    "notebook_path": "path/to/notebook2.ipynb"
    # Use default output_path and do not copy files
}

graded_results = grade_notebooks([item1, item2])
```

You can also specify a dictionary for `copy_files` to place them in specific locations.

The key is the source file and the value is the destination path.

The destination path is relative to the working directory of the Jupyter notebook.

```python
from jupygrader import grade_notebooks

item1 = {
    "notebook_path": "path/to/notebook1.ipynb",
    "copy_files": {"my_data.parquet": "my_data.parquet"},
}

item2 = {
    "notebook_path": "path/to/notebook2.ipynb",
    "copy_files": {
        "data/population.csv": "another/path/population.csv",
        "titanic.db": "databases/titanic.db",
    },
}

graded_results = grade_notebooks([item1, item2])

```

If your assignment has base files that should be copied to every notebook's workspace, you can specify them in the `base_files` parameter of the `grade_notebooks` function. This will copy those files to the working directory of each notebook being graded.

```python
from jupygrader import grade_notebooks

graded_results = grade_notebooks(
    ["notebook1.ipynb", "notebook2.ipynb"],
    base_files={
        # Copy from the URL to data/my_data.csv in the working directory relative to the notebook
        "https://example.com/path/to/base_file.csv": "data/my_data.csv",
        # Local files are also supported
        "local-data/another_file.key": "openai_api_key.key",
    },
)
```

If a notebook has been already graded, it will skip grading and return the cached result. This is useful for large assignments where you want to avoid re-grading notebooks that have not changed.

```python
from jupygrader import grade_notebooks

graded_results1 = grade_notebooks(
    ["notebook1.ipynb", "notebook2.ipynb", "notebook3.ipynb"]
)

# The second call will skip re-grading for all three notebooks if they have not changed, and the jupygrader version is the same
graded_results2 = grade_notebooks(
    ["notebook1.ipynb", "notebook2.ipynb", "notebook3.ipynb"]
)

```

To force a regrade, use `regrade_existing=True` parameter. This will re-grade all specified notebooks regardless of whether they have been previously graded or not.

```python
graded_results2 = grade_notebooks(
    ["notebook1.ipynb", "notebook2.ipynb", "notebook3.ipynb"], regrade_existing=True
)
```

You can also control the verbosity of the output and whether to export the graded results to a CSV file. By default, verbose output is enabled and the graded results are exported to a CSV file named `graded_results_{%Y%m%d_%H%M%S}.csv` in the current working directory.

```python
from jupygrader import grade_notebooks

graded_results = grade_notebooks(
    ["notebook1.ipynb", "notebook2.ipynb", "notebook3.ipynb"],
    verbose=True,  # Default, set to False to disable verbose output
    export_csv=True,  # Default, set to False to disable CSV export
    csv_output_path="path/to/output/graded_results.csv",  # Optional: specify a custom path for the CSV output,
)
```

---

### Grade a single notebook

You can grade a single notebook using the `grade_single_notebook` function.

!!! note

    The `grade_single_notebook` function is a wrapper around the `grade_notebooks` function. It is provided for convenience.

=== "Basic"

    ```python
    from jupygrader import grade_single_notebook

    # Grade a single notebook by path
    graded_result = grade_single_notebook('path/to/notebook.ipynb')
    ```

=== "With Custom Output Path and File Copying"

    ```python
    from jupygrader import grade_single_notebook

    # Grade with custom output path and file copying
    item = {
        'notebook_path': 'path/to/notebook.ipynb',
        'output_path': 'path/to/output',
        'copy_files': ['data.csv']
    }

    graded_result = grade_single_notebook(item)
    ```

## 📒 Create an autogradable notebook

The instructor authors only one "solution" notebook, which contains both the solution code and test cases for all graded parts.

### Code cell for learners

Any code between `# YOUR CODE BEGINS` and `# YOUR CODE ENDS` are stripped in the student version.

```python
import pandas as pd

# YOUR CODE BEGINS
sample_series = pd.Series([-20, -10, 10, 20])
# YOUR CODE ENDS

print(sample_series)
```

nbgrader syntax (`### BEGIN SOLUTION`, `### END SOLUTION`) is also supported.

```python
import pandas as pd

### BEGIN SOLUTION
sample_series = pd.Series([-20, -10, 10, 20])
### END SOLUTION

print(sample_series)
```

In the student-facing notebook, the code cell will look like:

```python
import pandas as pd

# YOUR CODE BEGINS

# YOUR CODE ENDS

print(sample_series)
```

### Graded test cases

A graded test case requires a test case name and an assigned point value.

- The `_test_case` variable should store the name of the test case.
- The `_points` variable should store the number of points, either as an integer or a float.

```python
_test_case = 'create-a-pandas-series'
_points = 2

pd.testing.assert_series_equal(sample_series, pd.Series([-20, -10, 10, 20]))
```

### Obfuscate test cases (Work-in-progress)

If you want to prevent learners from seeing the test case code, you can optionally set `_obfuscate = True` to base64-encode the test cases.

!!! warning

    This provides only basic obfuscation, and students with technical knowledge can easily decode the string to reveal the original code. Supporting a password-based encryption method is planned for future releases.

**Instructor notebook**

```python
_test_case = 'create-a-pandas-series'
_points = 2
_obfuscate = True

pd.testing.assert_series_equal(sample_series, pd.Series([-20, -10, 10, 20]))
```

**Student notebook**

```python
# DO NOT CHANGE THE CODE IN THIS CELL
_test_case = 'create-a-pandas-series'
_points = 2
_obfuscate = True

import base64 as _b64
_64 = _b64.b64decode('cGQudGVzdGluZy5hc3NlcnRfc2VyaWVzX2VxdWFsKHNhbXBsZV9zZXJpZXMsIHBkLlNlcmllcyhbLT\
IwLCAtMTAsIDEwLCAyMF0pKQ==')
eval(compile(_64, '<string>', 'exec'))
```

### Add hidden test cases

Hidden test cases only run while grading.

#### Original test case

```python
_test_case = 'create-a-pandas-series'
_points = 2

### BEGIN HIDDEN TESTS
pd.testing.assert_series_equal(sample_series, pd.Series([-20, -10, 10, 20]))
### END HIDDEN TESTS
```
