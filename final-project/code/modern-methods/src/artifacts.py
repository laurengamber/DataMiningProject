"""Small artifact helpers. Model construction and analysis stay in the notebooks."""

from pathlib import Path
import hashlib
import importlib.metadata as metadata
import json
import pickle
import platform
import sys
import numpy as np
import pandas as pd
from .topic_helpers import term_table
from shared.corpus import corpus_hash, digest, write_json
from shared.evaluation import aligned_assignments


def environment():
    return dict(
        platform=platform.platform(),
        machine=platform.machine(),
        processor=platform.processor(),
        python=sys.version,
        versions={
            name: metadata.version(name)
            for name in [
                "bertopic",
                "sentence-transformers",
                "umap-learn",
                "hdbscan",
                "scikit-learn",
                "gensim",
                "numpy",
                "pandas",
            ]
        },
    )


def array_hash(array):
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def run_identity(
    df, embeddings, parameters, vocabulary, implementation_hash, reservation
):
    return dict(
        corpus_hash=corpus_hash(df),
        embedding_hash=array_hash(embeddings),
        parameters=parameters,
        vocabulary_hash=digest(vocabulary),
        implementation_hash=implementation_hash,
        reservation_hash=digest(reservation),
        versions=environment()["versions"],
    )


def load_run(folder, expected=None):
    folder = Path(folder)
    manifest = json.loads((folder / "manifest.json").read_text())
    if expected is not None and manifest["identity"] != expected:
        raise ValueError(
            f"Stale run at {folder}; retain it separately before refitting"
        )
    for name, checksum in manifest["files"].items():
        path = folder / name
        if (
            not path.exists()
            or hashlib.sha256(path.read_bytes()).hexdigest() != checksum
        ):
            raise ValueError(f"Missing or changed run artifact: {path}")
    with (folder / "model.pkl").open("rb") as stream:
        model = pickle.load(
            stream
        )  # Only trusted artifacts generated locally by these notebooks.
    return model, manifest["metrics"]


def export_run(model, df, embeddings, folder, run_id, reserved_ids):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    assignments = pd.DataFrame(
        dict(
            article_id=df.article_id,
            model="bertopic",
            run_id=run_id,
            topic_id=model.topics_,
            membership_strength=model.probabilities_,
        )
    )
    aligned_assignments(df, assignments)
    assignments.to_csv(folder / "assignments.csv", index=False)
    term_table(model).to_csv(folder / "terms.csv", index=False)
    model.get_topic_info()[["Topic", "Count", "Name"]].rename(
        columns={"Topic": "topic_id", "Count": "count", "Name": "label"}
    ).to_csv(folder / "topics.csv", index=False)
    # Centroid-nearest development examples; never expose reserved review articles.
    evidence = []
    labels = np.asarray(model.topics_)
    for topic in sorted(set(labels) - {-1}):
        indices = np.flatnonzero(labels == topic)
        centroid = embeddings[indices].mean(axis=0)
        available = [i for i in indices if df.iloc[i].article_id not in reserved_ids]
        ordered = sorted(
            available,
            key=lambda i: (
                -float(embeddings[i] @ centroid),
                str(df.iloc[i].article_id),
            ),
        )[:3]
        for rank, i in enumerate(ordered, 1):
            row = df.iloc[i]
            evidence.append(
                dict(
                    topic_id=topic,
                    rank=rank,
                    article_id=row.article_id,
                    title=row.title,
                    publication=row.publication,
                    text=row.text,
                )
            )
    representatives = pd.DataFrame(
        evidence,
        columns=["topic_id", "rank", "article_id", "title", "publication", "text"],
    )
    representatives.to_csv(folder / "representatives.csv", index=False)
    representatives.drop(columns="text").to_csv(
        folder / "representative_ids.csv", index=False
    )
    with (folder / "model.pkl").open("wb") as stream:
        pickle.dump(model, stream)


def save_run_manifest(folder, identity, metrics):
    folder = Path(folder)
    names = [
        "assignments.csv",
        "terms.csv",
        "topics.csv",
        "representative_ids.csv",
        "coherence.csv",
        "model.pkl",
    ]
    files = {
        name: hashlib.sha256((folder / name).read_bytes()).hexdigest() for name in names
    }
    write_json(
        folder / "manifest.json",
        dict(
            identity=identity,
            corpus_hash=identity["corpus_hash"],
            metrics=metrics,
            environment=environment(),
            files=files,
        ),
    )


def selection_record(out, df, runs):
    path = Path(out) / "selection.json"
    if not path.exists():
        write_json(
            path,
            dict(corpus_hash=corpus_hash(df), run_id="", rationale="", selected_by=""),
        )
    record = json.loads(path.read_text())
    if record.get("corpus_hash") != corpus_hash(df):
        raise ValueError("Selection belongs to a different corpus")
    if not str(record.get("run_id", "")).strip():
        return None
    if record["run_id"] not in runs or any(
        not str(record.get(k, "")).strip() for k in ["rationale", "selected_by"]
    ):
        raise ValueError(
            "Choose a completed run and supply a rationale and team selector"
        )
    return record


def labels_table(folder, out, identity):
    """Editable table with an immutable companion identity; never overwrite manual work."""
    folder, out = Path(folder), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    binding = out / "labels_identity.json"
    if binding.exists() and json.loads(binding.read_text()) != identity:
        raise ValueError("Labels belong to a different selected run")
    path = out / "topic_labels.csv"
    if path.exists() and not binding.exists():
        raise ValueError("Existing labels lack a run identity")
    write_json(binding, identity)
    topics = pd.read_csv(folder / "topics.csv").query("topic_id >= 0")
    reps = pd.read_csv(folder / "representative_ids.csv", dtype={"article_id": str})
    if not path.exists():
        table = topics.rename(columns={"label": "keyword_label"})
        table["proposed_label"] = ""
        table["evidence_ids"] = table.topic_id.map(
            reps.groupby("topic_id").article_id.agg(" | ".join)
        ).fillna("")
        table["evidence_notes"] = ""
        table["confirmed"] = False
        table.to_csv(path, index=False)
    table = pd.read_csv(path, keep_default_na=False)
    if table.topic_id.duplicated().any() or set(table.topic_id) != set(topics.topic_id):
        raise ValueError("Label topic IDs do not match the selected model")
    if not table.confirmed.astype(str).str.lower().isin(["true", "false"]).all():
        raise ValueError("Label confirmation must be true or false")
    for row in table.itertuples():
        evidence = {v.strip() for v in str(row.evidence_ids).split("|") if v.strip()}
        valid = set(reps.loc[reps.topic_id.eq(row.topic_id), "article_id"])
        if not evidence.issubset(valid):
            raise ValueError(
                "Label evidence must use this topic’s nonreserved development representatives"
            )
        if str(row.confirmed).lower() == "true" and (
            not evidence
            or not str(row.proposed_label).strip()
            or not str(row.evidence_notes).strip()
        ):
            raise ValueError("Confirmed labels require a label and supporting evidence")
    return table


def topic_inventory(folder, out, n_articles, labels=None):
    folder, out = Path(folder), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    topics = pd.read_csv(folder / "topics.csv").rename(
        columns={"label": "keyword_label"}
    )
    terms = pd.read_csv(folder / "terms.csv")
    reps = pd.read_csv(folder / "representative_ids.csv", dtype={"article_id": str})
    topics["keywords"] = topics.topic_id.map(
        terms.sort_values("rank").groupby("topic_id").term.agg(", ".join)
    )
    topics["prevalence"] = topics["count"] / n_articles
    topics["representative_article_ids"] = topics.topic_id.map(
        reps.groupby("topic_id").article_id.agg(" | ".join)
    ).fillna("")
    topics = topics.merge(
        pd.read_csv(folder / "coherence.csv"),
        on="topic_id",
        how="left",
        validate="one_to_one",
    )
    topics["label"] = topics.keyword_label
    topics["label_status"] = "keywords only; team interpretation pending"
    if labels is not None:
        confirmed = labels.loc[
            labels.confirmed.astype(str).str.lower().eq("true")
        ].set_index("topic_id")
        mask = topics.topic_id.isin(confirmed.index)
        topics.loc[mask, "label"] = topics.loc[mask, "topic_id"].map(
            confirmed.proposed_label
        )
        topics.loc[mask, "label_status"] = "team confirmed"
    topics.loc[topics.topic_id.eq(-1), ["label", "label_status"]] = [
        "Unassigned",
        "not a topic",
    ]
    topics.to_csv(out / "topic_inventory.csv", index=False)
    return topics
