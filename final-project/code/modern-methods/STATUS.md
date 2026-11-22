# Modern analysis status — November 21, 2026

The three notebook rewrites are implemented. All three have run in fresh kernels on the corrected 7,332-article corpus. The 7,332 normalized full-text embeddings and all six standard BERTopic seed-42 fits are complete. The shared corpus hash matches the existing manifest exactly.

| Run | Topics | Mean c_v | Unassigned | Cosine silhouette |
| --- | ---: | ---: | ---: | ---: |
| n15_c25_s42 | 76 | 0.692 | 20.2% | 0.114 |
| n15_c50_s42 | 40 | 0.662 | 19.9% | 0.119 |
| n15_c100_s42 | 21 | 0.641 | 14.6% | 0.105 |
| n30_c25_s42 | 70 | 0.705 | 18.0% | 0.122 |
| n30_c50_s42 | 35 | 0.646 | 19.1% | 0.123 |
| n30_c100_s42 | 24 | 0.630 | 22.2% | 0.134 |

Full precision, timing, and provenance are in `Results/modern/experiments.csv` and each run's manifest. All top terms have full coverage in the common coherence reference. Silhouette excludes outliers and samples at most 2,000 assigned articles. These are full-corpus exploratory results, not held-out performance.

Every grid run has a topic inventory, development examples, size plots, publication counts/proportions for all 25 outlets, and publication figures for the 16 outlets with at least 50 articles. Labels are provisional keyword labels. Results from the old 7,337-article runs are not reused.

## Explicit team decisions and pending inputs

The user requested that **model selection remain pending for team article review**. `Results/modern/selection.json` is intentionally unfilled. No automatic selection, final thematic interpretation, or selected-model seed result is claimed.

1. Review run metrics and nonreserved representative articles, then record the chosen run, rationale, and team selector in `selection.json`.
2. Rerun notebook 02 to fit the selected configuration with seeds 7 and 21, export matched publication comparisons, and create its label table.
3. Confirm topic names with article evidence. Existing human edits are preserved across reruns.
4. Laura supplies the four LDA exports. Joint human review additionally needs confirmed classical labels and the shared review-reservation attestation.
5. Two team members independently complete the review packets. Real ratings are not available yet; no independent human scores have been generated.

The 100-article sample is reserved before new development review. Audit-packet IDs and legacy development examples are excluded. Share `Results/modern/review_sample.json` with Laura before topic naming.

## Verification and boundaries

Sixteen tests passed, including a real synthetic-data BERTopic fit/serialization check, exact corpus reconstruction, cache/run rejection, reserved-example separation, label preservation, publication denominators, seed-label permutation, LDA alignment, review freeze/roster validation, outlier exclusions, and degenerate kappa/bootstrap cases. Synthetic fixtures live only in temporary test directories and are not project findings.

Fresh-kernel notebook execution covers the real complete-grid/pending-team-input path. Completed-review behavior is tested with temporary fixtures; no genuine completed team input exists to exercise the final joint notebook branch yet. Publication figure layout was visually inspected.

`pr3-submission.tex`, the classical implementation, and legacy model artifacts are untouched. The PR3 evidence checklist and completion-plan CSV identify remaining work; team completion dates and PR2 feedback are not invented.

Held-out evaluation and shared-period publication sensitivity remain final-report work. See the [notebook README](notebooks/README.md) for commands, schemas, rubric, interpretation limits, and the rare-stratum issue.

## Guided reviewer notebook

`notebooks/04_human_review.ipynb` now provides the coordinator prerequisite checklist, independent 1–5 rubric, one-item article display, commented answer-entry cells, explicit save/correction controls, resumable progress, and a coordinator-only summary and interpretation section. Each reviewer uses a separate ignored personal workbook and their own answer CSV. No genuine ratings or model selection have been supplied.

The notebook's default pending-input path executed successfully in a fresh kernel. Five additional tests exercise entry, resuming, corrections, stale edits, packet identity, outliers, separation of reviewer files, the notebook's item-number guard, and compatibility with the existing summary. The full suite now passes 21 tests. The original three analysis notebooks and study results are unchanged by this addition.
