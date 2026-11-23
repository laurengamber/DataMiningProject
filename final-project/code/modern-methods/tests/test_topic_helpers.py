import json
import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from src import topic_helpers as h, artifacts as a
from shared import evaluation as ev
from shared.corpus import audit_corpus, load_corpus, corpus_hash
from shared.human_review import quadratic_kappa


class Tokenizer:
    def encode(self, text, add_special_tokens=False, **kwargs):
        return list(range(int(text)))

    def num_special_tokens_to_add(self, pair=False):
        return 2


def sample_frames():
    df = pd.DataFrame(
        {
            "article_id": ["a", "b", "c"],
            "text": ["car road", "law bill", "road policy"],
            "title": ["Car", "Law", "Both"],
            "publication": ["Outlet", "Outlet", "Other"],
        }
    )
    modern = pd.DataFrame(
        {
            "article_id": df.article_id,
            "model": "bertopic",
            "run_id": "m",
            "topic_id": [0, 1, -1],
        }
    )
    classical = pd.DataFrame(
        {
            "article_id": df.article_id,
            "model": "lda",
            "run_id": "c",
            "topic_id": [0, 1, 0],
        }
    )
    labels = {
        ("bertopic", 0): "Vehicles",
        ("bertopic", 1): "Policy",
        ("lda", 0): "Vehicles",
        ("lda", 1): "Policy",
    }
    return df, modern, classical, labels


class CorpusAndCacheTests(unittest.TestCase):
    def test_exact_project_corpus(self):
        with tempfile.TemporaryDirectory() as temp:
            df, summary = audit_corpus(out=temp)
            self.assertEqual(len(df), 7332)
            self.assertEqual(
                summary["dropped_article_ids"],
                ["1449843", "1465862", "1798409", "1821156", "1824347"],
            )
            self.assertEqual(
                corpus_hash(df),
                "c73293f76ba4b0a18d685e5724f75b1123a86c9012497fc324090989642a8f99",
            )
            self.assertEqual(
                load_corpus(temp).article_id.tolist(), df.article_id.tolist()
            )

    def test_chunk_boundaries(self):
        for n in [1, 480, 481, 960, 961]:
            chunks = h.token_chunks(str(n), Tokenizer())
            self.assertEqual(sum(chunks, []), list(range(n)))
            self.assertLessEqual(max(map(len, chunks)), 480)
        with self.assertRaises(ValueError):
            h.token_chunks("0", Tokenizer())

    def test_embeddings_and_stale_identity(self):
        h.validate_embeddings(np.tile(np.ones(384) / np.sqrt(384), (2, 1)), 2)
        for arr in [np.zeros((2, 384)), np.ones((3, 384)), np.full((2, 384), np.nan)]:
            with self.assertRaises(ValueError):
                h.validate_embeddings(arr, 2)
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            h.write_json(p / "manifest.json", {"identity": {"corpus_hash": "old"}})
            with self.assertRaises(ValueError):
                a.load_run(p, {"corpus_hash": "new"})

    def test_reservation_preserves_sample_and_rejects_changes(self):
        df, *_ = sample_frames()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sample.json"
            record = ev.reserve_review_ids(df, path, ["a"], n=2)
            self.assertEqual(set(record["article_ids"]), {"b", "c"})
            self.assertEqual(record, ev.reserve_review_ids(df, path, ["a"], n=2))
            with self.assertRaises(ValueError):
                ev.reserve_review_ids(df, path, ["b"], n=2)

    def test_cache_rejects_reordering_and_modified_vectors(self):
        df, *_ = sample_frames()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cache = root / "cache"
            cache.mkdir()
            corpus = root / "corpus.csv"

            def save_corpus(frame):
                frame.to_csv(corpus, index=False)
                h.write_json(
                    root / "corpus_manifest.json",
                    {
                        "article_ids": frame.article_id.tolist(),
                        "corpus_hash": corpus_hash(frame),
                    },
                )

            save_corpus(df)
            vectors = np.tile(np.ones(384) / np.sqrt(384), (len(df), 1))
            np.save(cache / "embeddings.npy", vectors)
            manifest = dict(
                article_ids=df.article_id.tolist(),
                text_hash=h.digest(df.text.tolist()),
                model=h.MODEL,
                revision=h.MODEL_REVISION,
                chunk_tokens=480,
                pooling="token_weighted_mean_l2",
                dimension=384,
            )
            h.write_json(cache / "manifest.json", manifest)
            h.write_json(
                root / "Results/modern/embedding_pointer.json",
                {
                    "folder": "cache",
                    "manifest": manifest,
                    "array_hash": a.array_hash(vectors),
                },
            )
            loaded, _ = h.load_inputs(root, corpus)
            self.assertEqual(loaded.article_id.tolist(), df.article_id.tolist())
            save_corpus(df.iloc[::-1])
            with self.assertRaisesRegex(ValueError, "Corpus/cache mismatch"):
                h.load_inputs(root, corpus)
            save_corpus(df)
            vectors[
                0
            ] *= -1  # Still unit length: shape/norm checks alone cannot detect this.
            np.save(cache / "embeddings.npy", vectors)
            with self.assertRaisesRegex(ValueError, "checksum"):
                h.load_inputs(root, corpus)


class EvaluationTests(unittest.TestCase):
    def test_silhouette_undefined(self):
        for labels in [[-1, -1], [0, 0], [0, 1]]:
            value, _ = h.silhouette(np.eye(2), labels, "cosine")
            self.assertTrue(np.isnan(value))

    def test_jaccard_orientation(self):
        lhs = pd.DataFrame(
            {"topic_id": [0, 0, -1], "rank": [1, 2, 1], "term": ["a", "b", "noise"]}
        )
        rhs = pd.DataFrame({"topic_id": [2, 2], "rank": [1, 2], "term": ["b", "c"]})
        table = ev.jaccard_table(lhs, rhs)
        self.assertEqual(table.index.tolist(), [0])
        self.assertEqual(table.columns.tolist(), [2])
        self.assertAlmostEqual(table.loc[0, 2], 1 / 3)

    def test_publication_denominators_and_alignment(self):
        df, modern, *_ = sample_frames()
        with tempfile.TemporaryDirectory() as temp:
            counts, proportions = ev.publication_exports(df, modern.iloc[::-1], temp)
            self.assertEqual(counts.to_numpy().sum(), 3)
            np.testing.assert_allclose(proportions.sum(axis=1), 1)
            self.assertEqual(proportions.loc["Other", -1], 1)
            self.assertEqual(proportions.loc["Outlet", 0], 0.5)
            with self.assertRaises(ValueError):
                ev.publication_exports(df, modern.iloc[:2], temp)

    def test_seed_permutation_and_outliers(self):
        df, modern, *_ = sample_frames()
        other = modern.copy()
        other.topic_id = [8, 9, -1]
        with tempfile.TemporaryDirectory() as temp:
            summary = ev.seed_publication_comparison(df, modern, other.iloc[::-1], temp)
            self.assertEqual(summary["adjusted_rand_index"], 1)
            self.assertEqual(summary["evaluated_count"], 2)
            changes = pd.read_csv(Path(temp) / "publication_changes.csv")
            self.assertTrue(changes.difference.eq(0).all())
            self.assertEqual(summary["unmatched_baseline_topics"], [])

    def test_classical_schema(self):
        df, _, classical, _ = sample_frames()
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            classical.iloc[::-1].to_csv(out / "assignments.csv", index=False)
            pd.DataFrame(
                [
                    dict(topic_id=t, rank=i + 1, term=f"word{i}", weight=0.1)
                    for t in [0, 1]
                    for i in range(10)
                ]
            ).to_csv(out / "terms.csv", index=False)
            pd.DataFrame(
                {"topic_id": [0, 1], "label": ["Vehicles", "Policy"], "count": [2, 1]}
            ).to_csv(out / "topics.csv", index=False)
            aligned, _, _ = ev.validate_classical(out, df.article_id)
            self.assertEqual(aligned.article_id.tolist(), df.article_id.tolist())
            with self.assertRaises(ValueError):
                ev.validate_classical(out, ["a", "b"])


class HumanReviewTests(unittest.TestCase):
    def packet(self, temp):
        df, modern, classical, labels = sample_frames()
        return ev.review_packets(
            df, modern, classical, temp, labels, article_ids=df.article_id.tolist()
        )

    def complete(self, temp):
        for i in [1, 2]:
            path = Path(temp) / f"reviewer_{i}.csv"
            table = pd.read_csv(path, keep_default_na=False)
            table["irrelevant"] = False
            table["ambiguous_label"] = False
            table.loc[table.topic_id.ge(0), "fit_rating"] = (
                [2, 3, 4, 4, 5] if i == 1 else [2, 4, 4, 5, 5]
            )
            table.to_csv(path, index=False)

    def test_pending_preserved_and_frozen(self):
        with tempfile.TemporaryDirectory() as temp:
            self.packet(temp)
            self.assertIn("pending", ev.summarize_reviews(temp))
            path = Path(temp) / "reviewer_1.csv"
            table = pd.read_csv(path, keep_default_na=False)
            table.loc[0, "notes"] = "Human note"
            table.to_csv(path, index=False)
            self.packet(temp)
            self.assertEqual(pd.read_csv(path).loc[0, "notes"], "Human note")
            df, m, c, labels = sample_frames()
            labels[("lda", 0)] = "Changed"
            with self.assertRaises(ValueError):
                ev.review_packets(
                    df, m, c, temp, labels, article_ids=df.article_id.tolist()
                )

    def test_agreement_and_outlier_exclusion(self):
        with tempfile.TemporaryDirectory() as temp:
            self.packet(temp)
            self.complete(temp)
            summary = ev.summarize_reviews(temp)
            modern = summary.set_index("model").loc["bertopic"]
            self.assertEqual(modern.rated_articles, 2)
            self.assertEqual(modern.unassigned_articles, 1)
            self.assertEqual(modern.within_one_agreement, 1)
            self.assertEqual(modern.bootstrap_samples, 1000)
            self.assertTrue((Path(temp) / "human_evaluation.csv").exists())

    def test_bad_roster_even_when_unrated(self):
        with tempfile.TemporaryDirectory() as temp:
            self.packet(temp)
            path = Path(temp) / "reviewer_2.csv"
            table = pd.read_csv(path)
            table.iloc[:-1].to_csv(path, index=False)
            with self.assertRaises(ValueError):
                ev.summarize_reviews(temp)

    def test_outlier_rating_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            self.packet(temp)
            self.complete(temp)
            path = Path(temp) / "reviewer_1.csv"
            table = pd.read_csv(path)
            table.loc[table.topic_id.eq(-1), "fit_rating"] = 1
            table.to_csv(path, index=False)
            with self.assertRaises(ValueError):
                ev.summarize_reviews(temp)

    def test_degenerate_kappa(self):
        self.assertTrue(np.isnan(quadratic_kappa([5, 5], [5, 5])))
        self.assertTrue(np.isnan(quadratic_kappa([], [])))
        from sklearn.metrics import cohen_kappa_score

        self.assertAlmostEqual(
            quadratic_kappa([1, 2, 4, 5], [1, 3, 3, 5]),
            cohen_kappa_score([1, 2, 4, 5], [1, 3, 3, 5], weights="quadratic"),
        )
        with tempfile.TemporaryDirectory() as temp:
            self.packet(temp)
            self.complete(temp)
            for i in [1, 2]:
                path = Path(temp) / f"reviewer_{i}.csv"
                table = pd.read_csv(path)
                table.loc[table.topic_id.ge(0), "fit_rating"] = 5
                table.to_csv(path, index=False)
            summary = ev.summarize_reviews(temp)
            self.assertTrue(summary.weighted_kappa.isna().all())
            self.assertTrue(summary.valid_bootstrap_samples.eq(0).all())


if __name__ == "__main__":
    unittest.main()
