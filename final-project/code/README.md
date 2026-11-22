# Final-project code

All project pipeline code lives here. The former repository-root `modern-methods/project/` contained only empty directories and has been removed; no source files or saved results needed moving.

| Folder | Purpose |
| --- | --- |
| [classical-methods](classical-methods/) | LDA preprocessing, representation, fitting, interpretation, and exports |
| [modern-methods](modern-methods/notebooks/README.md) | Corpus preparation, embeddings, BERTopic experiments, and modern publication analysis |
| [shared](shared/) | Common corpus, evaluation, and human-review utilities |
| [comparison](comparison/README.md) | Joint BERTopic–LDA metrics, publication comparisons, and human-review results |
| [human-review](human-review/README.md) | Coordinator workflow and separate independent reviewer notebooks |

Start Jupyter from the repository root with `uv run jupyter lab`. Run modern notebooks 01–03, document the team model choice, and supply the classical exports. Use [pipeline_comparison.ipynb](comparison/pipeline_comparison.ipynb) to compare outputs and prepare the frozen review packet once both label sets are confirmed. Each reviewer then uses their assigned notebook; rerun the comparison after both finish to include human results.

Existing data and output locations are unchanged:

- Raw articles: repository-root `data/self_driving_articles.csv`.
- Shared deduplicated corpus: `final-project/data/corpus.csv`.
- Modern runs and caches: `final-project/code/modern-methods/Results/modern/`.
- Classical handoff: `final-project/code/modern-methods/Results/classical/`.
- Joint results and review packets: `final-project/code/modern-methods/Results/comparison/`.

From the repository root, validate the notebook collection with:

```sh
uv run python final-project/code/modern-methods/verify_notebooks.py
```

See each folder's instructions before executing analyses or entering ratings. Missing team inputs remain pending; the notebooks do not edit the PR3 manuscript.
