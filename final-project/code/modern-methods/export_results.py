"""Export the selected BERTopic results without fitting or loading a model."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from shared.corpus import corpus_hash, digest, load_corpus, write_json
from shared.evaluation import aligned_assignments
from src import artifacts


README = """# Modern (BERTopic) results

These generated snapshots contain the selected BERTopic run, `{run_id}`.
The source runs, selection, and editable labels remain under `modern/`.

Refresh from the repository root without refitting or loading models:

```sh
uv run python final-project/code/modern-methods/export_results.py
```

Notebook 03 also refreshes these files after preparing selected-model summaries.
Run notebooks 02 and 03 first if the selected run's required summaries are missing.

| File | Contents |
| --- | --- |
| `assignments.csv` | One row per article: article ID, model, run, topic, and membership strength. |
| `terms.csv` | Ranked terms and weights from the selected run. |
| `topics.csv` | Topic ID, confirmed label (otherwise keywords), and article count. |
| `topic_labels.csv` | Snapshot of proposals, evidence, and confirmation status. |
| `representative_ids.csv` | Up to three centroid-nearest nonreserved examples per topic, with titles and publications. |
| `representatives.csv` | The same examples with full corpus text; generated locally and ignored by Git. |
| `stability.csv` | Seed 7 and 21 comparisons: ARI, evaluated coverage, and outlier agreement. |
| `coherence.csv` | Per-topic coherence and vocabulary coverage. |
| `topic_inventory.csv` | Counts, prevalence, keywords, current labels/status, coherence, and example IDs. |
| `publication_counts.csv` | Article counts for every publication and topic. |
| `publication_proportions.csv` | Shares of all articles in each publication, including unassigned articles. |
| `publication_sample_sizes.csv` | Total articles per publication. |
| `manifest.json` | Selected run, corpus and run identity, parameters, metrics, environment, and source/output hashes. |

Edit labels in `modern/selected/{run_id}/topic_labels.csv`, then refresh this export.
Changes to these snapshots are overwritten. Only team-confirmed labels replace
keyword labels. Topic `-1` means **Unassigned**, not a substantive topic.

There is no `mixtures.csv`: this configuration uses `calculate_probabilities=False`.
Membership strength is the existing clustering strength, not an LDA topic mixture.
Seed ARI covers articles assigned in both runs; retain its evaluated count and fraction.
Representatives are development examples and exclude the reserved review sample.
The export preserves source artifacts and does not change comparison inputs.
"""


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def export_results(root=ROOT, corpus_dir=None):
    """Validate saved inputs, then refresh root/Results; return its path.

    root and corpus_dir allow isolated fixtures. All validation and rendering
    finish in a temporary directory before any consolidated file is replaced.
    """
    root = Path(root)
    out = root / "Results"
    source = out / "modern"
    corpus_dir = Path(corpus_dir) if corpus_dir is not None else root.parents[1] / "data"
    df = load_corpus(corpus_dir)
    selection = json.loads((source / "selection.json").read_text())
    run_id = str(selection.get("run_id", "")).strip()
    _require(bool(run_id), "No modern run selected: fill Results/modern/selection.json first")
    _require(Path(run_id).name == run_id and run_id not in {".", ".."}, "Invalid selected run ID")
    experiments = pd.read_csv(source / "experiments.csv")
    _require(run_id in set(experiments.run_id), "Selected run is absent from experiments.csv")
    _require(selection.get("corpus_hash") == corpus_hash(df), "Selection/corpus mismatch")
    _require(all(str(selection.get(k, "")).strip() for k in ["rationale", "selected_by"]),
             "Selection requires rationale and selected_by")
    folder = source / "runs" / run_id
    selected = source / "selected" / run_id
    manifest = json.loads((folder / "manifest.json").read_text())
    identity = manifest["identity"]
    reservation = json.loads((source / "review_sample.json").read_text())
    _require(identity["corpus_hash"] == corpus_hash(df) == manifest["corpus_hash"],
             "Run/corpus mismatch")
    _require(reservation["corpus_hash"] == corpus_hash(df)
             and identity["reservation_hash"] == digest(reservation), "Review reservation mismatch")
    _require(manifest["metrics"]["run_id"] == run_id and identity["parameters"]["seed"] == 42,
             "Selection must identify the completed seed-42 run")

    # Only consumed CSVs are required: a checkout need not contain model.pkl.
    run_files = ["assignments.csv", "terms.csv", "topics.csv", "representative_ids.csv", "coherence.csv"]
    for name in run_files:
        _require(_sha(folder / name) == manifest["files"].get(name),
                 f"Missing or changed run artifact: {folder / name}")
    binding = dict(run_id=run_id, corpus_hash=corpus_hash(df), run_identity_hash=digest(identity))
    _require(json.loads((selected / "labels_identity.json").read_text()) == binding,
             "Labels belong to a different selected run")

    assignments = pd.read_csv(folder / "assignments.csv", dtype={"article_id": str})
    aligned = aligned_assignments(df, assignments)
    _require(assignments.model.eq("bertopic").all() and assignments.run_id.eq(run_id).all(),
             "Assignments identify a different model or run")
    _require(assignments.topic_id.ge(-1).all() and assignments.topic_id.mod(1).eq(0).all(),
             "Invalid assignment topic IDs")
    _require(np.isfinite(assignments.membership_strength).all()
             and assignments.membership_strength.between(0, 1).all(), "Invalid membership strengths")
    topics = pd.read_csv(folder / "topics.csv")
    _require(topics.topic_id.is_unique and set(topics.topic_id) == set(assignments.topic_id),
             "Topic IDs do not match assignments")
    counts = assignments.topic_id.value_counts().reindex(topics.topic_id)
    _require(np.array_equal(topics["count"].to_numpy(), counts.to_numpy()),
             "Topic counts do not match assignments")

    reps = pd.read_csv(folder / "representative_ids.csv", dtype={"article_id": str})
    reserved = set(map(str, reservation["article_ids"]))
    _require(reserved.issubset(set(df.article_id)), "Review reservation contains unknown articles")
    _require(not (set(reps.article_id) & reserved), "Representatives include reserved review articles")
    _require(reps.article_id.is_unique and set(reps.article_id).issubset(set(df.article_id)),
             "Representative article IDs are invalid")
    _require(reps.topic_id.ge(0).all()
             and np.array_equal(reps.topic_id, reps.article_id.map(assignments.set_index("article_id").topic_id)),
             "Representatives do not belong to their topics")
    available = assignments.loc[~assignments.article_id.isin(reserved) & assignments.topic_id.ge(0)]
    expected_counts = available.topic_id.value_counts().clip(upper=3).sort_index()
    _require(reps.groupby("topic_id").size().equals(expected_counts), "Incomplete representative examples")
    representatives = reps[["topic_id", "rank", "article_id"]].merge(
        df[["article_id", "title", "publication", "text"]], on="article_id", validate="one_to_one")
    for column in ["title", "publication"]:
        _require(reps[column].fillna("").tolist() == representatives[column].fillna("").tolist(),
                 f"Representative {column} does not match corpus")

    stability = pd.read_csv(selected / "stability.csv")
    _require(len(stability) == 2 and set(stability.seed) == {7, 21},
             "Seed stability requires comparisons with seeds 7 and 21")
    publication_files = ["publication_counts.csv", "publication_proportions.csv", "publication_sample_sizes.csv"]
    pub_counts = pd.crosstab(df.publication, aligned.topic_id)
    pub_counts[-1] = pub_counts.get(-1, 0)
    pub_counts = pub_counts.sort_index(axis=1)
    pub_counts.columns = pub_counts.columns.astype(str)
    expected_tables = [pub_counts, pub_counts.div(pub_counts.sum(axis=1), axis=0),
                       pub_counts.sum(axis=1).rename("article_count").to_frame()]
    for name, expected in zip(publication_files, expected_tables):
        actual = pd.read_csv(selected / name, index_col="publication")
        try:
            pd.testing.assert_frame_equal(actual, expected, check_dtype=False, check_names=False)
        except AssertionError as error:
            raise ValueError(f"Publication summary does not match assignments: {name}") from error

    source_paths = [source / n for n in ["selection.json", "experiments.csv", "review_sample.json"]]
    source_paths += [folder / n for n in ["manifest.json", *run_files]]
    source_paths += [selected / n for n in ["labels_identity.json", "topic_labels.csv", "stability.csv", *publication_files]]
    source_paths += [corpus_dir / n for n in ["corpus.csv", "corpus_manifest.json"]]
    # Corpus paths are relative to root as well, so provenance is portable.
    sources = {os.path.relpath(p, root): _sha(p) for p in source_paths}
    with tempfile.TemporaryDirectory(prefix=".export-", dir=out) as temp:
        stage = Path(temp)
        for name in ["assignments.csv", "terms.csv", "coherence.csv", "representative_ids.csv"]:
            (stage / name).write_bytes((folder / name).read_bytes())
        for name in ["topic_labels.csv", "stability.csv", *publication_files]:
            (stage / name).write_bytes((selected / name).read_bytes())
        # Reuse existing label validation against staged copies, preserving edits at source.
        write_json(stage / "labels_identity.json", binding)
        labels = artifacts.labels_table(folder, stage, binding)
        (stage / "labels_identity.json").unlink()
        inventory = artifacts.topic_inventory(folder, stage, len(df), labels)
        inventory[["topic_id", "label", "count"]].to_csv(stage / "topics.csv", index=False)
        representatives.to_csv(stage / "representatives.csv", index=False)
        (stage / "README.md").write_text(README.format(run_id=run_id))
        write_json(stage / "manifest.json", dict(
            model="bertopic", run_id=run_id, corpus_hash=corpus_hash(df), selection=selection,
            identity=identity, parameters=identity["parameters"], metrics=manifest["metrics"],
            environment=manifest["environment"], source_files=sources,
            files={p.name: _sha(p) for p in sorted(stage.iterdir())},
        ))
        _require(all(_sha(root / name) == checksum for name, checksum in sources.items()),
                 "Source artifacts changed during export; retry with stable inputs")
        for path in sorted(stage.iterdir(), key=lambda p: (p.name == "manifest.json", p.name)):
            path.replace(out / path.name)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        out = export_results()
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"Cannot export modern results: {error}\n")
    print(f"Exported selected modern results to {out}")


if __name__ == "__main__":
    main()
