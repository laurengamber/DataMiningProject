# Final-project code

This folder contains the code for our LDA and BERTopic analyses, their comparison, and the human review.

The selected comparison is BERTopic `n30_c25_s42` versus LDA `lda_k40_s42`.
Quantitative results, draft labels, and interpretation are in the separate
[PR3 results notes](../progress-report-3/pr3-results-notes.md). Human ratings and
complete team label confirmation remain pending; three labels have explicit
assisted human approval. The separate
[robustness follow-up](modern-methods/Results/robustness/2026-11-25/README.md)
now includes seed/publication sensitivity, the six-setting BERTopic comparison,
shared-period coverage, an exploratory 80/20 split, and new timing measurements.

| Folder | Contents |
| --- | --- |
| [classical-methods](classical-methods/) | LDA preprocessing, fitting, topic interpretation, and saved results |
| [modern-methods](modern-methods/notebooks/README.md) | Article embeddings, BERTopic experiments, and publication results |
| [shared](shared/) | Functions both methods use for the dataset and evaluation |
| [comparison](comparison/README.md) | Comparisons of the models and human-review results |
| [human-review](human-review/README.md) | Separate reviewer notebooks and a coordinator notebook |

## Running the project

Start Jupyter from the repository root with `uv run jupyter lab`. Run modern notebooks 01–03, choose a model as a team, and validate the saved LDA exports. Then use [pipeline_comparison.ipynb](comparison/pipeline_comparison.ipynb) to compare the results.

Once both sets of topic labels are final, the comparison notebook prepares the human-review files. Each reviewer uses their own notebook. After both finish, rerun the comparison to include their ratings.

## Data and results

These paths start at the repository root:

- `data/self_driving_articles.csv`: source articles.
- `final-project/data/corpus.csv`: shared dataset after removing duplicates.
- `final-project/code/modern-methods/Results/modern/`: modern runs and saved embeddings.
- `final-project/code/classical-methods/results/`: Laura's LDA exports.
- `final-project/code/modern-methods/Results/comparison/`: comparison results and review files.

To check the notebook files without running the analysis:

```sh
uv run python final-project/code/modern-methods/verify_notebooks.py
```

The folder READMEs explain the individual steps. Missing inputs show as pending. We update the PR3 manuscript separately.
