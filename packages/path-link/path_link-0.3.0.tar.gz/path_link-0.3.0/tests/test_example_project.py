import subprocess
import sys
from pathlib import Path


def test_minimal_project_runs_successfully():
    """
    Runs the baked-in minimal example project as a subprocess to verify
    that the editable install works and the core functionality is intact.
    This acts as an end-to-end smoke test.
    """
    # Get the root of the main project repository
    repo_root = Path(__file__).resolve().parent.parent
    # Get the path to the example project directory
    example_dir = repo_root / "examples" / "minimal_project"

    assert example_dir.is_dir(), f"Example project directory not found at {example_dir}"

    # Run the example's main.py using the same Python interpreter that is running the tests.
    # This ensures it runs within the same virtual environment.
    result = subprocess.run(
        [sys.executable, "src/main.py"],
        cwd=example_dir,
        text=True,
        capture_output=True,
        timeout=15,
    )

    # Print the output for debugging in case of failure
    print("Example project stdout:", result.stdout)
    print("Example project stderr:", result.stderr)

    # Assert that the script ran successfully
    assert result.returncode == 0, (
        f"Example project failed to run. Stderr: {result.stderr}"
    )

    # Assert that the output contains the expected success messages
    assert "PTOOL initialized" in result.stdout
    assert "Resolved paths" in result.stdout
    assert "data_dir" in result.stdout, (
        "Expected 'data_dir' to be in the resolved paths."
    )
