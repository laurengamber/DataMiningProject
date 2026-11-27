# Modern (BERTopic) results

These generated snapshots contain the selected BERTopic run, `n30_c25_s42`.
The source runs, selection, and editable labels remain under `modern/`.

Refresh from the repository root without refitting or loading models:

```sh
uv run python final-project/code/modern-methods/export_results.py
```

Notebook 03 also refreshes these files after preparing selected-model summaries.
Run notebooks 02 and 03 first if the selected run's required summaries are missing.

| File | Contents |
| --- | --- |
| `assignments.csv` | One row per article: article ID, model, run, topic, and membership strength. |
| `terms.csv` | Ranked terms and weights from the selected run. |
| `topics.csv` | Topic ID, confirmed label (otherwise keywords), and article count. |
| `topic_labels.csv` | Snapshot of proposals, evidence, and confirmation status. |
| `representative_ids.csv` | Up to three centroid-nearest nonreserved examples per topic, with titles and publications. |
| `representatives.csv` | The same examples with full corpus text; generated locally and ignored by Git. |
| `stability.csv` | Seed 7 and 21 comparisons: ARI, evaluated coverage, and outlier agreement. |
| `coherence.csv` | Per-topic coherence and vocabulary coverage. |
| `topic_inventory.csv` | Counts, prevalence, keywords, current labels/status, coherence, and example IDs. |
| `publication_counts.csv` | Article counts for every publication and topic. |
| `publication_proportions.csv` | Shares of all articles in each publication, including unassigned articles. |
| `publication_sample_sizes.csv` | Total articles per publication. |
| `manifest.json` | Selected run, corpus and run identity, parameters, metrics, environment, and source/output hashes. |

Edit labels in `modern/selected/n30_c25_s42/topic_labels.csv`, then refresh this export.
Changes to these snapshots are overwritten. Only team-confirmed labels replace
keyword labels. Topic `-1` means **Unassigned**, not a substantive topic.

There is no `mixtures.csv`: this configuration uses `calculate_probabilities=False`.
Membership strength is the existing clustering strength, not an LDA topic mixture.
Seed ARI covers articles assigned in both runs; retain its evaluated count and fraction.
Representatives are development examples and exclude the reserved review sample.
The export preserves source artifacts and does not change comparison inputs.
