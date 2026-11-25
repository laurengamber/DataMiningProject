# Classical analysis status — November 23, 2026

The three-notebook workflow and its supporting implementation are complete. All three notebooks
have executed successfully in fresh kernels on the verified 7,332-article corpus. Preprocessing
reproduces 21,528 terms, 98.97% sparsity, and zero empty articles. All seven seed-42 LDA fits
are complete at 100 iterations, with the existing fixed symmetric priors of 1/K.

| K | Mean c_v | Keyword diversity | Training perplexity | Fit seconds |
| --- | ---: | ---: | ---: | ---: |
| 10 | 0.650 | 0.850 | 3499.2 | 134.0 |
| 20 | 0.634 | 0.780 | 3312.9 | 150.2 |
| 30 | 0.630 | 0.763 | 3253.5 | 160.4 |
| 40 | 0.655 | 0.708 | 3223.7 | 170.2 |
| 50 | 0.649 | 0.724 | 3191.7 | 182.4 |
| 60 | 0.652 | 0.720 | 3202.4 | 186.9 |
| 70 | 0.649 | 0.700 | 3226.6 | 206.2 |

Full precision and original measured stage timings are in `../modern-methods/Results/classical/experiments.csv`
and each run manifest. All top terms have full coverage in the common coherence reference.
These are full-corpus exploratory results, not held-out performance. Training perplexity does
not rank LDA against BERTopic. This is a new 100-iteration grid; historical PR2 results from
a 20-iteration grid and the earlier K=40 selection are not reused as new findings.

Every run includes assignments, all topic mixtures, top terms, per-topic coherence, inventories,
nonreserved development examples, topic-size figures, and publication tables/figures. Tables
cover all 25 publications and all topics, including zero-count topics. The main heatmaps show
16 publications with at least 50 articles. Names remain provisional keyword labels.

## Verification

- All 36 tests passed: seven classical tests and 29 modern/comparison/review tests.
- All seven real runs passed file-hash and implementation-identity verification, exact article
  alignment, normalized-mixture and dominant-assignment checks, topic-count reconciliation,
  reserved-example separation, and publication-denominator checks.
- All three classical notebooks executed without errors in fresh kernels. Notebook structure
  and Python syntax were validated across the project. K=10 and K=70 figures were visually inspected.
- Real synthetic LDA fixtures exercised serialization, scoring recovery, seed checks, label
  preservation, provisional and confirmed handoffs, the joint comparison, and frozen-review
  preservation. Synthetic fixtures remained in temporary directories and are not study findings.
- Comparison integration also checks declared export hashes, displays exported classical seed
  results, and retains zero-count classical topics in complete publication tables.

## Pending team decisions

The shared 100-article review reservation is unchanged. No team choice, confirmed topic names,
selected-model empirical seed results, or genuine human ratings have been supplied. The selection
record is intentionally blank, and no selected root-level handoff has been fabricated.

1. Review the metrics and nonreserved articles, then record a choice, rationale, and selector
   in `../modern-methods/Results/classical/selection.json`.
2. Rerun notebook 02 to reuse the grid and fit the selected configuration with seeds 7 and 21.
3. Confirm topic names with development evidence, then run notebook 03 to publish the validated handoff.
4. Complete modern selection and naming, run the comparison notebook, and collect independent ratings.

Changed exports cannot overwrite an active comparison binding. Preserve provisional comparisons
before publishing revised exports; never overwrite frozen review packets or answers. See the
[workflow and handoff instructions](README.md). Held-out testing, shared-date sensitivity,
manuscript revisions, and final thematic interpretation remain follow-up work.
