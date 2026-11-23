# Compare the methods

[pipeline_comparison.ipynb](pipeline_comparison.ipynb) brings together the BERTopic, LDA, and human-review results planned in [PR2](../../progress-report-2/pr2-submission.tex).

## When to run it

Run modern notebooks 01–03, record our model choice, and add Laura's four LDA exports. The comparison notebook uses those saved results without refitting the models. Missing files show as pending; files that do not match the dataset or selected runs cause an error.

We can compare the numerical results before topic naming or human review is finished. Once both sets of labels are final, run the notebook to prepare the review files. After both reviewers finish, set `RUN_HUMAN_SUMMARY = True` and rerun it to add their scores.

From the repository root:

```sh
uv run python final-project/code/modern-methods/verify_notebooks.py --execute comparison
```

## What we compare

- Coherence, keyword diversity, vocabulary coverage, and the share of unassigned articles.
- Top-ten-word Jaccard overlap, with LDA topics in rows and BERTopic topics in columns. Best matches include ties.
- How often the models assign the same articles to each pair of topics.
- Topic shares by publication, using heatmaps and complete CSV tables.
- Recorded runtimes, with the hardware and stages included.
- Each reviewer's mean score, exact agreement, agreement within one point, and quadratic-weighted kappa with a 1,000-resample bootstrap interval.

Unassigned BERTopic articles are excluded from fit scores and agreement, and discussed separately. The notebook includes questions to help us interpret the tables and write the report.

## File locations

Paths below are relative to `../modern-methods/`:

| Path | Contents |
| --- | --- |
| `Results/classical/` | Laura's `assignments.csv`, `terms.csv`, `topics.csv`, and `manifest.json`; see the [required format](../modern-methods/notebooks/README.md#lauras-handoff) |
| `Results/modern/` | Reserved review sample, modern runs, model choice, and topic labels |
| `Results/comparison/<modern-run>/` | Comparison tables, PNG/PDF figures, runtime details, and report checklists |
| `Results/comparison/<modern-run>/human_review/` | Review packet and separate answer CSVs |
| `Results/comparison/status.json` | Current inputs and pending work; check this before using older results |

The saved manifests check that the outputs use the same data and model runs. Rerunning keeps existing reviewer answers and stops if the review inputs have changed. Full article text and individual answers are ignored by Git.

Use [reviewer 1](../human-review/reviewer_1.ipynb) and [reviewer 2](../human-review/reviewer_2.ipynb) for independent ratings. The [coordinator notebook](../human-review/review_coordinator.ipynb) checks progress and summarizes the reviews.

Modern notebook 03 covers modern results only. This notebook covers the comparison. Held-out testing and comparisons over shared date ranges are still planned for the final report.
