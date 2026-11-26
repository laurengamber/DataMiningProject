# Final-project code

This folder contains the code for our LDA and BERTopic analyses, their comparison, and the human review.

| Folder | Contents |
| --- | --- |
| [classical-methods](classical-methods/README.md) | Selected LDA CLI pipeline and separate exploratory notebooks |
| [modern-methods](modern-methods/notebooks/README.md) | Article embeddings, BERTopic experiments, and publication results |
| [shared](shared/) | Functions both methods use for the dataset and evaluation |
| [comparison](comparison/README.md) | Comparisons of the models and human-review results |
| [human-review](human-review/README.md) | Separate reviewer notebooks and a coordinator notebook |

## Running the project

Start Jupyter from the repository root with `uv run jupyter lab`. Run modern notebook 01 to establish the shared corpus and review reservation. Run the modern notebooks and choose the modern model as a team. Run `classical-methods/main.py` for the selected LDA configuration. The [classical notebooks](classical-methods/README.md) retain a separate exploratory grid. Then use [pipeline_comparison.ipynb](comparison/pipeline_comparison.ipynb) to compare the results.

Once both sets of topic labels are final, the comparison notebook prepares the human-review files. Each reviewer uses their own notebook. After both finish, rerun the comparison to include their ratings.

## Data and results

These paths start at the repository root:

- `data/self_driving_articles.csv`: source articles.
- `final-project/data/corpus.csv`: shared dataset after removing duplicates.
- `final-project/code/modern-methods/Results/modern/`: modern runs and saved embeddings.
- `final-project/code/modern-methods/Results/classical/`: Selected LDA CLI exports.
- `final-project/code/modern-methods/Results/classical_exploration/`: Separate 100-iteration notebook grid.
- `final-project/code/modern-methods/Results/comparison/`: comparison results and review files.

To check the notebook files without running the analysis:

```sh
uv run python final-project/code/modern-methods/verify_notebooks.py
```

The folder READMEs explain the individual steps. Missing inputs show as pending. We update the PR3 manuscript separately.
