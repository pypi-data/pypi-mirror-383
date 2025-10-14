from jupygrader import grade_notebooks
from pathlib import Path
import shutil

TEST_NOTEBOOKS_DIR = Path(__file__).resolve().parent / "test-files"
SAMPLE_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "sample-graded-results"

# Create the output directory if it doesn't exist
SAMPLE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Generate sample outputs for documentation
def test_generate_sample_outputs_01():
    notebook_path = (
        TEST_NOTEBOOKS_DIR / "sample-notebooks" / "sample-submission-01.ipynb"
    )

    shutil.copy2(
        notebook_path,
        SAMPLE_OUTPUT_DIR / "sample-submission-01.ipynb",
    )

    grade_notebooks(
        [
            {
                "notebook_path": notebook_path,
                "output_path": SAMPLE_OUTPUT_DIR,
            }
        ],
        csv_output_path=SAMPLE_OUTPUT_DIR / "sample-graded-results.csv",
        regrade_existing=True,
    )
