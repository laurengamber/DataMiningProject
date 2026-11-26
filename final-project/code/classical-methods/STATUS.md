# Classical analysis and PR #16 validation — November 26, 2026

All three conflicts were resolved with the incoming `main` versions of `export.py`,
`interpret.py`, and `main.py`. Those files remain identical to incoming commit `f3474af`.
The nonconflicting notebook workflow remains available, with its support functions in
`notebook_artifacts.py` and `notebook_interpret.py`.

## Selected model rerun

The selected CLI pipeline uses `selected_configuration.json`: K=40, seed 42, 50 batch
iterations, document-topic prior 0.1, and topic-word prior 0.025. It was rerun on all
7,332 articles, including the seed-7 and seed-21 stability fits.

- All dominant assignments, topic counts, keyword ordering, and representative article IDs
  reproduce the checked-in `classical-methods/results/` reference.
- Seed ARIs remain 0.3230332180 (7) and 0.3468972677 (21), evaluated on all 7,332 articles.
- Probability values differ only at floating-point scale: maximum absolute difference
  1.5944e-12 across the full mixture table; top-term weight differences are at most 1.10e-15.
- The saved reference exports were preserved. The fresh CLI exports are in
  `../modern-methods/Results/classical/`. Byte-level hashes differ for some numeric files,
  so existing approved-label and frozen-review bindings must continue using their saved sources.

## Effect on the current comparison and report findings

A separate checkout of `mkc/model-comparison` at `f348d95` was validated first with its
original exports and copied review files, then with the new refit in a separate comparison
directory. Both comparison and robustness-report notebooks executed in fresh kernels.

All 13 checked comparison tables match exactly: model and per-topic coherence, top-word
Jaccard overlap, best lexical matches, assignment contingency, matched publication shares,
and complete publication counts, proportions, and sample sizes. All 76 robustness CSVs
match the saved analysis after rebuilding its reports. No numerical report conclusions
need to change because of this merge. The incoming manuscript’s outdated final-model
methods paragraph was corrected to 50 iterations and the selected priors; its
pre-existing historical outline is otherwise retained.

| Model | Topics | Mean c_v | Keyword diversity | Unassigned fraction |
| --- | ---: | ---: | ---: | ---: |
| BERTopic `n30_c25_s42` | 70 | 0.704696 | 0.651429 | 0.180442 |
| Selected LDA `lda_k40_s42` | 40 | 0.655233 | 0.710000 | 0 |

All 21 review files, including frozen inputs and independent answer files, remain
byte-for-byte unchanged in both the original checkout and the isolated baseline.
The refit was not promoted into approved labels or a new frozen packet.

PR #16 itself still has a blank modern selection record. Its comparison notebook executes
successfully and reports the selected LDA input ready and the modern choice pending.
This branch-specific status does not revoke the choices or labels on `mkc/model-comparison`.

## Separate exploratory notebook grid

The three classical notebooks retain the original seven-setting, 100-iteration experiment
with symmetric 1/K priors. Its artifacts now live in
`../modern-methods/Results/classical_exploration/`, separate from the selected CLI handoff.
Run IDs can coincide across these experiments; directory and manifest parameters distinguish them.
All seven configurations were refitted from the notebook fitting code. The notebooks
then completed in fresh kernels, verifying completed runs and rebuilding publication exports.

| K | Mean c_v | Keyword diversity | Training perplexity | New fit seconds |
| --- | ---: | ---: | ---: | ---: |
| 10 | 0.649574 | 0.850000 | 3499.190 | 129.3 |
| 20 | 0.634264 | 0.780000 | 3312.900 | 146.6 |
| 30 | 0.629560 | 0.763333 | 3253.467 | 153.9 |
| 40 | 0.654585 | 0.707500 | 3223.659 | 169.1 |
| 50 | 0.649019 | 0.724000 | 3191.670 | 185.2 |
| 60 | 0.651515 | 0.720000 | 3202.432 | 186.6 |
| 70 | 0.649463 | 0.700000 | 3226.589 | 218.6 |

The scientific tables reproduce the original PR grid within absolute tolerance 1e-10.
Fit and evaluation times are newly measured; they are not a controlled hardware benchmark.
Training perplexity is an LDA diagnostic, not held-out performance or a cross-method score.
The exploratory selection remains blank; no new team choice or human label was invented.

## Verification

- All 37 tests pass: eight classical tests and 29 modern/comparison/review tests.
- All registered notebooks validate for structure and Python syntax.
- Three classical notebooks and PR #16's comparison notebook execute in fresh kernels.
- The current comparison and robustness reports execute with both original and refitted inputs.
- All seven exploratory runs pass implementation-identity and artifact-hash verification,
  exact article alignment, normalized-mixture and dominant-assignment checks, topic-count
  reconciliation, reserved-example separation, and publication-denominator checks.
- Comparison and exploratory heatmaps/topic-size figures were visually reviewed.
- The corrected PR3 manuscript compiles successfully with `latexmk`; the selected-model
  settings and seed results were checked in the compiled text.
- The 100-article reservation, approved topic labels, frozen review packets, and user checkout
  are preserved. Independent human ratings remain pending.

Machine-readable evidence is in
[`Results/pr16_validation/`](../modern-methods/Results/pr16_validation/):
`selected_model.json`, `comparison.json`, and `exploration.json`.
See [README.md](README.md) for the selected pipeline and separate notebook commands.
