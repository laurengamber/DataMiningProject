# November 25 follow-up experiments

These artifacts extend the selected full-corpus comparison without replacing its exports. Corpus identity is `c73293f76ba4b0a18d685e5724f75b1123a86c9012497fc324090989642a8f99`; full-corpus selections remain `lda_k40_s42` and `n30_c25_s42`.

| Artifact | Purpose |
| --- | --- |
| `lda_full_s{42,7,21}/` | New selected-configuration fits, assignments, top terms, coherence, vocabulary, timing and provenance; large component/mixture arrays stay local |
| `bertopic_full_s42_timing/` | New selected-configuration fit using validated cached embeddings; stage measurement, not historical runtime |
| `split_ids.csv`, `split_strata.csv`, `split_protocol.json` | Reproducible publication/year split and singleton policy |
| `lda_split_s42/`, `bertopic_split_s42/` | Training-only vocabularies/fits; held-out reference coherence; held-out assignments |
| `split_metrics.csv`, `split_topic_proportions.csv`, `split_publication_shifts.csv` | Split results, assigned/outlier denominators, training/held-out distributions |
| `sensitivity_summary.csv`, `principal_theme_sensitivity.csv` | LDA seed and five BERTopic alternative comparisons against the selected full-corpus reference |
| `lda_seed/`, `bertopic_grid/` | Shared maximum-overlap matching, all overlap edges, unmatched topics, split/merge diagnostics and publication changes |
| `shared_period/` | Coverage-driven common period, retained IDs/outlets/date ranges/counts, and restricted existing-fit shares |
| `new_stage_timings.csv` | New measurements; separate stages and cache conditions in each manifest |
| [label_review/](label_review/README.md) | 110-topic naming review: batch index, decision ledger (`team_decisions.csv`), reservation attestation, and local full-text cards |
| [audit_review/2026-11-25/](audit_review/2026-11-25/README.md) | New dated 30-article corpus audit (complete); original PR2 judgments unavailable |

The split is an **exploratory robustness check**, not untouched testing. Full-corpus development previously influenced settings and stopword choices. Training-only vocabularies, LDA, UMAP and clustering are fitted with the selected configurations held fixed; pretrained embeddings are reused. Near duplicates and syndicated stories can cross the split. The human sample is reserved from naming, not unsupervised fitting.

Topic matching maximizes shared article counts one-to-one; it does not establish semantic equivalence. Read matched keywords and retention/purity alongside the complete split/merge edges. Main publication-change summaries use outlets with at least 50 full-corpus articles, all articles in denominators, and only matched topics. Report omitted/unmatched topics too. Shared-period results restrict existing assignments; they do not refit temporal models. Vice and Vice News remain distinct.

New wall-clock measurements record software, CPU architecture, thread pools and cache conditions. The existing hardware record identifies an Apple M5 with 16 GiB RAM and 10 logical CPUs. Fitting processes run serially with thread pools capped at one; lightweight reporting and a test run overlapped portions of the LDA seed work. These are individual executions, not isolated repeated benchmarks. BERTopic's first new fit may include JIT warmup, and embeddings are cached. Evaluation tasks differ (LDA includes perplexity). No end-to-end speed ranking is justified.

Run from the repository root:

```sh
MPLBACKEND=Agg OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python final-project/code/comparison/robustness.py lda
MPLBACKEND=Agg OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=1 .venv/bin/python final-project/code/comparison/robustness.py modern
MPLBACKEND=Agg .venv/bin/python final-project/code/comparison/robustness_reports.py
.venv/bin/python final-project/code/comparison/prepare_label_review.py
MPLBACKEND=Agg .venv/bin/python final-project/code/modern-methods/verify_notebooks.py --execute robustness
PYTHONPATH=final-project/code/modern-methods:final-project/code MPLBACKEND=Agg .venv/bin/python -m unittest discover -s final-project/code/modern-methods/tests -v
```

Completed experiment directories are checksum-bound and reused only with matching input/code identities; a changed identity or incomplete output stops execution. Reporting code is separate from fitting code, and none of these scripts write the original full-corpus models, labels, reservation or reviewer answers.

Mary Kate approved all 110 topic labels in assisted naming review; these are naming decisions, not independent fit ratings. Independent ratings remain pending. See the [PR3 results notes](../../../../../progress-report-3/pr3-results-notes.md) for findings.
