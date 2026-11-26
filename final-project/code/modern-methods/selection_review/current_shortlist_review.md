# BERTopic selection evidence — November 25, 2026

Mary Kate selected **n30_c25_s42** explicitly after the assistant presented the shortlist. See [selection.json](../Results/modern/selection.json).

The comparison considers all six current runs. The three primary candidates are n30_c25_s42 (highest coherence, 70 topics), n15_c25_s42 (76 topics), and n15_c50_s42 (40 topics). The recommendation was n30_c25_s42: its coherence and outlier fraction both improve on the other two shortlisted runs, while current examples retain specific legal, deployment, racing, and ride-service themes. The coarser n15_c100_s42 has the lowest outlier fraction (14.6%) and remains a meaningful coverage alternative. More topics and matching LDA's topic count are not inherently better.

[Current shortlist review](current_shortlist_review.csv) records each run's five largest, three lowest-coherence and three smallest assigned topics, deduplicated within run: 33 topic/run pairs, 70 distinct articles. Selection excludes topic -1. All supplied representative IDs for those topics were checked against the reserved sample; none overlap. Review covered keywords, titles and opening/middle/ending passages, not an exhaustive reading of the approximately 119,000 words of full article text. Findings are assistant developmental assessments, not independent human ratings or estimates of whole-cluster accuracy.

The legacy selection_review.csv is retained as historical assistant evidence. Its topic IDs/examples do not consistently describe the current inventories; do not use its numeric suggestions as current selection scores. This new review binds its evidence to current run manifests.

All candidates retain weak/source-format clusters. Particularly useful counterexamples are TechCrunch/Recode/DealBook roundups and conversational technology essays/interviews. High coherence alone cannot establish AV relevance. Some apparent strong evidence comes from syndicated or near-duplicate stories (Apple retrenchment; Uber-Volvo announcements), so representative agreement is not independent replication. No corpus cleaning or model fitting settings were changed during selection.
