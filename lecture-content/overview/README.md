# Grimm's fairy-tale word cloud

The cloud combines the `Text` column of all 63 documents in
[tschomacker's Grimms' Fairy Tales dataset on Kaggle](https://www.kaggle.com/datasets/tschomacker/grimms-fairy-tales).
Titles and the CSV index are excluded.

From the repository root, run:

```sh
uv run python lecture-content/overview/grimms_wordcloud.py
```

The project's existing dependencies include `wordcloud`; it also installs the
Pillow and fontTools dependencies used for the image and embedded SVG font.
The downloaded CSV is cached in `data/grimms_fairytales.csv` beside the script.
If missing, the script downloads it from Kaggle's public dataset endpoint.

Outputs:

- `grimms_wordcloud.png`: a 2400 × 1500 image with title, explanation, and source.
- `grimms_wordcloud.svg`: a scalable version of the cloud for slides, without the title/footer.
- `grimms_word_frequencies.csv`: all retained words and their exact corpus counts.

Preprocessing lowercases the text, normalizes apostrophes, strips possessive
`'s`, and extracts alphabetic tokens (including contractions). Tokens shorter
than three characters and the `wordcloud` English stopwords are removed.
The additional exclusions are `said`, `say`, `says`, `replied`, `answered`,
`cried`, `will`, `would`, `could`, `must`, `shall`, `may`, `might`,
`one`, `two`, `now`, `upon`, `thou`, `thee`, `thy`, and `thine`.
No stemming, lemmatization, or plural merging is applied. Each occurrence counts
equally, so longer tales contribute more words. The image displays the 160 most
frequent retained words. Font size increases with frequency but is also adjusted
to fit the layout; consult the CSV for numerical comparisons. A fixed random
seed makes the layout reproducible in the same dependency environment.

Alternative input and output paths can be provided with `--input` and
`--output-dir`.

## Pre-reading selection

`prereading_titles.txt` lists the three tales selected in **Pre-Lecture Readings
LDA.pdf**: *Cat and Mouse in Partnership*, *Rapunzel*, and *The Mouse, the Bird,
and the Sausage*. The subset uses the Kaggle story text, which can differ in
wording from the versions printed in the PDF. The PDF supplies the selection;
its introductory instructions, titles, and author credits are not counted.

Generate the subset with the same styling and preprocessing:

```sh
uv run python lecture-content/overview/grimms_wordcloud.py \
  --titles-file lecture-content/overview/prereading_titles.txt \
  --output-dir lecture-content/overview/pre-reading
```

The resulting PNG, SVG, and frequency CSV are in `pre-reading/`, keeping the
full-corpus outputs separate. Selection matches whole titles without regard to
case and requires exactly one nonempty document per requested title.
