"""Compatibility entry point: execute notebook 01, including the review reservation."""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    subprocess.run(
        [
            sys.executable,
            str(Path(__file__).with_name("verify_notebooks.py")),
            "--execute",
            "01",
        ],
        check=True,
    )
