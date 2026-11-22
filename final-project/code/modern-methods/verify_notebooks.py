"""Validate notebooks or execute them in fresh kernels; never run only an unreported prefix."""

import argparse
from pathlib import Path
import nbformat
from nbclient import NotebookClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute", nargs="+", choices=["01", "02", "03", "04"], default=[]
    )
    parser.add_argument(
        "--skip-embeddings",
        action="store_true",
        help="Only for notebook 01 audit checks; reports skipped cells",
    )
    parser.add_argument(
        "--timeout", type=int, default=1800, help="Per-cell timeout in seconds"
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    for path in sorted((root / "notebooks").glob("*.ipynb")):
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        for cell in notebook.cells:
            if cell.cell_type == "code":
                compile(cell.source, str(path), "exec")
        if path.name[:2] not in args.execute:
            print("Validated:", path.name, flush=True)
            continue
        # A failed or partial run must not retain results from unexecuted old cells.
        for cell in notebook.cells:
            if cell.cell_type == "code":
                cell.outputs = []
                cell.execution_count = None
        if args.skip_embeddings:
            for cell in notebook.cells:
                if "embedding" in cell.metadata.get("tags", []):
                    cell.metadata.setdefault("tags", []).append("skip-execution")
        print("Executing fresh kernel:", path.name, flush=True)
        client = NotebookClient(
            notebook,
            timeout=args.timeout,
            kernel_name="python3",
            resources={"metadata": {"path": str(root)}},
            skip_cells_with_tag="skip-execution",
        )
        try:
            client.execute()
        finally:
            # Persist failure evidence too; never claim a successful run on exception.
            for cell in notebook.cells:
                if args.skip_embeddings and "skip-execution" in cell.metadata.get(
                    "tags", []
                ):
                    cell.metadata["tags"].remove("skip-execution")
            nbformat.write(notebook, path)
        print(
            "Executed:",
            path.name,
            "(embedding cells skipped)" if args.skip_embeddings else "",
            flush=True,
        )


if __name__ == "__main__":
    main()
