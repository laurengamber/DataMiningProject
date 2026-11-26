# Response to Progress Report 2 feedback

Prepared November 26, 2026. This response addresses the [instructor’s PR2 feedback](../progress-report-2/pr2-feedback.tex). It describes completed analyses and prepared PR3 results materials; integration into the conference manuscript and independent article-fit evaluation remain pending.

## 1. Answer the research questions with themes, publication comparisons, and differences between models

**Feedback.** The report should move beyond algorithm implementation and evaluation to explain what themes appear in autonomous-vehicle coverage, how they differ across publications, and whether LDA and BERTopic support different conclusions. The requested minimum was a table of topic labels, keywords, sizes, and representative articles, followed by an initial publication comparison.

**Response.** We completed the comparison of the selected LDA and BERTopic models on the same 7,332 articles from 25 publications. All 40 LDA and 70 BERTopic labels have been approved by Mary Kate during assisted review and transferred into the authoritative label tables. The [results notes](pr3-results-notes.md) now contain the complete topic inventories and article-supported interpretations. For the main report, we selected an eight-row topic table covering Waymo, Uber–Waymo litigation, congressional legislation, and Hill.TV interviews in both models. Each row includes its approved label, keywords, article count, and a nonreserved representative article; titles and publications are supplied for citation lookup.

Both models recover recognizable themes concerning AV development, commercialization, safety, and governance, including Tesla/Autopilot, Waymo deployment, litigation, freight, suppliers, regulation, and urban mobility. We also retain mixed and format-driven labels rather than treating every cluster as a distinct substantive theme. For example, both models assign the same 27 articles to Hill.TV interview coverage, all from The Hill. This agreement reflects a source-associated format and does not by itself establish coherent AV content.

The publication comparison now provides concrete findings:

| Example | Selected LDA result | Selected BERTopic result | Interpretation |
| --- | --- | --- | --- |
| Waymo: The Verge versus TechCrunch | 6.14% versus 3.05% | 9.28% versus 7.00% | The direction persists across the checked configurations, LDA seeds, and shared-period analysis, although topic breadth differs. |
| Litigation: Vox versus Reuters | 9.40% versus 5.04% | 8.80% versus 4.33% | The direction persists across all six BERTopic configurations and the shared period, but reverses under LDA seed 7. |
| Congressional legislation: The Hill | 33.99% | 8.22% | Both models identify the theme, but its measured share depends strongly on topic definition. |
| Urban mobility: Wired | 14.06% | 2.01% | Model choice changes the apparent prominence of the theme; the contrast persists in the shared-period subset. |

Each percentage uses all corpus articles from the relevant publication as its denominator, including BERTopic-unassigned articles. These results describe the collected corpus, not all output from each outlet, editorial intentions, or public opinion. A coverage-based restriction to 2016–2018 retains 4,931 articles from 11 publications and supports the selected directional comparisons while preserving the substantial model differences. [Publication and robustness evidence](pr3-results-notes.md#findings-for-the-research-questions).

We also examined shared article assignments to explain differences in topic boundaries. LDA’s 356-article Uber testing/crash topic separates into several BERTopic event and policy clusters, with 61 articles unassigned. Conversely, BERTopic’s 538-article Tesla topic includes 227 articles from LDA’s product/upgrades topic and 152 from its crash-investigation topic. Thus, BERTopic’s larger topic count does not imply finer distinctions everywhere.

Two focused figures are prepared for the main results: [publication comparisons](../code/modern-methods/Results/robustness/2026-11-26/report_selection/publication_examples.pdf) and [topic splitting and combining](../code/modern-methods/Results/robustness/2026-11-26/report_selection/topic_split_merge.pdf). Captions, representative examples, and the proposed topic and metrics tables are documented in the [report selections](pr3-results-notes.md#selected-main-report-examples-and-figures--november-26-2026). Full inventories, publication heatmaps, and the 40-by-70 Jaccard matrix remain available as supporting material.

The resulting interpretation is qualified: BERTopic has higher mean coherence (0.7047 versus 0.6552), while LDA has higher keyword diversity (0.7100 versus 0.6514) and assigns every article. BERTopic leaves 1,323 articles unassigned (18.04%). These measures and the robustness checks support complementary descriptions of the corpus, not an overall accuracy ranking. Independent human-fit results are still pending.

## 2. Treat the retrospective 80/20 split as exploratory robustness analysis

**Feedback.** Vocabulary and configuration development had already used the full corpus before the proposed split. Refitting on 80% therefore cannot make the remaining 20% an untouched evaluation set.

**Response.** We agree. The saved protocol and results notes explicitly identify this analysis as an **exploratory robustness check**, disclose the earlier full-corpus development, and avoid claims of untouched final-test performance. Refitting does not undo the influence of those earlier decisions.

The completed split uses seed 42 and publication/year strata, producing 5,866 training and 1,466 held-out articles. Ten singleton strata remain in training. With configurations fixed, vocabularies, LDA, UMAP, clustering, and c-TF-IDF were fitted using training articles only. Cached pretrained article embeddings were reused without corpus-adaptive training; no held-out tuning was performed. Nevertheless, earlier development influenced settings and stopwords, and near-duplicate or syndicated stories may cross partitions. This is not a story-group holdout. [Split protocol](../code/modern-methods/Results/robustness/2026-11-25/split_protocol.json).

Using the same held-out articles as the coherence reference, BERTopic’s mean c_v is 0.6337 and LDA’s is 0.6130. BERTopic leaves 454 of 1,466 held-out articles unassigned (30.97%), compared with 23.37% of its training articles. LDA’s held-out perplexity is 6,922.24 under its training vocabulary; there is no corresponding BERTopic perplexity. We interpret these as descriptive sensitivity results, not independent validation of labels or evidence of a generalization ranking. [Split results](../code/modern-methods/Results/robustness/2026-11-25/split_metrics.csv).

The separate 100-article human-review sample is reserved from naming and development review, not from unsupervised fitting. Its frozen packet therefore evaluates article–label fit within the study corpus; it is not an unseen-corpus prediction test.

## Additional correction and remaining work

While reconciling the evidence, we found that PR2’s claim of a completed, uniformly clean 30-article manual audit lacked saved judgments. A new audit was completed on November 26: 24 articles were judged centrally relevant, five peripheral, and one not relevant; seven contained boilerplate, four were malformed, and two had uncertain malformed-text judgments. These dimensions overlap. Mary Kate accepted assistant suggestions after the assistant inspected all stored texts; her direct reading scope was not confirmed. This is a new assisted audit, not substantiation of the historical PR2 claim or an estimate of corpus-wide defect prevalence. The original record remains preserved. [Completed audit and limitations](../code/modern-methods/Results/robustness/2026-11-25/audit_review/2026-11-25/completed_audit_summary_2026-11-26.json).

The remaining work is to integrate these prepared materials and corrections into the manuscript, complete the two independent reviews of the same 100 articles, and report per-reviewer fit scores and agreement with the specified article-bootstrap uncertainty. Unassigned BERTopic items will receive qualitative review and remain excluded from numerical fit ratings. No human-rating averages, agreement estimates, or confidence intervals are claimed as completed here.
