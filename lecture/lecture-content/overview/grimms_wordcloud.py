"""Create a reproducible word cloud from Kaggle's 63 Grimm fairy tales.

Run from the project root:
    uv run python lecture-content/overview/grimms_wordcloud.py
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from pathlib import Path
import re
import unicodedata
from urllib.request import urlopen
from zipfile import ZipFile
import io

from PIL import Image, ImageDraw, ImageFont
from wordcloud import STOPWORDS, WordCloud
from wordcloud.wordcloud import FONT_PATH


HERE = Path(__file__).resolve().parent
DOWNLOAD_URL = (
    "https://www.kaggle.com/api/v1/datasets/download/"
    "tschomacker/grimms-fairy-tales"
)
# Explicitly excluded so readers can distinguish editorial choices from counts.
EXTRA_STOPWORDS = {
    "said", "say", "says", "replied", "answered", "cried",
    "will", "would", "could", "must", "shall", "may", "might",
    "one", "two", "now", "upon", "thou", "thee", "thy", "thine",
}
PALETTE = ["#254C45", "#38756C", "#505071", "#8D4F55", "#AB6C31", "#35465C"]


def color_word(word, font_size, position, orientation, random_state, **kwargs):
    return random_state.choice(PALETTE)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=HERE / "data/grimms_fairytales.csv")
    parser.add_argument("--output-dir", type=Path, default=HERE)
    parser.add_argument(
        "--titles-file", type=Path,
        help="Optional UTF-8 file listing one exact story title per line (case-insensitive).",
    )
    args = parser.parse_args()

    if not args.input.exists():
        args.input.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(DOWNLOAD_URL, timeout=60) as response:
            archive_bytes = response.read()
        with ZipFile(io.BytesIO(archive_bytes)) as archive:
            args.input.write_bytes(archive.read("grimms_fairytales.csv"))

    with args.input.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if "Text" not in (reader.fieldnames or []):
            raise ValueError("The input CSV must contain a Text column.")
        if args.titles_file and "Title" not in reader.fieldnames:
            raise ValueError("Selecting stories requires a Title column.")
        rows = list(reader)
    if args.titles_file:
        titles = [line.strip() for line in args.titles_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        requested = {title.casefold() for title in titles}
        if not requested:
            raise ValueError("The titles file contains no story titles.")
        rows = [row for row in rows if row["Title"].strip().casefold() in requested]
        found = Counter(row["Title"].strip().casefold() for row in rows)
        missing = requested - found.keys()
        if missing:
            raise ValueError(f"Story titles not found: {sorted(missing)}")
        if any(count != 1 for count in found.values()):
            raise ValueError("Selected story titles must each match exactly one document.")
        if any(not row["Text"].strip() for row in rows):
            raise ValueError("A selected story has empty text.")
        print("Selected stories:", "; ".join(row["Title"] for row in rows))
    stories = [row["Text"].strip() for row in rows if row["Text"].strip()]
    if not stories:
        raise ValueError("The input contains no nonempty stories.")

    text = unicodedata.normalize("NFKC", "\n".join(stories)).lower()
    text = text.replace("’", "'")
    text = re.sub(r"\b([a-z]+)'s\b", r"\1", text)
    tokens = re.findall(r"[a-z]+(?:'[a-z]+)?", text)
    stopwords = set(STOPWORDS) | EXTRA_STOPWORDS
    counts = Counter(word for word in tokens if len(word) > 2 and word not in stopwords)
    if not counts:
        raise ValueError("No words remain after preprocessing.")
    # Alphabetical tie-breaking keeps the result stable across runs.
    frequencies = dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
    cloud = WordCloud(
        width=2200, height=1120, background_color="#FAF7F0",
        max_words=160, min_font_size=13, max_font_size=220,
        prefer_horizontal=1.0, relative_scaling=0.5,
        random_state=42, margin=8, collocations=False,
        color_func=color_word,
    ).generate_from_frequencies(frequencies)

    canvas = Image.new("RGB", (2400, 1500), "#FAF7F0")
    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.truetype(FONT_PATH, 76)
    subtitle_font = ImageFont.truetype(FONT_PATH, 29)
    footer_font = ImageFont.truetype(FONT_PATH, 23)
    draw.text((1200, 70), "GRIMMS' FAIRY TALES", fill="#254C45", font=title_font, anchor="mt")
    draw.text(
        (1200, 170),
        (f"{len(stories)} selected stories  /  Pre-lecture reading"
         if args.titles_file else f"{len(stories)} stories  /  The words that fill their world"),
        fill="#50575A", font=subtitle_font, anchor="mt",
    )
    draw.line((100, 238, 2300, 238), fill="#D7D2C6", width=2)
    canvas.paste(cloud.to_image(), (100, 265))
    draw.text(
        (1200, 1420),
        "Larger words occur more often. Common words and selected narration words removed.",
        fill="#50575A", font=footer_font, anchor="mt",
    )
    draw.text(
        (1200, 1460), "Source: Kaggle / tschomacker / grimms-fairy-tales",
        fill="#50575A", font=footer_font, anchor="mt",
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    image_path = args.output_dir / "grimms_wordcloud.png"
    canvas.save(image_path, dpi=(200, 200))
    # A scalable cloud without the title/footer, convenient for slide layouts.
    (args.output_dir / "grimms_wordcloud.svg").write_text(
        cloud.to_svg(embed_font=True), encoding="utf-8"
    )
    with (args.output_dir / "grimms_word_frequencies.csv").open("w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow(["word", "count"])
        writer.writerows(frequencies.items())
    print(f"Read {len(stories)} stories; retained {sum(counts.values()):,} tokens and {len(counts):,} unique words.")
    print(f"Saved {image_path}")
    print("Most frequent:", ", ".join(f"{word} ({count})" for word, count in list(frequencies.items())[:12]))


if __name__ == "__main__":
    main()
