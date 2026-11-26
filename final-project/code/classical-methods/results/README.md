# Classical (LDA) results

Saved reference exports for the selected LDA run (`lda_k40_s42`: K=40, seed 42). Hyperparameters are in `../selected_configuration.json`. The current `classical-methods/main.py` writes new exports to `final-project/code/modern-methods/Results/classical/` relative to the repository root; it does not rewrite this saved reference directory. Existing comparison labels and frozen reviews remain bound to these reference files.


| File | What it is |
|---|---|
| `assignments.csv` | One row per article: `article_id`, `model`, `run_id`, dominant `topic_id`, and `membership_strength` (that topic's probability). |
| `mixtures.csv` | Full topic mixture per article (`topic_0` … `topic_39`); each row sums to 1. |
| `terms.csv` | Top 10 terms per topic: `topic_id`, `rank`, `term`, `weight`. |
| `topics.csv` | `topic_id`, `label`, and `count` (articles whose dominant topic is that topic). The label is the hand label if one exists, otherwise the keyword label. |
| `topic_labels.csv` | Label input saved with this reference. For a new CLI run, edit `manual_label` and `evidence_notes` in `modern-methods/Results/classical/topic_labels.csv`, then rerun `main.py` to apply them in that output directory. |
| `representatives.csv` | The 5 articles with the highest probability for each topic, read when writing labels. |
| `stability.csv` | Agreement (adjusted Rand index) of dominant topics between the seed-42 model and refits with seeds 7 and 21. |
| `manifest.json` | Corpus hash, run ID, seed, and the hyperparameters used. |