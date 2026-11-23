# Human review

Each reviewer has a separate notebook and answer file:

| Notebook | Used by | Answer file |
| --- | --- | --- |
| [reviewer_1.ipynb](reviewer_1.ipynb) | Reviewer 1 | `reviewer_1.csv` |
| [reviewer_2.ipynb](reviewer_2.ipynb) | Reviewer 2 | `reviewer_2.csv` |
| [review_coordinator.ipynb](review_coordinator.ipynb) | Coordinator | Checks progress and summarizes both reviews |

The reviewer IDs are already set. Leave them unchanged. Both reviewers use the same rating guide and read the same 100 articles, rating each model's label separately.

## Start or resume a review

1. Start Jupyter with `uv run jupyter lab` and open your assigned notebook.
2. Save a personal copy as `reviewer_1_workbook.ipynb` or `reviewer_2_workbook.ipynb` inside the packet folder. Git ignores these working copies.
3. Leave `PACKET_FOLDER = None` unless the coordinator gave you a different folder.
4. Run the setup and configuration cells to load your saved answers.
5. Read the rating guide, display an unfinished item, and read the full article.
6. Fill in the score, flags, notes, and displayed item number. Set `SAVE_RATING = True` and run the cell to save.
7. Repeat the display and entry steps. Use the progress cell to find unfinished items. You can close the notebook and reload the same folder later.
8. Send your CSV to the coordinator when finished. Wait until both reviewers finish before discussing scores, and keep the original independent ratings.

Keep the repository notebooks as blank templates. A personal copy may contain answers in its code cells as well as article text in its outputs. Clearing outputs alone does not remove typed answers.

## Files needed

The [comparison notebook](../comparison/pipeline_comparison.ipynb) prepares the packet after both models and topic labels are final. The default folder is:

```text
final-project/code/modern-methods/Results/comparison/<selected-run>/human_review/
```

Each reviewer needs `review_packet.csv`, `review_freeze.json`, `review_status.json`, and their own answer CSV. They do not need the other person's answers. The checks keep the article IDs, assignments, and labels fixed during review. Missing files show as pending.

After collecting both CSVs, the coordinator can summarize them in [review_coordinator.ipynb](review_coordinator.ipynb), or enable the human summary in [the comparison notebook](../comparison/pipeline_comparison.ipynb). Full article text and individual answers stay local and are ignored by Git.

## Check the notebooks

From the repository root:

```sh
uv run python final-project/code/modern-methods/verify_notebooks.py
uv run python final-project/code/modern-methods/verify_notebooks.py --execute reviewer_1 reviewer_2
uv run python final-project/code/modern-methods/verify_notebooks.py --execute coordinator
```

The first command checks all seven project notebooks without running them. The next commands run the reviewer or coordinator notebooks. With the default settings, they save no answers or combined summaries. `--execute 04` also runs the coordinator notebook for compatibility with older commands.

Use these commands on the blank templates, not on personal workbooks with edited save cells.
