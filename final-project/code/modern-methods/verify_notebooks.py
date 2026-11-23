"""Validate notebooks or execute them in fresh kernels; never run only an unreported prefix."""

import argparse
from pathlib import Path
import nbformat
from nbclient import NotebookClient


def main():
    root = Path(__file__).resolve().parent
    review_root = root.parent / "human-review"
    notebooks = {
        "01": root / "notebooks/01_corpus_and_embeddings.ipynb",
        "02": root / "notebooks/02_modern_topic_modeling.ipynb",
        "03": root / "notebooks/03_evaluation_and_comparison.ipynb",
        "comparison": root.parent / "comparison/pipeline_comparison.ipynb",
        "coordinator": review_root / "review_coordinator.ipynb",
        "reviewer_1": review_root / "reviewer_1.ipynb",
        "reviewer_2": review_root / "reviewer_2.ipynb",
        "classical_01": root.parent / "classical-methods/notebooks/01_corpus_and_representation.ipynb",
        "classical_02": root.parent / "classical-methods/notebooks/02_classical_topic_modeling.ipynb",
        "classical_03": root.parent / "classical-methods/notebooks/03_classical_results_and_exports.ipynb",
    }
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute",
        nargs="+",
        choices=list(notebooks) + ["04"],
        default=[],
        help="Notebook selector; 04 remains an alias for coordinator.",
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
    selected = {"coordinator" if name == "04" else name for name in args.execute}
    for name, path in notebooks.items():
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        for cell in notebook.cells:
            if cell.cell_type == "code":
                compile(cell.source, str(path), "exec")
        if name not in selected:
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
            resources={"metadata": {"path": str(path.parent)}},
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
