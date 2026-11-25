# Modern topic-modeling notebooks

We use these notebooks to prepare the articles, fit BERTopic, and compare coverage across publications. From the repository root, run `uv sync` and then `uv run jupyter lab`.

## Notebook order

1. **01_corpus_and_embeddings.ipynb** prepares the 7,332 articles, reserves the human-review sample, and creates or loads the GTE-small embeddings.
2. **02_modern_topic_modeling.ipynb** fits six BERTopic settings, shows metrics and example articles, and runs seeds 7 and 21 after we choose a model.
3. **03_evaluation_and_comparison.ipynb** saves modern topic summaries and publication results. Despite its original filename, it now covers only the modern method.
4. **[pipeline_comparison.ipynb](../../comparison/pipeline_comparison.ipynb)** compares BERTopic with Laura's LDA results and prepares the human-review files once labels are final. Run it again after the reviewers finish to include their results.
5. **[reviewer 1](../../human-review/reviewer_1.ipynb)** and **[reviewer 2](../../human-review/reviewer_2.ipynb)** guide the independent ratings. The **[coordinator notebook](../../human-review/review_coordinator.ipynb)** checks progress and summarizes both reviews.

The model settings, loops, and analysis are in the notebooks. `src/topic_helpers.py` contains embedding and metric functions, `src/artifacts.py` manages saved results and labels, and `shared/` contains functions used by both methods. `run_embeddings.py` and `run_experiments.py` run the corresponding notebooks.

## Checks and execution

Run these from the repository root:

```sh
# Check notebook structure and Python syntax without running the analysis.
uv run python final-project/code/modern-methods/verify_notebooks.py

# Run the selected notebooks in fresh kernels and save their outputs.
uv run python final-project/code/modern-methods/verify_notebooks.py --execute 01 02 03
uv run python final-project/code/modern-methods/verify_notebooks.py --execute comparison

# Run the software tests.
PYTHONPATH=final-project/code/modern-methods uv run python -m unittest discover -s final-project/code/modern-methods/tests -v
```

`--execute 01 --skip-embeddings` runs only the data checks in notebook 01. `--timeout` sets the time limit per cell; the default is 1,800 seconds. Execution needs local Jupyter ports.

The first model download needs internet access. Later runs can use saved files offline. Embeddings use the Mac GPU through MPS when available, otherwise the CPU. Saved embeddings can be loaded on either device. The optional 200-article pilot is off by default.

## Data and saved results

The source file is `data/self_driving_articles.csv` at the repository root. Both methods use `final-project/data/corpus.csv`. For duplicate bodies, we keep the earliest-dated copy, using source order to break date ties. The expected corpus hash is `c73293f76ba4b0a18d685e5724f75b1123a86c9012497fc324090989642a8f99`.

Paths below start in `final-project/code/modern-methods`:

| Path | Contents |
| --- | --- |
| `Results/modern/review_sample.json` | Reserved article IDs, eligible articles, exclusions, seed, and corpus hash; share with Laura before topic naming |
| `Results/modern/cache/` | Saved embeddings and model files |
| `Results/modern/runs/<run>/` | Assignments, metrics, keywords, example articles, topic summaries, and publication tables |
| `Results/modern/selection.json` | Our model choice and reason |
| `Results/modern/selected/<run>/` | Topic labels, selected results, and seed comparisons |
| `Results/comparison/<modern-run>/` | Results from the comparison notebook and human review |
| `Results/modern/pr3_evidence_checklist.csv` and `completion_plan.csv` | Results ready for the report and remaining tasks |

Each run's manifest records its data, embeddings, settings, vocabulary, code version, package versions, review sample, and file hashes. These checks prevent mixing results from different runs. If changing an experiment, keep a separate copy of the old run and its labels/reviews before rerunning. Load only trusted local model files.

Small tables, figures, and manifests can go in Git. Models, embeddings, full article examples, and individual review files are ignored. Older results should remain separate from current runs.

## Choose a model and name the topics

The team selected `n30_c25_s42` on November 25, 2026. The
[current selection review](../selection_review/current_shortlist_review.md)
documents the recommendation and its limitations. Selected-model seed checks are
complete. Draft labels for both pipelines live in the comparison folder and are
summarized in the [PR3 notes](../../../progress-report-3/pr3-results-notes.md);
team-confirmed labels and independent ratings remain pending.

After notebook 02 finishes, read `experiments.csv`, the coherence results, topic-size plots, and each run's `representatives.csv`. The examples are articles closest to each topic's average embedding, excluding the reserved sample. Read small and weak topics as well as the largest ones. These examples help us choose and name topics; they are not a random evaluation sample.

Fill in `Results/modern/selection.json`:

```json
{
  "corpus_hash": "c73293f76ba4b0a18d685e5724f75b1123a86c9012497fc324090989642a8f99",
  "run_id": "",
  "rationale": "",
  "selected_by": ""
}
```

Choose a completed seed-42 run and explain how coherence, coverage, topic detail, and example articles support the choice. Rerun notebook 02 to reuse the grid results, fit seeds 7 and 21, and create `selected/<run>/topic_labels.csv`.

For each assigned topic, fill in `proposed_label` and `evidence_notes`, then set `confirmed=true` after team review. `evidence_ids` must use that topic's supplied example articles. Rerunning keeps these edits. Do not use reserved review articles for naming. Earlier AI-suggested selection scores are not independent human ratings.

## Laura's handoff

Save these four files in `../classical-methods/results/`:

| File | Required fields |
| --- | --- |
| `assignments.csv` | String `article_id`, `model=lda`, one `run_id`, and integer `topic_id`; one dominant assignment per shared article |
| `terms.csv` | `topic_id`, positive integer `rank`, single-word `term`, and finite `weight`; at least ten ranked terms per topic |
| `topics.csv` | Unique `topic_id`, `label`, and `count`; counts must match the assignments, including zero-count topics if any |
| `manifest.json` | Matching `corpus_hash`, settings/seeds, hardware/software, metrics, and any measured stage `timings` |

Keep LDA's full topic mixtures separately. The two methods can use different modeling vocabularies; coherence uses the same reference articles and tokenizer, and we report vocabulary coverage.

For human review, the manifest also needs `labels_confirmed: true` and `review_reservation_hash` equal to `shared.corpus.digest(reservation)`. These confirm that the labels are final and that the reserved articles were not used to choose names. The numerical comparison can run before these two fields are completed.

## Human evaluation

The [reviewer notebooks](../../human-review/README.md) explain how to read articles, enter scores, and save or resume. Both people review the same 100 reserved articles for both models. Model order is randomized within each article, but model names are visible, so the review is not blinded.

Use the 1–5 fit scale and relevance/ambiguity flags. Leave fit ratings blank for unassigned articles. Each person keeps a separate answer CSV and an ignored personal notebook copy inside the review folder. Wait until both people finish before discussing scores.

Then rerun [the comparison notebook](../../comparison/pipeline_comparison.ipynb) with `RUN_HUMAN_SUMMARY` enabled. It reports reviewer means, exact agreement, agreement within one point, and quadratic-weighted kappa with a 1,000-resample article bootstrap interval. Undefined kappa stays blank, and unusable resamples are counted. The sample was set aside from topic naming, not from model fitting.

## Interpreting the results

Publication CSVs include all outlets and topics. The main figures show outlets with at least 50 articles and the 15 largest topics plus unassigned articles. Shares use all articles from each outlet, so the displayed subset may add to less than 100%.

Seed ARI includes only articles assigned in both runs. Report the count and fraction compared too. Topics are matched across seeds by maximum shared article membership. The full overlap tables show unmatched topics and possible splits/merges. A split/merge flag requires two overlaps, each covering at least 10% of the source or target topic; it is a descriptive flag, not a significance test.

Fitting time combines UMAP, HDBSCAN, and keyword calculation. Evaluation, embedding, and model loading are timed separately. Loading an already downloaded model is not a measurement of download time. Compare LDA and modern runtimes only after checking their stages and hardware.

Held-out testing and comparisons over shared date ranges remain final-report tasks. Some publication/year groups have only one article, so we need a splitting rule. A held-out test must build the vocabulary, choose settings, and fit models using training data only.

We still need the actual PR2 feedback before writing a response to it. The completion table leaves dates for the team to confirm. We should document AI help with coding and planning separately from our model choices, interpretations, and independent ratings.
