"""Frozen article review packets and paired ordinal agreement; no generated ratings."""

from pathlib import Path
import json
import numpy as np
import pandas as pd
from .corpus import SEED, corpus_hash, digest, write_json

KEYS = ["article_id", "model", "run_id"]
IDENTITY = KEYS + ["topic_id", "label", "title"]
RUBRIC = """Two reviewers work independently before discussing disagreements.
Rate how well the assigned topic label describes the article:
1 = unrelated/misleading; 2 = weak or incidental fit; 3 = partial/mixed fit;
4 = good fit with minor omissions; 5 = clear central-theme fit.
Set irrelevant and ambiguous_label to true or false and add evidence notes.
For topic -1, leave fit_rating blank; review relevance/ambiguity qualitatively.
Membership strengths are not calibrated probabilities. Do not infer a rating from them.
The reserved sample is independent of development review, not held out from fitting.
"""


def review_packets(
    df, modern, classical, out, labels, article_ids=None, reservation=None
):
    """Optional IDs retain legacy API compatibility; project notebooks always supply a reservation."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    frames = [modern] + ([classical] if classical is not None else [])
    ids = (
        list(article_ids)
        if article_ids is not None
        else df.sample(min(100, len(df)), random_state=SEED).article_id.tolist()
    )
    if len(ids) != len(set(ids)) or not set(ids).issubset(df.article_id):
        raise ValueError("Invalid reserved review IDs")
    if reservation is not None:
        if (
            reservation["corpus_hash"] != corpus_hash(df)
            or reservation["article_ids"] != ids
        ):
            raise ValueError("Reservation does not match corpus or review IDs")
    for assignments in frames:
        if (
            assignments.article_id.duplicated().any()
            or set(assignments.article_id) != set(df.article_id)
            or assignments.model.nunique() != 1
            or assignments.run_id.nunique() != 1
        ):
            raise ValueError("Review assignments must describe one complete model run")
    lookup = df.set_index("article_id")
    indexed = [frame.set_index("article_id") for frame in frames]
    records = []
    rng = np.random.default_rng(SEED)
    for article in ids:
        row = lookup.loc[article]
        for index in rng.permutation(len(frames)):
            assignment = indexed[index].loc[article]
            topic, model = int(assignment.topic_id), str(assignment.model)
            label = "Unassigned" if topic == -1 else labels.get((model, topic), "")
            if not isinstance(label, str) or not label.strip():
                raise ValueError(
                    "Confirm every topic label before generating review packets"
                )
            records.append(
                dict(
                    article_id=article,
                    model=model,
                    run_id=str(assignment.run_id),
                    topic_id=topic,
                    label=label,
                    title=row.title,
                    text=row.text,
                )
            )
    packet = pd.DataFrame(records)
    freeze_record = dict(
        packet_hash=digest(packet.to_dict("records")),
        corpus_hash=corpus_hash(df),
        reservation_hash=digest(reservation) if reservation is not None else None,
    )
    freeze = out / "review_freeze.json"
    if freeze.exists() and json.loads(freeze.read_text()) != freeze_record:
        raise ValueError(
            "Review models, corpus, reservation or labels changed; preserve the old review"
        )
    write_json(freeze, freeze_record)
    packet.to_csv(out / "review_packet.csv", index=False)
    for reviewer in ["reviewer_1", "reviewer_2"]:
        path = out / f"{reviewer}.csv"
        if not path.exists():
            packet.drop(columns="text").assign(
                fit_rating="", irrelevant="", ambiguous_label="", notes=""
            ).to_csv(path, index=False)
    outliers = modern.loc[modern.topic_id.eq(-1), "article_id"]
    selected = outliers.sample(min(20, len(outliers)), random_state=SEED)
    if not (out / "outlier_review.csv").exists():
        df.loc[df.article_id.isin(selected), ["article_id", "title", "text"]].assign(
            relevance="", notes=""
        ).to_csv(out / "outlier_review.csv", index=False)
    (out / "rubric.txt").write_text(RUBRIC)
    write_json(
        out / "review_status.json",
        dict(
            joint_comparison_ready=classical is not None,
            sampled_articles=len(ids),
            modern_unassigned_in_sample=int(
                packet.query("model == 'bertopic' and topic_id == -1").shape[0]
            ),
            instructions=RUBRIC,
        ),
    )
    return packet


def quadratic_kappa(a, b):
    """Quadratic weighted Cohen kappa on the fixed 1–5 scale; undefined when expected disagreement is zero."""
    if not len(a):
        return np.nan
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    expected = np.mean(a * a) + np.mean(b * b) - 2 * np.mean(a) * np.mean(b)
    return float(1 - np.mean((a - b) ** 2) / expected) if expected > 0 else np.nan


def summarize_reviews(out, bootstrap_samples=1000, seed=SEED):
    out = Path(out)
    packet = pd.read_csv(
        out / "review_packet.csv",
        dtype={"article_id": str, "run_id": str},
        keep_default_na=False,
    )
    freeze = json.loads((out / "review_freeze.json").read_text())
    if digest(packet.to_dict("records")) != freeze["packet_hash"]:
        raise ValueError("Frozen review packet changed")
    expected = packet.set_index(KEYS)[["topic_id", "label", "title"]].sort_index()
    reviews = []
    pending = False
    for reviewer in ["reviewer_1", "reviewer_2"]:
        frame = pd.read_csv(
            out / f"{reviewer}.csv",
            dtype={"article_id": str, "run_id": str},
            keep_default_na=False,
        )
        if not set(IDENTITY + ["fit_rating", "irrelevant", "ambiguous_label"]).issubset(
            frame.columns
        ):
            raise ValueError("Review columns are missing")
        if frame.duplicated(KEYS).any():
            raise ValueError("Duplicate reviewer rows")
        identity = frame.set_index(KEYS)[["topic_id", "label", "title"]].sort_index()
        if not identity.equals(expected):
            raise ValueError(
                "Reviewer roster, topics, or labels differ from the frozen packet"
            )
        raw = frame.fit_rating.astype(str).str.strip()
        assigned = frame.topic_id.ge(0)
        if raw.loc[~assigned].ne("").any():
            raise ValueError("Outlier fit ratings must remain blank")
        provided = raw.ne("")
        ratings = pd.to_numeric(raw.where(provided), errors="raise")
        if not (ratings[provided].between(1, 5) & ratings[provided].mod(1).eq(0)).all():
            raise ValueError("Fit ratings must be integers from 1 to 5")
        pending |= bool(raw[assigned].eq("").any())
        frame["fit_rating"] = ratings
        for flag in ["irrelevant", "ambiguous_label"]:
            values = frame[flag].astype(str).str.lower().str.strip()
            if not values.isin(["true", "false", ""]).all():
                raise ValueError("Review flags must be true or false")
            pending |= bool(values.eq("").any())
        reviews.append(frame)
    if pending:
        # Do not leave an old completed summary beside newly incomplete inputs.
        for filename in [
            "human_evaluation.csv",
            "rating_distributions.csv",
            "review_examples.csv",
        ]:
            (out / filename).unlink(missing_ok=True)
        return "Human evaluation pending: complete both independent reviewer files."
    joined = reviews[0].merge(
        reviews[1], on=KEYS, validate="one_to_one", suffixes=("_1", "_2")
    )
    rng = np.random.default_rng(seed)
    result = []
    for model, group in joined.groupby("model"):
        scored = group.loc[group.topic_id_1.ge(0)]
        a, b = scored.fit_rating_1.to_numpy(float), scored.fit_rating_2.to_numpy(float)
        boots = []
        if len(a):
            for _ in range(bootstrap_samples):
                sample = rng.integers(0, len(a), len(a))
                boots.append(quadratic_kappa(a[sample], b[sample]))
        valid = np.asarray(boots)[np.isfinite(boots)]
        low, high = (
            np.quantile(valid, [0.025, 0.975]) if len(valid) else (np.nan, np.nan)
        )
        kappa = quadratic_kappa(a, b)
        result.append(
            dict(
                model=model,
                sample_articles=len(group),
                rated_articles=len(scored),
                unassigned_articles=len(group) - len(scored),
                mean_1=float(np.mean(a)) if len(a) else np.nan,
                mean_2=float(np.mean(b)) if len(b) else np.nan,
                exact_agreement=float(np.mean(a == b)) if len(a) else np.nan,
                within_one_agreement=(
                    float(np.mean(np.abs(a - b) <= 1)) if len(a) else np.nan
                ),
                weighted_kappa=kappa,
                kappa_status=(
                    "ok"
                    if np.isfinite(kappa)
                    else "undefined: no ratings or zero expected disagreement"
                ),
                kappa_ci_low=low,
                kappa_ci_high=high,
                bootstrap_samples=bootstrap_samples,
                valid_bootstrap_samples=len(valid),
            )
        )
    summary = pd.DataFrame(result)
    summary.to_csv(out / "human_evaluation.csv", index=False)
    pd.concat([r.assign(reviewer=i + 1) for i, r in enumerate(reviews)]).loc[
        lambda x: x.topic_id.ge(0)
    ].groupby(["model", "reviewer", "fit_rating"]).size().to_csv(
        out / "rating_distributions.csv"
    )
    joined.to_csv(out / "review_examples.csv", index=False)
    return summary
