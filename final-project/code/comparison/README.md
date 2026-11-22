# Pipeline comparison

[pipeline_comparison.ipynb](pipeline_comparison.ipynb) implements the comparison in [PR2](../../progress-report-2/pr2-submission.tex). It compares BERTopic and LDA using the same corpus and adds the independent human evaluation of each model.

Run the modern notebooks 01–03, document the team model choice, and supply Laura's four exports. Run this notebook before independent review to prepare packets after both label sets are confirmed. After both reviewers submit, rerun it with `RUN_HUMAN_SUMMARY = True` to refresh the combined table. Missing inputs remain pending; invalid artifacts fail validation. The notebook reads exports without loading fitted models or embeddings.

```sh
uv run python final-project/code/modern-methods/verify_notebooks.py --execute comparison
```

The comparison covers shared/per-topic coherence, vocabulary coverage, keyword diversity, outlier frequency, top-ten Jaccard overlap (LDA rows, modern columns), best matches with ties, article-assignment contingency, both publication heatmaps, and matched publication shares. Runtime tables preserve measured stages and hardware context. Human summaries report reviewer means, denominators, exact/within-one agreement, quadratic-weighted kappa, and a 1,000-resample interval; modern outliers are reviewed separately.

For compatibility, the existing paths remain relative to `../modern-methods/`:

- `Results/classical/`: Laura's `assignments.csv`, `terms.csv`, `topics.csv`, and `manifest.json`. See the [handoff schema](../modern-methods/notebooks/README.md#lauras-handoff).
- `Results/modern/`: common review reservation, selected modern run, label table, and measured artifacts.
- `Results/comparison/<modern-run>/`: comparison identity, metrics, CSV matrices, PDF/PNG figures, `pipeline_comparison.csv`, runtime context, and evidence/completion checklists.
- `Results/comparison/<modern-run>/human_review/`: frozen packet and separate reviewer CSVs. These remain ignored; reruns preserve answers and reject changed freezes.
- `Results/comparison/status.json`: current input status even when no modern model is selected. Check it before using older run outputs.

Use [reviewer 1](../human-review/reviewer_1.ipynb) and [reviewer 2](../human-review/reviewer_2.ipynb) independently; use [review_coordinator.ipynb](../human-review/review_coordinator.ipynb) for progress and qualitative interpretation. No scores are generated. The numeric comparison can finish before labels or human ratings are supplied.

Modern notebook 03 now owns only modern topic inventories, publication exports, and its own evidence checklist. This notebook owns the joint comparison. Neither edits the PR3 manuscript. Model choice, labels, independent ratings, and substantive interpretation remain team decisions; held-out and shared-period analyses remain final-report work.
