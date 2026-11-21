"""Compatibility entry point: execute notebook 02 without a second implementation."""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    subprocess.run(
        [
            sys.executable,
            str(Path(__file__).with_name("verify_notebooks.py")),
            "--execute",
            "02",
        ],
        check=True,
    )
