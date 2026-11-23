# Classical topic-modeling notebooks

These notebooks reuse the classical preprocessing and scikit-learn LDA implementation, then
produce the artifacts consumed by the joint comparison. Run from the repository root in the
project's `uv` environment.

## Notebook order

1. **[01_corpus_and_representation.ipynb](notebooks/01_corpus_and_representation.ipynb)** verifies
   the shared 7,332-article corpus and existing review reservation, then creates or loads the
   sparse unigram count matrix. Run modern notebook 01 first to establish the reservation.
2. **[02_classical_topic_modeling.ipynb](notebooks/02_classical_topic_modeling.ipynb)** fits seven
   topic counts, displays metrics and inventories, and waits for team selection. After selection,
   rerun it for seeds 7 and 21 and the editable topic-label table.
3. **[03_classical_results_and_exports.ipynb](notebooks/03_classical_results_and_exports.ipynb)**
   exports publication summaries and, once selected, the validated comparison handoff.
4. Use the **[comparison notebook](../comparison/README.md)** after choosing both models. Confirm
   both sets of topic names before preparing the independent human-review packets.

The settings, loops, selection, and analysis are visible in the notebooks. `preprocessing.py`
and `representation.py` prepare counts; `lda.py` fits and scores models; `interpret.py` handles
mixtures, evidence, and labels; `export.py` validates caches and writes handoffs. `main.py` is a
thin fresh-kernel notebook runner. The older `run_grid` and `stability_check` functions remain
available for compatibility, but the notebooks provide resumable, provenance-checked execution.

## Experimental choices

- Shared corpus hash: `c73293f76ba4b0a18d685e5724f75b1123a86c9012497fc324090989642a8f99`.
- Existing English/custom stopwords, no lemmatization, numeric-only and short tokens removed.
- Unigram counts with `min_df=5`, `max_df=0.5`: 21,528 terms and no empty articles on this corpus.
- K = 10, 20, 30, 40, 50, 60, 70; seed 42; batch variational Bayes; `max_iter=100`; `n_jobs=1`.
- Fixed symmetric scikit-learn priors, alpha = eta = 1/K. Selected-model seed checks use 7 and 21.
- Top-ten unigram c_v coherence uses the same reference articles/tokenizer and 110-token window
  as BERTopic. Report per-topic scores, vocabulary coverage, and keyword diversity.
- Perplexity is measured on the fitting corpus. It is neither held-out performance nor a metric
  that can rank LDA against BERTopic. LDA probabilities and HDBSCAN strengths are different measures.

The reports describe an earlier 20-iteration grid, K=40 selection, and seed ARIs of 0.32–0.36.
No corresponding saved classical artifacts were present when this workflow was implemented.
This seven-setting **100-iteration grid is a new experiment**; the old results are historical
reported findings. K=40 is a candidate, not an automatic selection.

## Commands

```sh
uv run jupyter lab

# Structure and syntax checks for all analysis/review notebooks.
uv run python final-project/code/modern-methods/verify_notebooks.py

# Fresh kernels; the grid may take substantial time. Completed fits are checkpointed.
uv run python final-project/code/classical-methods/main.py
# Or run particular notebooks:
uv run python final-project/code/modern-methods/verify_notebooks.py --execute classical_01 classical_02 classical_03 --timeout 86400

# Headless tests: no interactive plot windows.
MPLBACKEND=Agg uv run python -m unittest discover -s final-project/code/classical-methods/tests -v
MPLBACKEND=Agg PYTHONPATH=final-project/code/modern-methods uv run python -m unittest discover -s final-project/code/modern-methods/tests -v
```

Jupyter execution requires local kernel ports. The timeout is per cell, and a grid cell can contain
several fits. A failed notebook retains failure evidence; do not treat partially executed notebooks
as complete. Reuse valid caches when resuming. Load only trusted locally generated model pickles.

## Saved artifacts and selection

All paths below are relative to `../modern-methods/Results/classical/`, retaining the comparison's
existing export destination.

| Path | Purpose |
| --- | --- |
| `cache/representation/` | Sparse counts, ordered vocabulary, article diagnostics, and identity manifest |
| `representation_summary.json`, `corpus_by_publication.csv` | Preparation and coverage summaries |
| `runs/lda_k<K>_s<seed>/` | Model, mixtures, assignments, terms, topic counts, coherence, evidence, and manifest |
| `experiments.csv` | Completed seed-42 grid metrics; updated after each completed run |
| `selection.json` | Team-selected run, rationale, selector, and corpus hash |
| `selected/<run>/` | Editable labels, inventory, publication results, and seed comparisons |
| `assignments.csv`, `terms.csv`, `topics.csv`, `manifest.json` | Selected handoff read by the comparison |
| `mixtures.csv` | Full selected article-topic probabilities, retained locally |
| `stability.csv` | Selected seed summary, included in the handoff when available |
| `status.json`, `evidence_checklist.csv` | Current readiness and remaining team work |
| `preparation_execution.json`, `execution.json` | Current execution/cache-loading information |

A complete run has a manifest and verified file hashes. A fit checkpoint can be reused if scoring
was interrupted. Changes to data, ordering, vocabulary, settings, code, reservation, or relevant
package versions reject stale caches. Preserve old runs separately before rebuilding. Small tables,
figures, and manifests can go in Git; matrices, models, full-text evidence, and full mixtures stay local.

After reviewing metrics and **nonreserved** development articles, fill in `selection.json`:

```json
{
  "corpus_hash": "c73293f76ba4b0a18d685e5724f75b1123a86c9012497fc324090989642a8f99",
  "run_id": "",
  "rationale": "",
  "selected_by": ""
}
```

Choose a completed seed-42 run. Explain coherence, topic granularity, redundancy, sizes, and article
evidence. Do not substitute an automatically chosen metric maximum for the team decision.
Rerun notebook 02, then edit `selected/<run>/topic_labels.csv`: `proposed_label`, `evidence_ids`,
`evidence_notes`, and `confirmed`. Confirmed names require nonblank notes and valid evidence IDs.
Reruns preserve edits and reject labels bound to a different model.

Each topic's three development examples have its highest probabilities among nonreserved articles,
with article IDs breaking ties. Examples may have another dominant topic; the table records this.
This also supplies evidence for topics with zero dominant articles. Development examples are not a
random evaluation sample. The 100 reserved articles participate in fitting, but not selection review
or naming. The reservation was drawn **before** naming, correcting the old classical TODO notes.

## Comparison and review boundaries

The handoff retains one dominant assignment per article and all K topics, including zero-count topics.
The complete publication CSVs retain all topics and all outlets. Main figures follow the modern layout:
15 largest topics, outlets with at least 50 articles, all-article denominators, and an all-zero unassigned
column. Topics omitted from a figure still contribute to its denominator.

The manifest preserves original preprocessing, representation, fit, evaluation, and interpretation/export
times, with software and hardware context. Shared preparation is a one-time cost, not seven independent
costs to add together. File serialization/cache verification outside those stages is not claimed as fit
time. Cache loads are measured separately. Some runtime differences can reflect hardware and scheduling.

Numerical comparison can precede confirmed names. `labels_confirmed` becomes true only when every topic
has confirmed evidence; the reservation hash must also match. Genuine independent ratings are never
invented. See the [reviewer workflow](../human-review/README.md).

If a provisional comparison already exists and exports change, preserve the **entire** active comparison
directory under `Results/comparison/archive/<descriptive-name>/` before rerunning notebook 03 and the
comparison. The exporter stops before changing published files while an active comparison binding exists.
Never overwrite frozen packets or answers: finish the original review or explicitly start a separate study.
The archive retains the old identity, results, packet, and answers. Identical reruns require no archive.

Held-out evaluation, common-date coverage sensitivity, manuscript revisions, final theme interpretation,
and genuine ratings remain follow-up work. The modern model still needs its own team selection and labels.
