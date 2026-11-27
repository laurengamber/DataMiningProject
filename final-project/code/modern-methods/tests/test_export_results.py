"""Consolidated exports use saved evidence and never mutate source artifacts."""

import hashlib
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd

from export_results import export_results
from shared.corpus import corpus_hash, digest, write_json
from src import artifacts


class ExportResultsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "modern-methods"
        self.out = self.root / "Results"
        self.source = self.out / "modern"
        self.run = self.source / "runs/n30_c25_s42"
        self.selected = self.source / "selected/n30_c25_s42"
        self.corpus = Path(self.temp.name) / "data"
        for folder in [self.run, self.selected, self.corpus]:
            folder.mkdir(parents=True)
        self.df = pd.DataFrame(dict(
            article_id=[f"{i:03}" for i in range(1, 9)],
            title=[f"Article {i}" for i in range(8)],
            text=[f"Full article text {i}, including Unicode: café" for i in range(8)],
            publication=["Outlet A"] * 4 + ["Outlet B"] * 4,
        ))
        self.df.to_csv(self.corpus / "corpus.csv", index=False)
        ch = corpus_hash(self.df)
        write_json(self.corpus / "corpus_manifest.json", dict(corpus_hash=ch, article_ids=self.df.article_id.tolist()))
        self.reservation = dict(corpus_hash=ch, article_ids=["001", "002"])
        write_json(self.source / "review_sample.json", self.reservation)
        write_json(self.source / "selection.json", dict(
            corpus_hash=ch, run_id=self.run.name, rationale="Synthetic choice", selected_by="Test"))
        pd.DataFrame(dict(run_id=[self.run.name])).to_csv(self.source / "experiments.csv", index=False)
        self.assignments = pd.DataFrame(dict(
            article_id=self.df.article_id, model="bertopic", run_id=self.run.name,
            topic_id=[-1, 0, 0, 0, 0, 1, 1, 1], membership_strength=[0, .2, .3, .4, .5, .6, .7, .8]))
        self.assignments.to_csv(self.run / "assignments.csv", index=False)
        pd.DataFrame(dict(topic_id=[-1, 0, 1], count=[1, 4, 3], label=["outlier keywords", "road keywords", "policy keywords"])).to_csv(self.run / "topics.csv", index=False)
        pd.DataFrame(dict(topic_id=[-1, 0, 1], rank=[1, 1, 1], term=["car", "road", "policy"], weight=[.1, .2, .3])).to_csv(self.run / "terms.csv", index=False)
        pd.DataFrame(dict(topic_id=[0, 1], coherence=[.4, .5], vocabulary_coverage=[1., 1.])).to_csv(self.run / "coherence.csv", index=False)
        reps = self.df.iloc[2:].drop(columns="text").copy()
        reps.insert(0, "rank", [1, 2, 3, 1, 2, 3])
        reps.insert(0, "topic_id", [0, 0, 0, 1, 1, 1])
        reps.to_csv(self.run / "representative_ids.csv", index=False)
        self.identity = dict(corpus_hash=ch, reservation_hash=digest(self.reservation), parameters=dict(seed=42))
        self.manifest = dict(identity=self.identity, corpus_hash=ch,
                             metrics=dict(run_id=self.run.name), environment=dict(hardware="synthetic"),
                             files={p.name: self.sha(p) for p in self.run.glob("*.csv")})
        # An absent local model must not prevent exporting tracked CSVs.
        self.manifest["files"]["model.pkl"] = "unavailable"
        write_json(self.run / "manifest.json", self.manifest)
        write_json(self.selected / "labels_identity.json", dict(
            run_id=self.run.name, corpus_hash=ch, run_identity_hash=digest(self.identity)))
        pd.DataFrame(dict(
            topic_id=[0, 1], count=[4, 3], keyword_label=["road keywords", "policy keywords"],
            proposed_label=["Road safety", "Unconfirmed policy label"],
            evidence_ids=["003 | 004 | 005", "006 | 007 | 008"], evidence_notes=["Evidence", "Draft"],
            confirmed=[True, False],
        )).to_csv(self.selected / "topic_labels.csv", index=False)
        pd.DataFrame(dict(seed=[7, 21], adjusted_rand_index=[.8, .9], evaluated_count=[6, 7],
                          evaluated_fraction=[.75, .875], outlier_agreement=[.9, 1.])).to_csv(self.selected / "stability.csv", index=False)
        counts = pd.crosstab(self.df.publication, self.assignments.topic_id)
        counts.to_csv(self.selected / "publication_counts.csv")
        counts.div(counts.sum(axis=1), axis=0).to_csv(self.selected / "publication_proportions.csv")
        counts.sum(axis=1).rename("article_count").to_csv(self.selected / "publication_sample_sizes.csv")

    @staticmethod
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def export(self):
        return export_results(self.root, self.corpus)

    def snapshots(self, folder, recursive=False):
        return {str(p.relative_to(folder)): p.read_bytes()
                for p in (folder.rglob("*") if recursive else folder.iterdir()) if p.is_file()}

    def test_export_labels_ids_provenance_and_repeatability(self):
        before = self.snapshots(self.source, recursive=True)
        self.assertEqual(self.export(), self.out)
        self.assertEqual(before, self.snapshots(self.source, recursive=True))
        assignments = pd.read_csv(self.out / "assignments.csv", dtype={"article_id": str})
        self.assertEqual(assignments.article_id.tolist(), self.df.article_id.tolist())
        pd.testing.assert_frame_equal(assignments, self.assignments)
        labels = pd.read_csv(self.out / "topics.csv").set_index("topic_id").label.to_dict()
        self.assertEqual(labels, {-1: "Unassigned", 0: "Road safety", 1: "policy keywords"})
        reps = pd.read_csv(self.out / "representatives.csv", dtype={"article_id": str})
        self.assertEqual(reps.text.tolist(), self.df.iloc[2:].text.tolist())
        self.assertFalse(set(reps.article_id) & set(self.reservation["article_ids"]))
        self.assertFalse((self.out / "mixtures.csv").exists())
        manifest = json.loads((self.out / "manifest.json").read_text())
        self.assertEqual(len(manifest["files"]), 13)  # Twelve CSVs and README.
        for name, checksum in manifest["files"].items():
            self.assertEqual(self.sha(self.out / name), checksum)
        first = self.snapshots(self.out)
        self.export()
        self.assertEqual(first, self.snapshots(self.out))
        self.assertEqual(before, self.snapshots(self.source, recursive=True))

    def test_refresh_uses_current_confirmations(self):
        self.export()
        path = self.selected / "topic_labels.csv"
        labels = pd.read_csv(path)
        labels.loc[1, "confirmed"] = True
        labels.to_csv(path, index=False)
        self.export()
        topics = pd.read_csv(self.out / "topics.csv").set_index("topic_id")
        self.assertEqual(topics.loc[1, "label"], "Unconfirmed policy label")

    def test_invalid_inputs_preserve_existing_exports(self):
        self.export()
        before = self.snapshots(self.out)
        mutations = [
            (self.selected / "stability.csv", None),
            (self.run / "terms.csv", b"changed"),
            (self.selected / "labels_identity.json", b"{}"),
            (self.selected / "topic_labels.csv", (self.selected / "topic_labels.csv").read_bytes().replace(b"003 | 004 | 005", b"002")),
            (self.selected / "publication_counts.csv", b"publication,-1,0,1\nOutlet A,100,0,0\n"),
            (self.source / "selection.json", json.dumps(dict(corpus_hash=corpus_hash(self.df), run_id="")).encode()),
        ]
        for path, content in mutations:
            with self.subTest(path=path):
                original = path.read_bytes()
                try:
                    if content is None:
                        path.unlink()
                    else:
                        path.write_bytes(content)
                    with self.assertRaises((ValueError, FileNotFoundError)):
                        self.export()
                    self.assertEqual(before, self.snapshots(self.out))
                finally:
                    path.write_bytes(original)

    def test_reserved_representative_rejected_even_with_valid_hash(self):
        path = self.run / "representative_ids.csv"
        path.write_bytes(path.read_bytes().replace(b"003", b"002"))
        self.manifest["files"][path.name] = self.sha(path)
        write_json(self.run / "manifest.json", self.manifest)
        with self.assertRaisesRegex(ValueError, "reserved review"):
            self.export()
        self.assertFalse((self.out / "assignments.csv").exists())

    def test_incorrect_counts_rejected_even_with_valid_hash(self):
        path = self.run / "topics.csv"
        topics = pd.read_csv(path)
        topics.loc[1, "count"] = 100
        topics.to_csv(path, index=False)
        self.manifest["files"][path.name] = self.sha(path)
        write_json(self.run / "manifest.json", self.manifest)
        with self.assertRaisesRegex(ValueError, "Topic counts"):
            self.export()

    def test_notebook_exports_selected_run_and_reports_pending_selection(self):
        notebook = Path(__file__).resolve().parents[1] / "notebooks/03_evaluation_and_comparison.ipynb"
        cells = json.loads(notebook.read_text())["cells"]
        source = next("".join(c["source"]) for c in cells
                      if c["cell_type"] == "code" and "modern = terms = inventory = labels = None" in "".join(c["source"]))
        context = dict(
            ROOT=self.root, OUT=self.source, df=self.df, pd=pd, json=json,
            corpus_hash=corpus_hash, digest=digest, a=artifacts,
            ev=SimpleNamespace(publication_exports=lambda *args: (None, None)),
            display=lambda *args: None,
            selection=json.loads((self.source / "selection.json").read_text()),
            experiments=pd.DataFrame(dict(run_id=[self.run.name], topic_count=[2], coherence=[.5], outlier_fraction=[.125])),
        )
        with redirect_stdout(StringIO()), patch("IPython.display.Image"), patch(
            "export_results.export_results", side_effect=lambda root: self.export()
        ) as exporter:
            exec(compile(source, str(notebook), "exec"), context)
            exporter.assert_called_once_with(self.root)
        before = self.snapshots(self.out)
        context["selection"] = None
        output = StringIO()
        with redirect_stdout(output), patch("export_results.export_results") as exporter:
            exec(compile(source, str(notebook), "exec"), context)
            exporter.assert_not_called()
        self.assertIn("consolidated CSV export pending", output.getvalue())
        self.assertEqual(before, self.snapshots(self.out))


if __name__ == "__main__":
    unittest.main()
