"""Read one frozen review packet and safely save one reviewer's own answers."""

from pathlib import Path
import hashlib
import json
import numbers
import os
import tempfile
import pandas as pd
from shared.corpus import digest
from shared.human_review import IDENTITY, KEYS

ANSWER_COLUMNS = ["fit_rating", "irrelevant", "ambiguous_label", "notes"]


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_session(folder, reviewer):
    """Read only the selected reviewer's CSV; never load the other reviewer's scores."""
    if reviewer not in ["reviewer_1", "reviewer_2"]:
        raise ValueError("Choose reviewer_1 or reviewer_2 before opening a packet.")
    folder = Path(folder)
    path = folder / f"{reviewer}.csv"
    status = json.loads((folder / "review_status.json").read_text())
    if status.get("joint_comparison_ready") is not True:
        raise ValueError(
            "The coordinator must prepare the frozen joint-model review first."
        )
    packet = pd.read_csv(
        folder / "review_packet.csv",
        dtype={"article_id": str, "run_id": str},
        keep_default_na=False,
    )
    freeze = json.loads((folder / "review_freeze.json").read_text())
    if digest(packet.to_dict("records")) != freeze["packet_hash"]:
        raise ValueError(
            "The frozen packet changed. Stop and ask the coordinator to investigate."
        )
    if (
        packet.duplicated(KEYS).any()
        or set(packet.model) != {"lda", "bertopic"}
        or not packet.groupby("article_id")
        .model.agg(lambda s: set(s) == {"lda", "bertopic"})
        .all()
        or not packet.groupby("article_id").size().eq(2).all()
    ):
        raise ValueError(
            "Expected one assignment per model for every reserved article."
        )
    before = file_hash(path)
    answers = pd.read_csv(
        path, dtype={"article_id": str, "run_id": str}, keep_default_na=False
    )
    if file_hash(path) != before:
        raise ValueError("Answers changed while opening them; reload the session.")
    if (
        not set(IDENTITY + ANSWER_COLUMNS).issubset(answers.columns)
        or answers.duplicated(KEYS).any()
    ):
        raise ValueError("The reviewer CSV has missing columns or duplicate rows.")
    expected = packet.set_index(KEYS)[["topic_id", "label", "title"]].sort_index()
    if (
        not answers.set_index(KEYS)[["topic_id", "label", "title"]]
        .sort_index()
        .equals(expected)
    ):
        raise ValueError(
            "Reviewer IDs, labels, or topics differ from the frozen packet."
        )
    # Restore packet order even if someone sorted their CSV in a spreadsheet.
    answers = (
        answers.set_index(KEYS)
        .loc[pd.MultiIndex.from_frame(packet[KEYS])]
        .reset_index()
    )
    raw = answers.fit_rating.astype(str).str.strip()
    provided = raw.ne("")
    scores = pd.to_numeric(raw.where(provided), errors="raise")
    if not (scores[provided].between(1, 5) & scores[provided].mod(1).eq(0)).all():
        raise ValueError("Existing fit ratings must be integers from 1 to 5.")
    if raw[answers.topic_id.eq(-1)].ne("").any():
        raise ValueError("Outlier fit ratings must be blank.")
    for flag in ["irrelevant", "ambiguous_label"]:
        if (
            not answers[flag]
            .astype(str)
            .str.lower()
            .str.strip()
            .isin(["true", "false", ""])
            .all()
        ):
            raise ValueError(f"Existing {flag} values must be true, false, or blank.")
    complete = provided | answers.topic_id.eq(-1)
    for flag in ["irrelevant", "ambiguous_label"]:
        complete &= answers[flag].astype(str).str.strip().ne("")
    return dict(
        folder=folder,
        reviewer=reviewer,
        path=path,
        packet=packet,
        answers=answers,
        complete=complete,
        answers_hash=before,
        freeze_hash=file_hash(folder / "review_freeze.json"),
    )


def choose_item(session, item_number=None):
    """Return a zero-based row index; the notebook shows one-based item numbers."""
    if item_number is None:
        remaining = session["complete"].index[~session["complete"]].tolist()
        return remaining[0] if remaining else None
    if isinstance(item_number, bool) or not isinstance(item_number, numbers.Integral):
        raise ValueError("ITEM_NUMBER must be a whole number or None.")
    if not 1 <= item_number <= len(session["packet"]):
        raise ValueError(f"ITEM_NUMBER must be between 1 and {len(session['packet'])}.")
    return int(item_number) - 1


def save_answer(
    session,
    row_index,
    fit_rating,
    irrelevant,
    ambiguous_label,
    notes="",
    allow_update=False,
):
    """Update one row, reject stale sessions/accidental replacements, then replace the CSV atomically."""
    if (
        isinstance(row_index, bool)
        or not isinstance(row_index, numbers.Integral)
        or not 0 <= row_index < len(session["packet"])
    ):
        raise ValueError("Display a valid item before saving an answer.")
    if type(irrelevant) is not bool or type(ambiguous_label) is not bool:
        raise ValueError("Set both flags explicitly to True or False.")
    if not isinstance(notes, str):
        raise ValueError("NOTES must be text.")
    row = session["packet"].iloc[row_index]
    if row.topic_id == -1:
        if fit_rating is not None:
            raise ValueError("Leave FIT_RATING = None for an unassigned article.")
        rating = ""
    else:
        if (
            isinstance(fit_rating, bool)
            or not isinstance(fit_rating, numbers.Integral)
            or not 1 <= fit_rating <= 5
        ):
            raise ValueError("Set FIT_RATING to a whole number from 1 to 5.")
        rating = int(fit_rating)
    current = load_session(session["folder"], session["reviewer"])
    if (
        current["answers_hash"] != session["answers_hash"]
        or current["freeze_hash"] != session["freeze_hash"]
    ):
        raise ValueError(
            "The review file changed after you displayed this item. Reload it before saving."
        )
    old = current["answers"].loc[row_index, ANSWER_COLUMNS]
    if old.astype(str).str.strip().ne("").any() and not allow_update:
        raise ValueError(
            "This item already has answers. Use ALLOW_UPDATE = True only for an intentional correction."
        )
    answers = current["answers"].copy()
    # Object columns accept both initially blank cells and completed integer/bool values.
    for column in ANSWER_COLUMNS:
        answers[column] = answers[column].astype(object)
    answers.loc[row_index, ANSWER_COLUMNS] = [
        rating,
        irrelevant,
        ambiguous_label,
        notes.strip(),
    ]
    # The temporary filename is also ignored by the existing reviewer_*.csv Git rule.
    descriptor, temporary = tempfile.mkstemp(
        prefix=f"{session['reviewer']}_", suffix=".csv", dir=session["folder"]
    )
    try:
        with os.fdopen(descriptor, "w") as stream:
            answers.to_csv(stream, index=False)
        if file_hash(session["path"]) != current["answers_hash"]:
            raise ValueError(
                "The review file changed during saving; reload before trying again."
            )
        os.replace(temporary, session["path"])
    finally:
        Path(temporary).unlink(missing_ok=True)
    return load_session(session["folder"], session["reviewer"])
