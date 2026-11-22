"""Test reviewer data entry against temporary packets, never genuine study answers."""

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
import pandas as pd
from src.topic_helpers import review_packets, summarize_reviews
from src.reviewer import load_session, choose_item, save_answer


class ReviewerNotebookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        frame = pd.DataFrame(
            {
                "article_id": ["a", "b"],
                "title": ["Synthetic road news", "Synthetic mixed news"],
                "text": [
                    "Synthetic vehicle safety article.",
                    "Synthetic policy article.",
                ],
            }
        )
        modern = pd.DataFrame(
            {
                "article_id": ["a", "b"],
                "model": "bertopic",
                "run_id": "m",
                "topic_id": [0, -1],
            }
        )
        classical = pd.DataFrame(
            {
                "article_id": ["a", "b"],
                "model": "lda",
                "run_id": "c",
                "topic_id": [0, 1],
            }
        )
        labels = {("bertopic", 0): "Safety", ("lda", 0): "Safety", ("lda", 1): "Policy"}
        review_packets(
            frame, modern, classical, self.folder, labels, article_ids=["a", "b"]
        )

    def test_load_and_save_preserve_other_reviewer_and_resume(self):
        other = (self.folder / "reviewer_2.csv").read_bytes()
        session = load_session(self.folder, "reviewer_1")
        index = choose_item(session)
        self.assertEqual(index, 0)
        session = save_answer(
            session,
            index,
            4,
            False,
            False,
            notes="Read the complete synthetic article.",
        )
        self.assertTrue(session["complete"].iloc[index])
        self.assertEqual(choose_item(load_session(self.folder, "reviewer_1")), 1)
        self.assertEqual((self.folder / "reviewer_2.csv").read_bytes(), other)
        # This file is not needed for one person's independent work.
        (self.folder / "reviewer_2.csv").unlink()
        self.assertEqual(
            int(load_session(self.folder, "reviewer_1")["complete"].sum()), 1
        )

    def test_reject_invalid_answers_and_stale_edits(self):
        session = load_session(self.folder, "reviewer_1")
        before = session["path"].read_bytes()
        for rating, irrelevant, ambiguous in [
            (None, False, False),
            (0, False, False),
            (6, False, False),
            (True, False, False),
            (3, None, False),
            (3, "false", False),
        ]:
            with self.assertRaises(ValueError):
                save_answer(session, 0, rating, irrelevant, ambiguous)
        self.assertEqual(session["path"].read_bytes(), before)
        current = save_answer(session, 0, 3, False, False)
        with self.assertRaisesRegex(ValueError, "changed"):
            save_answer(session, 0, 4, False, False, allow_update=True)
        with self.assertRaisesRegex(ValueError, "already has answers"):
            save_answer(current, 0, 4, False, False)
        corrected = save_answer(current, 0, 4, False, False, allow_update=True)
        self.assertEqual(int(corrected["answers"].loc[0, "fit_rating"]), 4)

    def test_outlier_and_completed_files_match_existing_summary(self):
        for reviewer in ["reviewer_1", "reviewer_2"]:
            session = load_session(self.folder, reviewer)
            for index, row in session["packet"].iterrows():
                if row.topic_id == -1:
                    with self.assertRaises(ValueError):
                        save_answer(session, index, 1, False, False)
                    rating = None
                else:
                    rating = 3 + index % 2
                session = save_answer(
                    session, index, rating, False, False, notes="Synthetic test only."
                )
            self.assertIsNone(choose_item(session))
            self.assertTrue(session["complete"].all())
        result = summarize_reviews(self.folder, bootstrap_samples=20)
        modern = result.set_index("model").loc["bertopic"]
        self.assertEqual(modern.rated_articles, 1)
        self.assertEqual(modern.unassigned_articles, 1)

    def test_frozen_packet_and_identity_validation(self):
        packet = pd.read_csv(self.folder / "review_packet.csv")
        packet.loc[0, "label"] = "Changed label"
        packet.to_csv(self.folder / "review_packet.csv", index=False)
        with self.assertRaisesRegex(ValueError, "frozen packet changed"):
            load_session(self.folder, "reviewer_1")
        with self.assertRaises(ValueError):
            load_session(self.folder, "reviewer_3")

    def test_notebook_display_save_progress_and_number_guard(self):
        path = (
            Path(__file__).resolve().parents[2] / "human-review/04_human_review.ipynb"
        )
        notebook = json.loads(path.read_text())
        cells = {
            c["metadata"]["tags"][0]: "".join(c["source"])
            for c in notebook["cells"]
            if c["cell_type"] == "code"
        }
        context = {}
        with redirect_stdout(StringIO()):
            exec(compile(cells["setup"], str(path), "exec"), context)
            context["display"] = lambda *args, **kwargs: None
            config = (
                cells["configuration"]
                .replace("REVIEWER = None", 'REVIEWER = "reviewer_1"')
                .replace(
                    "PACKET_FOLDER = None",
                    f"PACKET_FOLDER = Path({str(self.folder)!r})",
                )
            )
            exec(compile(config, str(path), "exec"), context)
            original = (self.folder / "reviewer_1.csv").read_bytes()
            exec(compile(cells["display-item"], str(path), "exec"), context)
            exec(compile(cells["save-answer"], str(path), "exec"), context)
            self.assertEqual((self.folder / "reviewer_1.csv").read_bytes(), original)
            enabled = (
                cells["save-answer"]
                .replace("ITEM_TO_SAVE = None", "ITEM_TO_SAVE = 1", 1)
                .replace("FIT_RATING = None", "FIT_RATING = 4", 1)
                .replace("IRRELEVANT = None", "IRRELEVANT = False", 1)
                .replace("AMBIGUOUS_LABEL = None", "AMBIGUOUS_LABEL = False", 1)
                .replace("SAVE_RATING = False", "SAVE_RATING = True", 1)
            )
            exec(compile(enabled, str(path), "exec"), context)
            self.assertEqual(int(context["SESSION"]["complete"].sum()), 1)
            exec(compile(cells["display-item"], str(path), "exec"), context)
            with self.assertRaisesRegex(ValueError, "displayed item"):
                exec(compile(enabled, str(path), "exec"), context)
            exec(compile(cells["progress"], str(path), "exec"), context)
            exec(compile(cells["team-summary"], str(path), "exec"), context)
            exec(compile(cells["team-notes"], str(path), "exec"), context)
            self.assertFalse((self.folder / "human_evaluation.csv").exists())

    def test_separate_notebooks_save_only_their_preconfigured_reviewer(self):
        review_root = Path(__file__).resolve().parents[2] / "human-review"
        for reviewer, other in [
            ("reviewer_1", "reviewer_2"),
            ("reviewer_2", "reviewer_1"),
        ]:
            with self.subTest(reviewer=reviewer), redirect_stdout(StringIO()):
                path = review_root / f"{reviewer}.ipynb"
                notebook = json.loads(path.read_text())
                cells = {
                    cell["metadata"]["tags"][0]: "".join(cell["source"])
                    for cell in notebook["cells"]
                    if cell["cell_type"] == "code"
                }
                self.assertNotIn("team-summary", cells)
                self.assertNotIn("team-notes", cells)
                self.assertNotIn("summarize_reviews", cells["setup"])
                context = {}
                exec(compile(cells["setup"], str(path), "exec"), context)
                context["display"] = lambda *args, **kwargs: None
                config = cells["configuration"].replace(
                    "PACKET_FOLDER = None",
                    f"PACKET_FOLDER = Path({str(self.folder)!r})",
                )
                exec(compile(config, str(path), "exec"), context)
                self.assertEqual(context["REVIEWER"], reviewer)
                self.assertEqual(
                    context["SESSION"]["path"], (self.folder / f"{reviewer}.csv").resolve()
                )
                other_before = (self.folder / f"{other}.csv").read_bytes()
                own_before = (self.folder / f"{reviewer}.csv").read_bytes()
                exec(compile(cells["display-item"], str(path), "exec"), context)
                exec(compile(cells["save-answer"], str(path), "exec"), context)
                self.assertEqual(
                    (self.folder / f"{reviewer}.csv").read_bytes(), own_before
                )
                enabled = (
                    cells["save-answer"]
                    .replace("ITEM_TO_SAVE = None", "ITEM_TO_SAVE = 1", 1)
                    .replace("FIT_RATING = None", "FIT_RATING = 4", 1)
                    .replace("IRRELEVANT = None", "IRRELEVANT = False", 1)
                    .replace("AMBIGUOUS_LABEL = None", "AMBIGUOUS_LABEL = False", 1)
                    .replace("SAVE_RATING = False", "SAVE_RATING = True", 1)
                )
                exec(compile(enabled, str(path), "exec"), context)
                self.assertEqual(int(context["SESSION"]["complete"].sum()), 1)
                self.assertEqual(
                    (self.folder / f"{other}.csv").read_bytes(), other_before
                )
                exec(compile(config, str(path), "exec"), context)
                self.assertEqual(int(context["SESSION"]["complete"].sum()), 1)
                exec(compile(cells["progress"], str(path), "exec"), context)
                self.assertFalse((self.folder / "human_evaluation.csv").exists())


if __name__ == "__main__":
    unittest.main()
