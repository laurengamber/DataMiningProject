# Implementation and execution status

All project notebooks, helpers, tests, and outputs live here. Dependencies remain in the repository-level uv environment.

Completed: corpus audit, 200-article pilot, full 7,337-article embeddings, offline cache reuse, and all six seed-42 experiment fits. All primary topic terms have full coverage in the shared coherence dictionary.

| Neighbors | Minimum cluster size | Topics | c_v coherence | Outliers | Cosine silhouette |
|---:|---:|---:|---:|---:|---:|
| 15 | 25 | 70 | 0.701 | 17.1% | 0.095 |
| 15 | 50 | 39 | 0.661 | 19.2% | 0.126 |
| 15 | 100 | 24 | 0.635 | 21.0% | 0.111 |
| 30 | 25 | 71 | 0.706 | 18.5% | 0.121 |
| 30 | 50 | 34 | 0.652 | 18.0% | 0.120 |
| 30 | 100 | 24 | 0.632 | 21.8% | 0.130 |

These are exploratory results, not a selected final model. Silhouette excludes outliers; topic numbers identify clusters within a run and do not align across runs.

## Required next inputs

1. Read representative articles for the three shortlisted runs and fill both 1–5 rating columns plus notes in `output/modern/selection_review.csv`.
2. Resume notebook 02 at model selection. It runs seeds 7 and 21 and representation comparisons, then creates `topic_labels.csv` for manual labels and evidence notes.
3. Run notebook 03 for selected-model evaluation and publication exports. Supply Laura’s four classical artifacts under `output/classical/` to enable joint comparison.
4. Two team members complete the independent review CSVs, then rerun the human evaluation cells.

No human ratings, final topic names, or classical results have been fabricated. Final selected-model evaluation and downstream notebook cells remain pending these inputs. See `notebooks/README.md` for execution commands, handoff schemas, limitations, and deadlines.
