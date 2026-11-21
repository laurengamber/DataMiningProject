# Modern topic-modeling notebooks

Use the repository environment (`uv sync`, then `uv run jupyter lab`) and run these notebooks in order:

1. **01_corpus_and_embeddings.ipynb** reconstructs the 7,332-article corpus, reserves the independent review sample, and builds or validates full-text GTE-small embeddings.
2. **02_modern_topic_modeling.ipynb** runs six BERTopic configurations, exposes their metrics and development examples, accepts a documented team model choice, and runs seeds 7 and 21 for that choice.
3. **03_evaluation_and_comparison.ipynb** exports publication results for every grid run, selected-model evidence when available, LDA comparisons when supplied, and human evaluation when genuinely completed.

The notebooks contain the model construction, experiment loops, and analysis. `src/topic_helpers.py` handles embedding/cache mechanics and common model metrics; `src/artifacts.py` handles validated run artifacts and editable labels. `shared/` contains corpus and cross-pipeline evaluation utilities. The two old command-line entry points now execute the corresponding notebooks, so there is no separate experiment implementation.

From the repository root:

```sh
uv run python final-project/code/modern-methods/verify_notebooks.py
uv run python final-project/code/modern-methods/verify_notebooks.py --execute 01 02 03
PYTHONPATH=final-project/code/modern-methods uv run python -m unittest discover -s final-project/code/modern-methods/tests -v
```

Validation checks notebook schemas and Python compilation; `--execute` uses fresh kernels and saves actual outputs. `--execute 01 --skip-embeddings` is an explicitly partial audit check. `--timeout` sets the per-cell limit (default 1,800 seconds). Fresh kernels need local Jupyter ports. Initial model download needs network access; later use can be offline. GTE-small uses MPS when available, otherwise CPU. A completed compatible embedding matrix can be read on either device without loading the encoder. The optional 200-article pilot is off by default.

## Data and artifact identities

The only raw input is repository-root `data/self_driving_articles.csv`. Shared corpus output remains `final-project/data/corpus.csv`, preserving Laura's imports and manifest contract. Duplicate bodies keep the earliest date, breaking ties in source order. The expected corpus hash is `c73293f76ba4b0a18d685e5724f75b1123a86c9012497fc324090989642a8f99`.

Paths below are relative to `final-project/code/modern-methods`:

- `Results/modern/review_sample.json`: reserved IDs, eligible population, known prior-review exclusions, seed, and corpus hash. Share this with Laura before her development review.
- `Results/modern/cache/`: pinned encoder and resumable article embeddings; ignored by Git.
- `Results/modern/runs/<run>/`: immutable fit outputs, metrics, per-topic coherence, three nonreserved development examples per topic, inventories, and publication matrices.
- `Results/modern/selection.json`: the team's editable choice and rationale.
- `Results/modern/selected/<run>/`: editable labels, selected publication outputs, stability, topic matches, and publication-share changes across seeds.
- `Results/comparison/<modern-run>/`: validated LDA comparison and independent review outputs.
- `Results/modern/pr3_evidence_checklist.csv` and `completion_plan.csv`: manuscript evidence and remaining-work handoffs. The manuscript itself is never edited.

Run manifests bind the corpus, embedding matrix, vocabulary, configuration, executable fitting/helper code, review reservation, package versions, and artifact checksums. Mismatches fail rather than silently reusing a stale run. To deliberately change an experiment, preserve the old run and its selection/review artifacts outside the active output directory before rerunning. Do not copy legacy pickle files into the current run directory. Only load trusted local model files.

Small tables, figures, and manifests can be committed; models, caches, full article representatives, and individual full-text review packets stay ignored. The old `final-project/modern-methods` artifacts are historical and remain untouched.

## Team model selection and topic naming

After notebook 02 finishes its grid, review `experiments.csv`, per-topic coherence, size plots, and each run's `representatives.csv`. Examples are the nearest articles to each topic's embedding centroid among nonreserved articles. Inspect large, small, and weak topics. They are development evidence, not a random quality estimate.

Edit `Results/modern/selection.json` and fill:

```json
{
  "corpus_hash": "c73293f76ba4b0a18d685e5724f75b1123a86c9012497fc324090989642a8f99",
  "run_id": "",
  "rationale": "",
  "selected_by": ""
}
```

Use a completed seed-42 run ID and explain the balance of coherence, coverage, granularity, and article support. Then rerun notebook 02. It reuses the grid, fits seeds 7 and 21, and creates `selected/<run>/topic_labels.csv`.

For every non-outlier topic, fill `proposed_label`, `evidence_notes`, and `confirmed=true` after team review. `evidence_ids` must refer to that topic's supplied development representatives. Do not use reserved articles for naming. Unconfirmed names remain provisional; reruns preserve manual edits. Existing assistant-suggested selection ratings are never treated as independent human scores or used for automatic selection.

## Laura's handoff

Supply these files under `Results/classical/`:

| File | Required content |
| --- | --- |
| `assignments.csv` | `article_id` as string, `model=lda`, one `run_id`, integer `topic_id`; exactly one dominant assignment per shared article |
| `terms.csv` | `topic_id`, 1-based integer `rank`, unigram `term`, finite `weight`; at least ten ranked terms per topic |
| `topics.csv` | unique `topic_id`, `label`, `count`; counts match dominant assignments, including zero-count topics if any |
| `manifest.json` | matching `corpus_hash`, model parameters/seeds, software/hardware, metrics, and available stage `timings` |

Retain LDA mixtures separately. No LDA code or model choice is changed here. The shared coherence reference uses the existing common tokenizer/English stopwords; each pipeline can retain its own representation vocabulary. Report coverage rather than assuming identical modeling vocabularies.

Quantitative comparison needs the four valid exports. Human review additionally needs `labels_confirmed: true` and `review_reservation_hash` equal to `shared.corpus.digest(reservation)` in Laura's manifest. Those fields attest that her labels are frozen and the shared reserved articles were not development evidence. This extra attestation is optional for quantitative comparison, required for joint human review.

## Independent human evaluation

Both models and their labels must be frozen before creating the paired packet. The same 100 reserved articles appear for both models, in randomized within-article model order. The packets identify the models and are **not blinded**. Two reviewers work independently using `human_review/rubric.txt` and separate `reviewer_1.csv` and `reviewer_2.csv` files. Fill the 1–5 fit rating and true/false relevance/ambiguity flags. Leave outlier fit ratings blank; inspect them qualitatively.

Rerun notebook 03 after both files are complete. It validates the entire roster against the frozen packet, reports means, exact/within-one agreement, quadratic-weighted kappa, and a 1,000-resample paired-article bootstrap interval. Undefined kappa and degenerate resamples are reported explicitly. Missing ratings remain pending. The 100 articles are independent of development review, not held out from unsupervised fitting.

## Interpretation and PR3 boundaries

Publication CSVs contain all outlets and topics. Figures show outlets with at least 50 articles and the 15 largest topics plus outliers. Denominators include every article within an outlet, so displayed subsets may sum below one. Keyword labels are provisional until confirmed.

Seed ARI excludes articles unassigned in either run, and the evaluated count/fraction is reported. Maximum-overlap one-to-one topic matches support publication comparisons; complete overlap matrices expose unmatched topics and splits/merges. A split/merge flag requires at least two overlaps each representing at least 10% of the source/target topic. These are descriptive flags, not significance tests.

Runtime reports combined UMAP/HDBSCAN/representation time and separate evaluation time. Embedding compute and model load/download are reported separately; an externally pre-downloaded model means model-loading time is not a cold download measurement. Do not invent missing LDA timings or compare unmatched stage boundaries.

Held-out evaluation and shared-period sensitivity remain final-report work. Singleton publication/year strata preclude strict stratification into both partitions; set a rare-stratum policy first. Genuine held-out evaluation requires training-only preprocessing, vocabulary, selection, and fitting. Do not call this exploratory full-corpus analysis test performance.

The notebooks do not establish PR2 feedback compliance or fabricate dates, ratings, labels, or findings. The completion table identifies owners and outputs with dates left for team confirmation. Disclose substantive AI assistance with implementation and planning; human research decisions and independent ratings remain the team's responsibility.
