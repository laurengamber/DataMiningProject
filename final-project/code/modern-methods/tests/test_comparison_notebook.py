"""Execute comparison cells against temporary synthetic exports, never study ratings."""

from contextlib import redirect_stdout
import hashlib
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
import pandas as pd
from src import artifacts as a
from shared.corpus import corpus_hash, digest, write_json

NOTEBOOK = Path(__file__).resolve().parents[2] / "comparison/pipeline_comparison.ipynb"


class ComparisonNotebookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.out = self.root / "Results/modern"
        self.lda = self.root / "Results/classical"
        self.run = self.out / "runs/m"
        self.run.mkdir(parents=True)
        self.lda.mkdir(parents=True)
        words = [
            "road vehicle safety driver traffic sensor crash wheel truck highway".split(),
            "policy law bill senate regulation state government public rule agency".split(),
        ]
        self.df = pd.DataFrame(
            dict(
                article_id=[str(i) for i in range(60)],
                text=[" ".join(words[i % 2]) for i in range(60)],
                title=[f"Synthetic article {i}" for i in range(60)],
                publication=["Synthetic outlet"] * 60,
            )
        )
        self.reservation = dict(
            corpus_hash=corpus_hash(self.df), article_ids=["0", "1", "2", "3"]
        )
        write_json(self.out / "review_sample.json", self.reservation)
        write_json(
            self.out / "selection.json",
            dict(
                corpus_hash=corpus_hash(self.df),
                run_id="m",
                rationale="Synthetic test only",
                selected_by="Test",
            ),
        )
        pd.DataFrame({"run_id": ["m"]}).to_csv(
            self.out / "experiments.csv", index=False
        )
        modern = pd.DataFrame(
            dict(
                article_id=self.df.article_id,
                model="bertopic",
                run_id="m",
                topic_id=[-1] + [i % 2 for i in range(1, 60)],
            )
        )
        # LDA topic numbers deliberately differ, and its rows arrive reversed.
        classical = pd.DataFrame(
            dict(
                article_id=self.df.article_id,
                model="lda",
                run_id="c",
                topic_id=[10 if i % 2 == 0 else 20 for i in range(60)],
            )
        )
        for folder, frame, topics in [
            (self.run, modern, [0, 1]),
            (self.lda, classical.iloc[::-1], [10, 20]),
        ]:
            frame.to_csv(folder / "assignments.csv", index=False)
            term_rows = [
                dict(topic_id=t, rank=r, term=w, weight=1 / r)
                for t, terms in zip(topics, words)
                for r, w in enumerate(terms, 1)
            ]
            pd.DataFrame(term_rows).to_csv(folder / "terms.csv", index=False)
            frame.topic_id.value_counts().sort_index().rename("count").rename_axis(
                "topic_id"
            ).reset_index().assign(
                label=lambda x: x.topic_id.map(lambda t: f"Synthetic topic {t}")
            ).to_csv(
                folder / "topics.csv", index=False
            )
        pd.DataFrame(dict(topic_id=[0, 1], rank=[1, 1], article_id=["6", "7"])).to_csv(
            self.run / "representative_ids.csv", index=False
        )
        pd.DataFrame(
            dict(topic_id=[0, 1], coherence=[0.5, 0.5], vocabulary_coverage=[1.0, 1.0])
        ).to_csv(self.run / "coherence.csv", index=False)
        identity = dict(
            corpus_hash=corpus_hash(self.df), reservation_hash=digest(self.reservation)
        )
        write_json(
            self.run / "manifest.json",
            dict(
                identity=identity,
                files={
                    p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in self.run.glob("*.csv")
                },
                metrics=dict(
                    fitting_representation_seconds=2.0, evaluation_seconds=1.0
                ),
                environment={"hardware": "synthetic"},
            ),
        )
        write_json(
            self.lda / "manifest.json",
            dict(
                corpus_hash=corpus_hash(self.df),
                review_reservation_hash=digest(self.reservation),
                labels_confirmed=True,
                timings={"fit": 1.5},
                environment={"hardware": "synthetic"},
            ),
        )
        selected = self.out / "selected/m"
        labels = a.labels_table(
            self.run,
            selected,
            dict(
                run_id="m",
                corpus_hash=corpus_hash(self.df),
                run_identity_hash=digest(identity),
            ),
        )
        labels["proposed_label"] = ["Roads", "Policy"]
        labels["evidence_notes"] = "Synthetic development evidence"
        labels["confirmed"] = True
        labels.to_csv(selected / "topic_labels.csv", index=False)
        self.cells = {
            c["metadata"]["tags"][0]: "".join(c["source"])
            for c in json.loads(NOTEBOOK.read_text())["cells"]
            if c["cell_type"] == "code"
        }
        self.ctx = {}
        self.run_cell("setup")
        self.ctx.update(
            ROOT=self.root,
            OUT=self.out,
            CLASSICAL=self.lda,
            COMPARISON_ROOT=self.root / "Results/comparison",
            load_corpus=lambda: self.df,
            display=lambda *a, **k: None,
        )
        self.ctx["COMPARISON_ROOT"].mkdir(parents=True)
        self.run_cell("corpus")

    def run_cell(self, tag, source=None):
        with redirect_stdout(StringIO()):
            exec(compile(source or self.cells[tag], str(NOTEBOOK), "exec"), self.ctx)

    def load_models(self):
        for tag in ["modern-input", "classical-input", "comparison-identity"]:
            self.run_cell(tag)

    def test_pending_selection_and_missing_handoff_finish_with_status(self):
        self.ctx["selection"] = None
        (self.lda / "terms.csv").unlink()
        self.load_models()
        for tag in [
            "metrics",
            "overlap",
            "publications",
            "runtime",
            "review-packet",
            "human-summary",
            "evidence",
        ]:
            self.run_cell(tag)
        self.assertIsNone(self.ctx["COMPARISON"])
        self.assertIsNone(self.ctx["human_summary"])
        status = json.loads((self.root / "Results/comparison/status.json").read_text())
        self.assertIsNone(status["modern_run"])
        self.assertIsNone(status["classical_run"])
        self.assertIn("Pending", status["human_status"])
        self.assertFalse(list(self.root.rglob("reviewer_1.csv")))

    def test_complete_comparison_aligns_topics_denominators_and_preserves_answers(self):
        self.load_models()
        for tag in [
            "metrics",
            "overlap",
            "publications",
            "runtime",
            "review-packet",
            "human-summary",
            "evidence",
        ]:
            self.run_cell(tag)
        out = self.ctx["COMPARISON"]
        matches = self.ctx["best"].set_index("lda_topic")
        self.assertEqual(matches.loc[10, "modern_topic"], 0)
        self.assertEqual(matches.loc[20, "modern_topic"], 1)
        contingency = pd.read_csv(out / "assignment_contingency.csv", index_col=0)
        self.assertEqual(contingency.loc[10, "-1"], 1)
        modern_shares = pd.read_csv(
            out / "modern/publication_proportions.csv", index_col=0
        )
        self.assertAlmostEqual(modern_shares.iloc[0]["-1"], 1 / 60)
        self.assertAlmostEqual(modern_shares.iloc[0].sum(), 1.0)
        self.assertTrue(self.ctx["pipeline_comparison"].mean_1.isna().all())
        review = out / "human_review"
        for reviewer in ["reviewer_1", "reviewer_2"]:
            path = review / f"{reviewer}.csv"
            ratings = pd.read_csv(path, keep_default_na=False)
            ratings["fit_rating"] = [
                3 + i % 2 if t >= 0 else "" for i, t in enumerate(ratings.topic_id)
            ]
            ratings["irrelevant"] = False
            ratings["ambiguous_label"] = False
            ratings["notes"] = "Synthetic fixture only"
            ratings.to_csv(path, index=False)
        before = {p: p.read_bytes() for p in review.glob("reviewer_*.csv")}
        # Re-preparing a frozen packet must preserve completed independent answers.
        self.run_cell("review-packet")
        self.run_cell(
            "human-summary",
            self.cells["human-summary"].replace(
                "RUN_HUMAN_SUMMARY = False", "RUN_HUMAN_SUMMARY = True"
            ),
        )
        self.run_cell("evidence")
        result = self.ctx["pipeline_comparison"].set_index("model")
        self.assertEqual(result.loc["bertopic", "rated_articles"], 3)
        self.assertEqual(result.loc["lda", "rated_articles"], 4)
        self.assertEqual(result.loc["bertopic", "unassigned_fraction"], 0.25)
        self.assertTrue(result.human_status.eq("complete").all())
        self.assertTrue(self.ctx["human_summary"].bootstrap_samples.eq(1000).all())
        for p, contents in before.items():
            self.assertEqual(p.read_bytes(), contents)
        # A different classical export must not overwrite existing review/results.
        (self.lda / "terms.csv").write_text((self.lda / "terms.csv").read_text() + "\n")
        with self.assertRaisesRegex(ValueError, "different model exports"):
            self.run_cell("comparison-identity")

    def test_unconfirmed_labels_allow_quantitative_work_but_no_packet(self):
        manifest = json.loads((self.lda / "manifest.json").read_text())
        manifest["labels_confirmed"] = False
        write_json(self.lda / "manifest.json", manifest)
        self.load_models()
        self.run_cell("metrics")
        self.run_cell("review-packet")
        self.assertIsNotNone(self.ctx["comparison_metrics"])
        self.assertIsNone(self.ctx["review_folder"])

    def test_invalid_supplied_handoffs_raise(self):
        manifest = json.loads((self.lda / "manifest.json").read_text())
        for mutation in [
            {"corpus_hash": "wrong"},
            {"timings": {"fit": -1}},
            {"review_reservation_hash": "wrong"},
        ]:
            with self.subTest(mutation=mutation):
                write_json(self.lda / "manifest.json", dict(manifest, **mutation))
                with self.assertRaises(ValueError):
                    self.run_cell("classical-input")
        with (self.run / "assignments.csv").open("a") as stream:
            stream.write("\n")
        with self.assertRaisesRegex(ValueError, "Modern export changed"):
            self.run_cell("modern-input")

    def test_modern_notebook_has_no_joint_evaluation(self):
        path = (
            NOTEBOOK.parent.parent
            / "modern-methods/notebooks/03_evaluation_and_comparison.ipynb"
        )
        source = "\n".join(
            "".join(c["source"]) for c in json.loads(path.read_text())["cells"]
        )
        for removed in [
            "validate_classical",
            "jaccard_table",
            "review_packets",
            "summarize_reviews",
            "CLASSICAL",
            "human_status",
        ]:
            self.assertNotIn(removed, source)


if __name__ == "__main__":
    unittest.main()
