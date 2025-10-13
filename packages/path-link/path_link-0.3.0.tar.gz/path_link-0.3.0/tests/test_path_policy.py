from pathlib import Path
import re

# This test enforces the policy that all path manipulations outside of the
# `project_paths` package itself must go through the `ProjectPaths` object.
# This prevents direct usage of `os.path` or `pathlib.Path`, ensuring
# that all paths are managed and validated by the central system.

FORBIDDEN = [
    r"os\.path\.",  # e.g., os.path.join(...)
    r"pathlib\.Path\(",  # e.g., pathlib.Path(...)
    r"(?<!\.)Path\(",  # e.g., Path(...) after `from pathlib import Path`
    r"(?<!\.)ProjectPaths\s*\(",  # e.g., ProjectPaths() - forbidden in v2
]

# The `path_link` package is allowed to use these, as it's the implementation.
ALLOWED_PACKAGE_DIR = Path("src/path_link").resolve()
# Examples demonstrate proper usage, so they're exempt from policy
ALLOWED_EXAMPLES_DIR = Path("examples").resolve()


def test_no_direct_path_usage_policy():
    """
    Scans the source code to ensure forbidden path patterns are not used
    outside of the core `path_link` package.
    """
    src_dir = Path("src")
    assert src_dir.is_dir(), "The `src` directory must exist for this test to run."

    python_files = [p for p in src_dir.rglob("*.py") if p.is_file()]
    assert python_files, "No python files found in `src` to check."

    violations = []

    for file_path in python_files:
        # The policy does not apply to the implementation of path_link itself
        if file_path.resolve().is_relative_to(ALLOWED_PACKAGE_DIR):
            continue
        # Examples demonstrate proper usage, so they're exempt from policy
        if ALLOWED_EXAMPLES_DIR.exists() and file_path.resolve().is_relative_to(ALLOWED_EXAMPLES_DIR):
            continue

        text = file_path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN:
            if re.search(pattern, text):
                # A simple check to avoid flagging the import statement itself.
                # This is not perfect but avoids most false positives.
                lines_with_issue = [
                    line
                    for line in text.splitlines()
                    if re.search(pattern, line)
                    and not line.strip().startswith(("from ", "import "))
                ]
                if lines_with_issue:
                    violations.append(
                        f"- File '{file_path}' violates path policy with pattern '{pattern}' on lines: {lines_with_issue}"
                    )

    assert not violations, (
        "Project path policy violated. The following files use direct path manipulation instead of the ProjectPaths object:\n"
        + "\n".join(violations)
    )
