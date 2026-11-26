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

The individual reviewer notebooks provide the 1–5 rubric, article display, commented answer-entry cells, save/correction controls, and resumable progress. `../human-review/review_coordinator.ipynb` handles preparation, progress counts, combined results, and interpretation. Each reviewer uses a separate ignored personal workbook and their own answer CSV. No genuine ratings or model selection have been supplied.

The notebook's default pending-input path executed successfully in a fresh kernel. Five additional tests exercise entry, resuming, corrections, stale edits, packet identity, outliers, separation of reviewer files, the notebook's item-number guard, and compatibility with the existing summary. The full suite now passes 21 tests. The original three analysis notebooks and study results are unchanged by this addition.

## Separate reviewer notebooks — November 22, 2026

Human-review notebooks now live in `../human-review/`. The shared notebook has been renamed and refocused as `review_coordinator.ipynb`. New `reviewer_1.ipynb` and `reviewer_2.ipynb` are preconfigured for their respective answer CSVs and contain only the independent reading, rating, saving, and progress steps. Combined-score and team-interpretation cells remain in the shared notebook.

The full suite passes 22 tests, including six reviewer-workflow tests checking that each new notebook saves only its own reviewer file and resumes existing answers. Both new notebooks executed in fresh kernels with their safe pending-input defaults. The existing three analysis notebooks, saved study outputs, and PR3 manuscript were preserved. The validation command now follows the new folder layout and accepts `--execute reviewer_1 reviewer_2`.

## Coordinator notebook refocused — November 22, 2026

`../human-review/review_coordinator.ipynb` now contains only coordinator work: preparation instructions, packet lookup, aggregate completion counts, explicitly enabled combined results, interpretation notes, and PR3 handoff. Individual article display and answer entry remain in the two reviewer notebooks. Reviewer code and saved outputs, answer files, analysis notebooks, and the manuscript were preserved.

The coordinator notebook executed successfully in a fresh kernel with pending inputs, and the full suite passes 23 tests. The additional coordinator test covers read-only progress, incomplete/missing submissions, explicit summary generation after completion, and unchanged original reviewer files. Use `--execute coordinator`; the old `--execute 04` command remains an alias.

## Joint comparison moved to its own notebook — November 22, 2026

`../comparison/pipeline_comparison.ipynb` now owns the PR2 cross-method evaluation: shared coherence/diversity, top-ten Jaccard overlap and ties, assignment contingency, both publication heatmaps and matched shares, measured runtime context, frozen review packets, and the combined quantitative/human table. Modern notebook 03 now exports only modern inventories, publication results, and its modern evidence/completion tables. Reviewer and coordinator instructions point to the new notebook.

Existing `Results/classical/` and `Results/comparison/<run>/human_review/` paths remain unchanged. The new notebook validates exported artifacts without loading model pickles or embeddings, preserves reviewer answers, and rejects mismatched comparison identities. Use `verify_notebooks.py --execute comparison`. Model selection, LDA exports, confirmed labels, and genuine ratings are still pending; no current joint empirical findings are claimed.

All 28 tests pass. Modern notebook 03 and the new comparison notebook executed in fresh kernels with the actual available inputs. A separate fresh-kernel execution on temporary synthetic exports and ratings exercised the complete comparison path; those fixture ratings were never written to study outputs. The classical implementation, modern fitting helpers, six fitted runs, and PR3 manuscript are unchanged.

## Current status — November 26, 2026

Mary Kate selected `n30_c25_s42`; seeds 7 and 21 are complete. The comparison reads LDA directly from `../classical-methods/results/` without modifying it.

| Model | Topics | Mean c_v | Keyword diversity | Unassigned | Seed ARIs (fraction compared) |
| --- | ---: | ---: | ---: | ---: | --- |
| BERTopic `n30_c25_s42` | 70 | 0.705 | 0.651 | 18.0% | 0.961 (77.7%), 0.976 (77.4%) |
| LDA `lda_k40_s42` | 40 | 0.655 | 0.710 | 0% | 0.323, 0.347 (all articles) |

Comparison outputs are in `Results/comparison/n30_c25_s42/`. The robustness follow-up (LDA seeds, six-setting BERTopic sensitivity, shared-period coverage, exploratory 80/20 split, new stage timings) is in [Results/robustness/2026-11-25](Results/robustness/2026-11-25/README.md).

Mary Kate approved all 110 labels in assisted naming review ([decision ledger](Results/robustness/2026-11-25/label_review/team_decisions.csv)) and attested that the reserved 100 articles were not used for naming. Modern labels are in `Results/modern/selected/n30_c25_s42/topic_labels.csv`; LDA names are comparison-only, in `Results/comparison/n30_c25_s42/classical_labels.csv`. The 100-article review packet is frozen with blank answer files in `human_review/handoff/`. A new dated 30-article corpus audit is complete; the original PR2 audit judgments are unavailable.

Still pending: two independent reviewer submissions and the team's interpretation. See the [PR3 results notes](../../progress-report-3/pr3-results-notes.md) for findings, limitations and reproduction commands.
