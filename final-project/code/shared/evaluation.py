"""Shared evaluation vocabulary, metrics, and joint comparison; imports are lazy."""

from pathlib import Path
import json, re
import numpy as np
import pandas as pd
from .corpus import SEED, write_json, digest, corpus_hash


def representation_text(text):
    # Match BERTopic's English keyword preprocessing before fitting a fixed vocabulary.
    return (
        re.sub(r"[^A-Za-z0-9 ]+", "", text.replace("\n", " ").replace("\t", " "))
        or "emptydoc"
    )


def analyzer():
    # Lowercase word tokens without English stopwords; shared by coherence and classical preprocessing.
    from sklearn.feature_extraction.text import CountVectorizer

    return CountVectorizer(stop_words="english").build_analyzer()


def reference_texts(df):
    from gensim.corpora import Dictionary

    tokenizer = analyzer()
    texts = [tokenizer(representation_text(t)) for t in df.text]
    return texts, Dictionary(texts)


def coherence(terms, texts, dictionary):
    from gensim.models import CoherenceModel

    groups = []
    for t, g in terms[terms.topic_id.ge(0)].groupby("topic_id"):
        words = g.sort_values("rank").term.head(10).tolist()
        known = [w for w in words if w in dictionary.token2id]
        groups.append((t, known, len(known) / len(words) if words else 0))
    valid = [g for g in groups if len(g[1]) >= 2]
    values = (
        CoherenceModel(
            topics=[g[1] for g in valid],
            texts=texts,
            dictionary=dictionary,
            coherence="c_v",
            window_size=110,
            processes=1,
        ).get_coherence_per_topic()
        if valid
        else []
    )
    scores = {g[0]: float(v) for g, v in zip(valid, values)}
    return pd.DataFrame(
        [
            dict(
                topic_id=t,
                coherence=scores.get(t, np.nan),
                vocabulary_coverage=coverage,
            )
            for t, words, coverage in groups
        ],
        columns=["topic_id", "coherence", "vocabulary_coverage"],
    )


def stability(a, b):
    from sklearn.metrics import adjusted_rand_score

    a = np.array(a)
    b = np.array(b)
    if a.shape != b.shape or a.ndim != 1 or not len(a):
        raise ValueError("Stability requires equal nonempty aligned assignment arrays")
    mask = (a >= 0) & (b >= 0)
    return dict(
        adjusted_rand_index=(
            float(adjusted_rand_score(a[mask], b[mask])) if mask.sum() > 1 else np.nan
        ),
        evaluated_count=int(mask.sum()),
        evaluated_fraction=float(mask.mean()),
        outlier_agreement=float(np.mean((a == -1) == (b == -1))),
    )


def jaccard_table(a, b):
    def sets(df):
        return {
            t: set(g.sort_values("rank").term.head(10))
            for t, g in df[df.topic_id.ge(0)].groupby("topic_id")
        }

    aa, bb = sets(a), sets(b)
    return pd.DataFrame(
        {
            j: {i: len(x & y) / len(x | y) if x | y else 0 for i, x in aa.items()}
            for j, y in bb.items()
        }
    )


def validate_classical(folder, ids):
    folder = Path(folder)
    a = pd.read_csv(folder / "assignments.csv", dtype={"article_id": str})
    terms = pd.read_csv(folder / "terms.csv")
    topics = pd.read_csv(folder / "topics.csv")
    required = {"article_id", "model", "run_id", "topic_id"}
    if (
        not required.issubset(a.columns)
        or not a.article_id.is_unique
        or set(a.article_id) != set(ids)
    ):
        raise ValueError(
            "Classical assignments must contain exactly one row per shared article"
        )
    if not {"topic_id", "rank", "term", "weight"}.issubset(terms.columns) or not {
        "topic_id",
        "label",
        "count",
    }.issubset(topics.columns):
        raise ValueError("Invalid classical terms/topics schema")
    if (
        a.topic_id.isna().any()
        or terms[["topic_id", "rank", "term"]].isna().any().any()
    ):
        raise ValueError("Missing topic IDs or terms")
    if not set(a.topic_id).issubset(set(topics.topic_id)):
        raise ValueError("Unknown classical topic")
    if (
        topics.topic_id.duplicated().any()
        or a.model.ne("lda").any()
        or a.run_id.nunique() != 1
    ):
        raise ValueError(
            "Classical topics must be unique and assignments must describe one LDA run"
        )
    if not set(terms.topic_id).issubset(set(topics.topic_id)):
        raise ValueError("Unknown topic in classical terms")
    actual = a.topic_id.value_counts().sort_index()
    declared = topics.set_index("topic_id")["count"].sort_index()
    if not actual.reindex(declared.index, fill_value=0).equals(declared):
        raise ValueError("Classical topic counts disagree")
    for frame in [a, terms, topics]:
        values = pd.to_numeric(frame.topic_id, errors="raise")
        if not values.mod(1).eq(0).all():
            raise ValueError("Topic IDs must be integers")
        frame["topic_id"] = values.astype(int)
    if not (
        pd.to_numeric(terms["rank"], errors="raise").gt(0)
        & pd.to_numeric(terms["rank"]).mod(1).eq(0)
    ).all():
        raise ValueError("Term ranks must be positive")
    if terms.duplicated(["topic_id", "rank"]).any():
        raise ValueError("Duplicate term ranks")
    if any(frame.topic_id.lt(0).any() for frame in [a, terms, topics]):
        raise ValueError("LDA cannot contain outlier topic IDs")
    if not np.isfinite(pd.to_numeric(terms.weight, errors="raise")).all():
        raise ValueError("Nonfinite term weights")
    for topic in topics.topic_id:
        ranks = terms.loc[terms.topic_id.eq(topic), "rank"].tolist()
        if not set(range(1, 11)).issubset(ranks):
            raise ValueError("Each classical topic requires ten ranked terms")
    return a.set_index("article_id").loc[list(ids)].reset_index(), terms, topics


def reserve_review_ids(df, path, exclusions=(), n=100, seed=SEED):
    """Reserve once before development; the sample is not a model-training holdout."""
    path = Path(path)
    excluded = sorted(set(map(str, exclusions)) & set(df.article_id))
    eligible = df.loc[~df.article_id.isin(excluded), "article_id"].tolist()
    if len(eligible) < n:
        raise ValueError("Too few eligible articles for the requested review sample")
    record = dict(
        corpus_hash=corpus_hash(df),
        seed=seed,
        sample_size=n,
        excluded_article_ids=excluded,
        eligible_article_ids=eligible,
        article_ids=pd.Series(eligible).sample(n, random_state=seed).tolist(),
    )
    if path.exists():
        if json.loads(path.read_text()) != record:
            raise ValueError(
                "Review reservation changed; preserve it and investigate the inputs"
            )
    else:
        write_json(path, record)
    return record


def aligned_assignments(df, assignments):
    if (
        not assignments.article_id.is_unique
        or set(assignments.article_id) != set(df.article_id)
        or assignments.topic_id.isna().any()
    ):
        raise ValueError("Assignments must cover exactly the corpus, once per article")
    return assignments.set_index("article_id").loc[df.article_id].reset_index()


def publication_exports(df, assignments, out, labels=None):
    """All outlets in CSVs; the main figure uses n>=50 and the 15 largest topics."""
    import matplotlib.pyplot as plt

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    assignments = aligned_assignments(df, assignments)
    joined = df[["article_id", "publication"]].merge(
        assignments, on="article_id", validate="one_to_one"
    )
    counts = pd.crosstab(joined.publication, joined.topic_id)
    counts[-1] = counts.get(-1, 0)
    counts = counts.sort_index(axis=1)
    proportions = counts.div(counts.sum(axis=1), axis=0)
    counts.to_csv(out / "publication_counts.csv")
    proportions.to_csv(out / "publication_proportions.csv")
    counts.sum(axis=1).rename("article_count").to_csv(
        out / "publication_sample_sizes.csv"
    )
    top = (
        counts.drop(columns=-1)
        .sum()
        .sort_values(ascending=False)
        .head(15)
        .index.tolist()
    )
    main = proportions.loc[counts.sum(axis=1).ge(50), top + [-1]]
    if not main.empty:
        fig, ax = plt.subplots(figsize=(12, 7))
        im = ax.imshow(main, aspect="auto", vmin=0)
        names = labels or {}
        ax.set_xticks(
            range(len(main.columns)),
            [
                f'{t}: {names.get(t, "Unassigned" if t == -1 else str(t))}'
                for t in main.columns
            ],
            rotation=60,
            ha="right",
            fontsize=8,
        )
        ax.set_yticks(
            range(len(main)), [f"{p} (n={counts.loc[p].sum():,})" for p in main.index]
        )
        ax.set_title("Within-publication topic shares; 15 largest topics + unassigned")
        fig.colorbar(im, ax=ax, label="Share of all articles in publication")
        fig.tight_layout()
        for suffix in ["png", "pdf"]:
            fig.savefig(out / f"publication_proportions.{suffix}", dpi=180)
        plt.close(fig)
    return counts, proportions


def seed_publication_comparison(df, baseline, other, out):
    """One-to-one maximum overlap for summaries; retain all overlaps for split/merge inspection."""
    from scipy.optimize import linear_sum_assignment

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    a = aligned_assignments(df, baseline).topic_id.to_numpy()
    b = aligned_assignments(df, other).topic_id.to_numpy()
    both = (a >= 0) & (b >= 0)
    rows = sorted(set(a) - {-1})
    cols = sorted(set(b) - {-1})
    matrix = pd.crosstab(a[both], b[both]).reindex(
        index=rows, columns=cols, fill_value=0
    )
    matrix.to_csv(out / "topic_overlap_counts.csv")
    matches = []
    if rows and cols:
        rr, cc = linear_sum_assignment(-matrix.to_numpy())
        for i, j in zip(rr, cc):
            overlap = int(matrix.iloc[i, j])
            if overlap:
                matches.append(
                    dict(baseline_topic=rows[i], other_topic=cols[j], overlap=overlap)
                )
    matching = pd.DataFrame(
        matches, columns=["baseline_topic", "other_topic", "overlap"]
    )
    matching.to_csv(out / "topic_matches.csv", index=False)
    changes = []
    for r in matching.itertuples():
        for publication, positions in (
            df.reset_index(drop=True).groupby("publication").groups.items()
        ):
            av, bv = a[list(positions)], b[list(positions)]
            ap, bp = float(np.mean(av == r.baseline_topic)), float(
                np.mean(bv == r.other_topic)
            )
            changes.append(
                dict(
                    publication=publication,
                    article_count=len(positions),
                    baseline_topic=r.baseline_topic,
                    other_topic=r.other_topic,
                    baseline_share=ap,
                    other_share=bp,
                    difference=bp - ap,
                )
            )
    pd.DataFrame(
        changes,
        columns=[
            "publication",
            "article_count",
            "baseline_topic",
            "other_topic",
            "baseline_share",
            "other_share",
            "difference",
        ],
    ).to_csv(out / "publication_changes.csv", index=False)
    edges = []
    for a_id in rows:
        for b_id in cols:
            count = int(matrix.loc[a_id, b_id])
            if count:
                edges.append(
                    dict(
                        baseline_topic=a_id,
                        other_topic=b_id,
                        overlap=count,
                        baseline_fraction=count / int(np.sum(a == a_id)),
                        other_fraction=count / int(np.sum(b == b_id)),
                    )
                )
    pd.DataFrame(edges).to_csv(out / "split_merge_edges.csv", index=False)
    summary = dict(
        **stability(a, b),
        unmatched_baseline_topics=sorted(set(rows) - set(matching.baseline_topic)),
        unmatched_other_topics=sorted(set(cols) - set(matching.other_topic)),
        split_candidates=[
            t
            for t in rows
            if sum(
                e["baseline_topic"] == t and e["baseline_fraction"] >= 0.1
                for e in edges
            )
            > 1
        ],
        merge_candidates=[
            t
            for t in cols
            if sum(e["other_topic"] == t and e["other_fraction"] >= 0.1 for e in edges)
            > 1
        ],
        split_merge_threshold="At least two overlaps each covering >=10% of the source/target topic; descriptive flag only",
    )
    write_json(out / "summary.json", summary)
    return summary


# Keep these imports available to existing callers of shared.evaluation.
from .human_review import review_packets, summarize_reviews
