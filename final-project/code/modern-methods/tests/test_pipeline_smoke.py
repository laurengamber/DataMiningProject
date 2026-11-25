"""Exercise the actual notebook fitting function; synthetic results remain temporary."""

import json
import tempfile
import time
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from src import topic_helpers as h, artifacts as a
from shared import evaluation as ev
from shared.corpus import digest


class PipelineSmoke(unittest.TestCase):
    def test_native_pipeline_serialization_and_review_separation(self):
        from bertopic import BERTopic
        from umap import UMAP
        from hdbscan import HDBSCAN
        from sklearn.feature_extraction.text import CountVectorizer

        rng = np.random.default_rng(42)
        vectors = rng.normal(size=(80, 384))
        vectors[:40, :10] += 5
        vectors[40:, 10:20] += 5
        vectors /= np.linalg.norm(vectors, axis=1)[:, None]
        words = [
            "vehicle road autonomous safety crash driver sensor wheel traffic travel",
            "policy regulation senate bill testing government law vote committee legislation",
        ]
        df = pd.DataFrame(
            {
                "article_id": list(map(str, range(80))),
                "text": [words[i // 40] for i in range(80)],
                "title": ["Synthetic"] * 80,
                "publication": ["Synthetic outlet"] * 80,
            }
        )
        texts, dictionary = ev.reference_texts(df)
        vocabulary = (
            CountVectorizer(stop_words="english", min_df=5).fit(df.text).vocabulary_
        )
        notebook = (
            Path(__file__).resolve().parents[1]
            / "notebooks/02_modern_topic_modeling.ipynb"
        )
        cells = json.loads(notebook.read_text())["cells"]
        source = "".join(
            next(
                c for c in cells if "model-fit" in c.get("metadata", {}).get("tags", [])
            )["source"]
        )
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            reservation = ev.reserve_review_ids(df, out / "sample.json", n=10)
            context = dict(
                BERTopic=BERTopic,
                UMAP=UMAP,
                HDBSCAN=HDBSCAN,
                CountVectorizer=CountVectorizer,
                df=df,
                embeddings=vectors,
                texts=texts,
                dictionary=dictionary,
                vocabulary=vocabulary,
                a=a,
                h=h,
                time=time,
                OUT=out,
                implementation_hash=digest(source),
                reservation=reservation,
            )
            exec(compile(source, str(notebook), "exec"), context)
            model, metrics = context["fit_configuration"](15, 10)
            self.assertGreaterEqual(metrics["topic_count"], 2)
            self.assertEqual(model.topic_embeddings_.shape[1], 384)
            reloaded, again = context["fit_configuration"](15, 10)
            self.assertEqual(model.topics_, reloaded.topics_)
            self.assertEqual(metrics["run_id"], again["run_id"])
            folder = out / "runs" / metrics["run_id"]
            assignments = pd.read_csv(folder / "assignments.csv")
            self.assertEqual(assignments.topic_id.tolist(), model.topics_)
            representatives = pd.read_csv(
                folder / "representative_ids.csv", dtype={"article_id": str}
            )
            self.assertFalse(
                set(representatives.article_id) & set(reservation["article_ids"])
            )
            identity = {"run_id": metrics["run_id"], "corpus_hash": h.corpus_hash(df)}
            table = a.labels_table(folder, out / "labels", identity)
            table.loc[0, "proposed_label"] = "Team edit"
            table.to_csv(out / "labels/topic_labels.csv", index=False)
            again = a.labels_table(folder, out / "labels", identity)
            self.assertEqual(again.loc[0, "proposed_label"], "Team edit")
            table.loc[0, "evidence_ids"] = reservation["article_ids"][0]
            table.to_csv(out / "labels/topic_labels.csv", index=False)
            with self.assertRaises(ValueError):
                a.labels_table(folder, out / "labels", identity)
            context["implementation_hash"] = "changed"
            with self.assertRaises(ValueError):
                context["fit_configuration"](15, 10)


if __name__ == "__main__":
    unittest.main()
