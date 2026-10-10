# Mary Kate’s modern pipeline

From the repository root, run `uv sync`, then `uv run jupyter lab`. Execute notebooks 01–03 in order from fresh kernels. Notebook 01 downloads GTE-small and caches all embeddings; notebook 02 runs six fits before pausing for real model-selection ratings. Fill `output/modern/selection_review.csv`, resume notebook 02, then fill `topic_labels.csv`. Notebook 03 evaluates the selected model and reports missing team inputs.

Helpers live in `src/topic_helpers.py`. Run `PYTHONPATH=modern-methods/project uv run python -m unittest discover -s modern-methods/project/tests` from the repository root. Generated large corpus copies, models, and caches are ignored by Git. Keep small tables and figures as reviewable results. Only load trusted local model pickle files.

## Laura’s handoff

Use `output/modern/corpus.csv`; `article_id` is the original unique X1 converted to a string. Keep the same records, including flagged duplicate bodies. Share the corpus manifest before fitting. Place these files in `output/classical/`:

- `assignments.csv`: article_id, model (`lda`), run_id, topic_id. Exactly one dominant-topic row per article. Retain LDA mixtures in a separate file.
- `terms.csv`: topic_id, rank (1-based), term (unigram), weight. At least ten ranked terms per topic where available; consistent tokenizer and English stopwords for comparison.
- `topics.csv`: topic_id, label, count. Counts must match dominant-topic assignments.
- `manifest.json`: corpus_hash from the shared corpus manifest, parameters, seeds, versions, hardware, and stage timings (preprocessing, fitting, representation, evaluation). Record cold and cached execution separately.

Publication and dates are metadata, not model features. Primary coherence and Jaccard use top-ten unigram terms and exclude BERTopic −1. Joint review requires frozen labels, the same 100 seeded articles, and two independently completed reviewer files. Do not replace blank human ratings with model-generated ratings.

## Milestones

- October 21, 2026: audit, shared corpus, embeddings, baseline.
- November 4: experiment study, selection, labels, modern pipeline.
- November 18: seed stability, joint quantitative and human evaluation.
- December 2: report tables, figures, methods/results, presentation.

The lecture’s logistic regression, word2vec, and fine-tuning examples provide context; they are not added experiments. The original chapter notebook remains unchanged.

## Command-line execution and verification

From the repository root:

```sh
uv run python modern-methods/project/run_embeddings.py
uv run python modern-methods/project/run_experiments.py
uv run python modern-methods/project/verify_notebooks.py
PYTHONPATH=modern-methods/project uv run python -m unittest discover -s modern-methods/project/tests
```

The experiment script stops at model selection. Resume notebook 02 after filling the ratings. All output paths in this document are relative to `modern-methods/project/`; dependencies remain managed by the repository-level pyproject and lockfile. Cache/model files stay local. Do not commit full article review packets.

Vocabulary filtering uses a fixed vocabulary learned from original articles with `min_df=5`; BERTopic otherwise interprets that threshold over concatenated topic documents, which can fail or hide topic-specific terms. The fixed vocabulary is reused across fits and representations.

Keyword/coherence preprocessing matches BERTopic’s English representation preprocessing (remove non-ASCII punctuation, then lowercase word tokenization and English stopwords). This is separate from the minimally cleaned contextual embedding input. Laura’s top terms should use this same evaluation vocabulary; coverage is reported for terms that differ.
