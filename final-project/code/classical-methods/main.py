"""Run the classical notebook workflow in fresh kernels from any working directory."""
from pathlib import Path
import subprocess
import sys

if __name__ == '__main__':
    verifier = Path(__file__).resolve().parents[1]/'modern-methods/verify_notebooks.py'
    raise SystemExit(subprocess.call([
        sys.executable, str(verifier), '--execute', 'classical_01', 'classical_02',
        'classical_03', '--timeout', '86400', *sys.argv[1:]
    ]))
