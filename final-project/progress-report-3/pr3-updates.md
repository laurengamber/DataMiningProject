# PR3 manuscript updates from PR2

Prepared November 22, 2026. This is an editing guide for [pr3-submission.tex](pr3-submission.tex), based on [PR2](../progress-report-2/pr2-submission.tex), the [PR3 assignment](pr3-assignment.md), and the current saved analysis. **Neither manuscript is edited by this document.**

The current PR3 file is a copy of PR2 with only the report title changed. It still includes PR1 feedback, old pre-deduplication BERTopic results, an obsolete completion schedule, and outline placeholders. PR3 needs a unified working manuscript that distinguishes completed results from remaining research decisions.

## 1. Changes to make first

| Existing PR2/PR3 location or claim | Update for PR3 |
| --- | --- |
| “Implementation Progress and Initial Findings”: modern runs use 7,337 articles and must be rerun | Replace with the completed six-run study on **7,332 deduplicated articles**. |
| Table `tab:bertopic-grid` and the paragraph selecting `n15_c25_s42` | Replace the table with Section 4 below. Remove the bold selected row and old selection rationale. **No current configuration has been selected.** |
| Table `tab:stability`, ARI 0.957/0.975, and “BERTopic's assignments were more stable” | Remove from current-results claims. These are historical pre-deduplication findings; selected-configuration seed reruns on the current corpus are pending. |
| Smaller clusters always leave fewer articles unassigned | Replace with the observed interaction: the coverage trend differs between the two UMAP neighborhood settings. |
| Top-three model shortlist decided by 1–5 selection ratings | Replace with an explicit team choice and written rationale based on metrics, granularity, and article evidence. Legacy assistant-suggested scores are not independent human ratings. |
| “Paper Outline 2,” status legend, and “Purpose / Planned content / Required evidence” blocks | Replace with manuscript sections and actual preliminary results, discussion, and conclusion. Put unfinished analyses in the completion plan. |
| “Response to Feedback” addresses PR1 | Replace with a response to actual **PR2** feedback when obtained. Do not relabel the old responses as PR2 feedback. |
| Old November 18 milestones and `Due: November 8th, 2026` | Replace with confirmed current dates. The PR3 assignment in this repository does not establish a due date. |

Do not describe the current results as final themes, a final model, held-out performance, completed human evaluation, or a completed LDA–BERTopic comparison.

## 2. Abstract, introduction, and paper structure

### Suggested replacement abstract

> We investigate themes in autonomous-vehicle news coverage and how their prevalence differs across publications using an LDA baseline and an embedding-based BERTopic pipeline. The shared corpus contains 7,332 deduplicated articles from 25 publications, spanning January 2016 through March 2020. In the completed modern-method analysis, we generated full-text GTE-small embeddings and evaluated six combinations of UMAP neighborhood size and HDBSCAN minimum cluster size. The configurations produced 21–76 topics, mean $c_v$ coherence of 0.630–0.705, and unassigned shares of 14.6–22.2%. Smaller minimum cluster sizes produced finer topic partitions and higher coherence, while the effect on coverage depended on the UMAP setting. Article assignments, topic keywords, and within-publication proportions are available for all six configurations. Final modern-model selection, topic naming, selected-model stability checks, paired LDA comparison, and independent human ratings remain incomplete. These preliminary findings establish sensitivity to configuration choices; substantive thematic conclusions will require article-based interpretation and the remaining evaluation.

Restore the existing dataset and method citations when incorporating this prose. This draft intentionally omits historical LDA numerical claims that have not been revalidated through a current handoff.

### Introduction and related work

Keep the three research questions from PR2. Update the contribution paragraph so the claimed contribution matches completed evidence:

> The completed work provides a shared, deduplicated article corpus, a reproducible six-configuration BERTopic study, and article-level publication summaries for each configuration. The planned matched evaluation against LDA will assess how pipeline choice affects the recovered themes and publication comparisons. At this stage, configuration sensitivity can be assessed quantitatively, while named themes and cross-method conclusions await team interpretation and the classical handoff.

Retain the literature synthesis and existing verified citations, but distinguish motivation from established results. The statements “the first” such comparison and “no study” has done it require a defensible literature review; the code rewrite does not establish those claims. Likewise, do not label all 25 publications as U.S. publications unless that geographic scope has been established.

Use a coherent paper order: abstract and keywords; introduction; related work; data; methodology; experimental design; preliminary results; preliminary discussion; limitations/responsible use; preliminary conclusion; completion plan; response to PR2 feedback; references. Suggested keywords: *autonomous vehicles; news coverage; topic modeling; BERTopic; latent Dirichlet allocation*.

## 3. Data, methodology, and reproducibility

### Data section

Retain PR2's dataset description, regex, article-level unit of analysis, date coverage, duplicate policy, and corpus summary. Change the description of modern article bodies and metadata from future to completed tense. The modern runs now use the same 7,332 IDs and cleaned article texts recorded in the shared manifest.

Suggested addition:

> We regenerated the modern analysis from the deduplicated corpus and verified its ordered article IDs and text hash against the shared corpus manifest. Exact duplicate article bodies were removed by retaining the earliest-dated copy, with ties resolved in source order. Publication and date are interpretation metadata rather than embedding or clustering features. All six modern configurations use the same article set and cached embedding matrix.

**Check with the team:** PR2 says a 30-article manual audit found no irrelevant, malformed, or boilerplate-containing articles. The saved [audit CSV](../data/corpus_review.csv) has no fully populated relevance/boilerplate/malformed flag rows. That does not prove the reported review never occurred, but the current file does not substantiate it. Obtain the reviewers' record before retaining the numerical audit claim; do not fill those flags retrospectively from assumptions.

### Modern pipeline

Retain the 480-token chunking and token-weighted pooling equation (`eq:pooling`), GTE-small's 384-dimensional article vectors, the five-dimensional UMAP setup, HDBSCAN assumptions, and the c-TF-IDF equation (`eq:ctfidf`). The model revision is pinned at `17e1f347d17fe144873b1201da91788898c639cd`.

State these actual settings:

- UMAP: neighbors 15 or 30, five components, cosine distance, `min_dist=0`, seed 42 for the grid.
- HDBSCAN: minimum cluster size 25, 50, or 100; `min_samples=10`; Euclidean distance; excess-of-mass selection; outliers retained as topic −1.
- Keywords: ten unigram terms; English stopwords removed; fixed vocabulary learned over individual articles with `min_df=5`, reused across configurations.
- Fitting: the standard BERTopic interface with cached embeddings and fitted UMAP/HDBSCAN components. No KeyBERT/MMR representation experiments are part of the current study.

Add how development examples are chosen:

> For each non-outlier topic, we export up to three development articles ranked by similarity to the topic's mean article embedding, excluding the reserved human-evaluation IDs. These examples support naming and interpretation; they are not a random sample for estimating topic quality. Topic names remain unconfirmed until the team records labels and supporting evidence.

### Classical pipeline: retain only verified historical claims

The modern rewrite did not change Laura's code or refit LDA. PR2 reports a selected $K=40$, 20-iteration grid fits, a 100-iteration final fit, and seed ARIs of 0.32/0.36. Ask Laura to verify those figures and supply their artifacts before presenting them as the current matched baseline.

The repository currently has no completed classical handoff directory, and `interpret.py` and `export.py` still contain TODOs. Also, the current `lda.py` sets `MAX_ITER=100` for its fitting helper, including grid calls. This does not disprove the historical 20-iteration experiments, but the present default alone cannot reproduce that description. Reconcile the reported configurations with Laura's actual run records. Do not infer that all classical work is absent merely because the export handoff is missing.

### Implementation environment and validation

Replace the generic modern-hardware description with the recorded **Apple M5, 10 logical CPUs, 16 GiB memory, macOS 26.6.2, Python 3.13.11**. GTE-small computation used PyTorch MPS; dimensionality reduction and clustering ran on the CPU. Do not automatically attribute this machine to Laura's runs.

Recorded core versions remain BERTopic 0.17.4, sentence-transformers 6.1.0, umap-learn 0.5.12, hdbscan 0.8.44, scikit-learn 1.9.1, and gensim 4.4.0. [Hardware details](../code/modern-methods/Results/modern/hardware.json) and [embedding execution metadata](../code/modern-methods/Results/modern/embedding_execution.json) provide the source.

Suggested reproducibility statement:

> Three analysis notebooks cover corpus construction and embeddings, the bounded configuration study, and publication/evaluation outputs. A fourth notebook guides independent human review with a common rubric, per-reviewer answer files, explicit saving, and progress checks. All four notebooks have executed through the stages supported by available inputs; pending research decisions are reported explicitly. The 21-test suite checks corpus and artifact identity, real BERTopic fitting and serialization, review-sample separation, publication denominators, reviewer-file validation, and agreement calculations. Synthetic fixtures are used only for software tests and are not study results.

## 4. Replace the preliminary BERTopic results

Use this table in place of `tab:bertopic-grid`. Values are rounded from [experiments.csv](../code/modern-methods/Results/modern/experiments.csv); unassigned counts were checked against each run's assignments.

| UMAP neighbors | Minimum cluster size | Topics | Mean $c_v$ | Unassigned articles | Cosine silhouette |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 15 | 25 | 76 | 0.692 | 1,484 (20.2%) | 0.114 |
| 15 | 50 | 40 | 0.662 | 1,461 (19.9%) | 0.119 |
| 15 | 100 | 21 | 0.641 | 1,071 (14.6%) | 0.105 |
| 30 | 25 | 70 | 0.705 | 1,323 (18.0%) | 0.122 |
| 30 | 50 | 35 | 0.646 | 1,399 (19.1%) | 0.123 |
| 30 | 100 | 24 | 0.630 | 1,628 (22.2%) | 0.134 |

**Suggested caption:** “BERTopic configuration study on 7,332 deduplicated articles (seed 42). Topic counts exclude unassigned articles. Mean $c_v$ uses the shared reference corpus and top-ten unigram terms. Cosine silhouette is evaluated on a seeded sample of 2,000 assigned articles in the original 384-dimensional embedding space; outliers are excluded. No configuration has yet been selected.”

All six runs have more than 2,000 assigned articles, so the stated sample size applies to every row. All non-outlier topic terms have full coverage in the shared coherence reference. The outlier counts and percentages use all 7,332 articles as the denominator.

### Suggested replacement results prose

> We completed the six-configuration BERTopic study on the deduplicated corpus. Topic counts ranged from 21 to 76, and mean $c_v$ ranged from 0.630 to 0.705. Within each UMAP neighborhood setting, smaller minimum cluster sizes produced more topics and higher coherence. The highest mean coherence occurred with 30 neighbors and minimum cluster size 25: this configuration produced 70 topics and left 1,323 articles (18.0%) unassigned. It is a candidate configuration, not a selected final model.
>
> Coverage did not follow a uniform trend. With 15 neighbors, increasing minimum cluster size from 25 to 100 reduced the unassigned share from 20.2% to 14.6%; with 30 neighbors, it increased from 18.0% to 22.2%. The lowest unassigned share occurred with 15 neighbors and minimum cluster size 100, which produced 21 topics with mean $c_v=0.641$. These differences show that coherence, coverage, and topic granularity favor different configurations. Cosine silhouette values remained low (0.105–0.134) in the original embedding space. These conditional scores provide a clustering diagnostic, not evidence that the topics are substantively correct.

Do not reuse the old statement that `n15_c25_s42` has 70 topics, coherence 0.701, or 1,256 unassigned articles. Its current values are **76 topics, coherence 0.692, and 1,484 unassigned articles**.

### Publication outputs: completed computation, pending interpretation

Suggested prose:

> For every grid configuration, we computed topic counts and within-publication proportions for all 25 publications. The denominator includes all articles from a publication, including those left unassigned. The main heatmaps display the 16 publications with at least 50 articles and the 15 largest non-outlier topics plus the unassigned category. Complete matrices retain every publication and topic. Because the figure shows only a subset of topics, its displayed shares need not sum to one. The keyword labels are provisional; publication-level thematic conclusions await the team's configuration choice and article-supported topic names.

The figures are per-configuration exploratory outputs. Choosing one merely for a figure does not establish a final model. After team selection, use its confirmed labels and write an article-supported interpretation. A numerical publication pattern alone does not establish an outlet's editorial intent or a population-level difference.

### Computational cost: optional compact results paragraph

> The recorded embedding computation took 100.7 seconds on MPS with no article embeddings reused. The six fits, including dimensionality reduction, clustering, and keyword representation, took 7.3–13.6 seconds each; evaluation took an additional 9.9–24.3 seconds per configuration. These are observed stage timings on the recorded machine, not repeated benchmark estimates. The encoder had been downloaded separately: the recorded 0.3-second loading time is not a cold download measurement. A matched LDA runtime comparison remains pending.

Do not report the sum as a cold end-to-end runtime: these measurements omit some preparation, model-download, export, and plotting work and can include different initialization/cache effects.

## 5. Experimental design: completed versus planned

### Model selection and topic labels

Replace the scored-shortlist tiebreak with:

> The team will choose one modern configuration after reviewing coherence, coverage, topic sizes, granularity, keywords, and development articles across the grid. The chosen run and supporting rationale will be recorded explicitly. No configuration is selected automatically by a single metric. Topic labels and article evidence will be confirmed before independent evaluation. At the present reporting stage, the configuration choice and labels remain pending.

[selection.json](../code/modern-methods/Results/modern/selection.json) is currently blank by explicit team decision. The legacy selection CSV contains assistant-suggested assessments; these must not be described as completed independent human ratings.

### Independent human review

Suggested replacement:

> Before new development review, we reserved 100 article IDs with seed 42 from 7,276 eligible articles. We conservatively excluded 56 unique IDs appearing in the earlier audit packet or legacy development examples. The reserved articles remain in unsupervised fitting but are excluded from new selection and naming examples; this is separation of human-review evidence, not a held-out model test. Both pipelines must respect the same reservation.
>
> After both models and their labels are frozen, two reviewers will independently assess each model's assigned label for the same 100 articles, giving 200 article–model items per reviewer. Fit is scored from 1 (unrelated or misleading) to 5 (clear central-theme fit), with separate flags for article irrelevance and label ambiguity. BERTopic-unassigned items receive no numeric fit rating and are summarized separately. The packets identify the models, so the review is not blinded. We will report reviewer means, exact agreement, agreement within one point, and quadratic-weighted Cohen's kappa with a 95% interval from 1,000 paired-article bootstrap resamples. Undefined kappa values and the number of valid bootstrap resamples will be reported explicitly. The workflow is implemented, but no genuine independent ratings have been collected in the current artifacts.

Use [review_sample.json](../code/modern-methods/Results/modern/review_sample.json) for sampling evidence and [the coordinator notebook](../code/human-review/review_coordinator.ipynb) for the procedure. The reviewer notebook has been exercised with temporary test fixtures; that does not constitute completed human evaluation.

### Seed stability and topic matching

State that the selected configuration will be rerun with seeds 7 and 21. Report ARI only on articles assigned in both runs, together with the compared count/fraction and outlier-status agreement. Publication comparisons use maximum-overlap one-to-one topic matching; complete overlap tables retain unmatched topics and split/merge patterns. Topic numbers must not be compared directly across runs.

The implementation flags splits/merges when at least two overlaps each account for at least 10% of the source/target topic. If this diagnostic appears in the manuscript, identify the threshold as descriptive, not a significance test. **There are no current-corpus seed-stability results yet.**

### Held-out evaluation and leakage

Replace the assertion that strict publication-by-year stratification will place every group in both partitions:

> All results reported here describe models fitted to the full fixed corpus. A separate held-out evaluation is deferred to the final-report phase. Because some publication-by-year groups contain only one article, a policy for sparse groups must be established before partitioning. Any genuinely held-out evaluation must keep evaluation data out of preprocessing and vocabulary decisions, configuration selection, and model fitting. The current full-corpus study must not be interpreted as held-out performance.

The corpus contains **10 singleton publication–year groups**. A training-only refit after inspecting a full-corpus parameter study does not by itself make those articles an untouched final test set. If the same corpus is reused, explain the earlier exploratory exposure and describe the check proportionally, rather than claiming fully independent test performance.

### Coherence and cross-method alignment

Change coherence to completed tense for the modern grid; retain top-ten unigrams, the common tokenizer/English stopwords, 110-token windows, per-topic values, and outlier exclusion. Keyword diversity is the number of distinct top-ten words divided by the total number of top-ten term entries across non-outlier topics.

Retain `eq:jaccard` and the proposed LDA-row/BERTopic-column heatmap, but mark the comparison pending Laura's validated assignments, terms, topics, and manifest. Do not state that identical modeling vocabularies are required: the comparison shares reference preprocessing and reports coverage, while LDA retains its own custom-stopword and representation choices. Jaccard overlap indicates lexical agreement, not semantic equivalence.

## 6. Preliminary discussion, limitations, and conclusion

### Suggested discussion paragraphs

> The corrected configuration study shows a tradeoff between topic granularity and aggregate coherence: smaller minimum cluster sizes yield finer partitions with higher coherence. However, coverage responds differently under the two UMAP neighborhood settings. The coherence maximum therefore does not establish a uniquely preferable model. Development-article review is needed to determine whether finer clusters describe useful themes or fragment broader stories.
>
> Low original-space silhouette values indicate limited separation under this diagnostic, but they do not by themselves invalidate the topics or measure interpretability. Conversely, higher coherence does not establish that a topic label captures the central content of its articles. The reserved independent review is intended to add this missing article-level evidence.
>
> Publication matrices are now available, but interpretation remains conditional on the chosen model and confirmed topic names. Unequal outlet sizes, unequal time coverage, and event-driven clusters provide alternative explanations for apparent publication differences. Whether substantive patterns persist across seeds or across LDA and BERTopic remains an open empirical question.

Keep PR2's corpus-selection, unequal-coverage, syndication, pooling, and dominant-topic limitations. Add that the current analysis is exploratory, the human sample excludes prior review IDs, reviewer identities are not blinded to models, and no inter-method stability or quality superiority is established yet. Do not turn keyword-based cluster names into final themes without article evidence.

For responsible use, describe substantive AI assistance accurately: coding, notebook scaffolding, test development, and editing support. State that team members retain responsibility for research choices, interpretation, citations, and genuine independent ratings. Do not describe legacy assistant-suggested assessments as human observations.

### Suggested preliminary conclusion

> We have completed a reproducible six-configuration BERTopic analysis of 7,332 deduplicated autonomous-vehicle news articles and generated topic and publication summaries for each configuration. The results show that topic granularity, coherence, and assignment coverage depend on configuration choices, with no single metric determining the final model. The remaining work is to select and label a configuration through article review, assess its stability, integrate the classical baseline, and complete independent human evaluation. These steps are necessary before drawing substantive conclusions about themes across publications or the relative merits of the two pipelines.

## 7. Completion plan required by the PR3 assignment

Replace the old two-column schedule with the five required columns below. The listed dates are deliberately unconfirmed; **the team must replace them with real dates before submission**. December 2 appears in PR2's plan, but it should not be assumed to be the verified final deadline.

| Remaining task | Reason the task is necessary | Responsible group member | Expected output | Completion date |
| --- | --- | --- | --- | --- |
| Review the grid and record the modern configuration choice | Enables a defensible model for interpretation | Mary Kate, with team review | Chosen run and written rationale | Team to confirm |
| Confirm modern topic names and supporting article evidence | Required to answer the themes question | Mary Kate, with team review | Confirmed label table and topic inventory | Team to confirm |
| Fit selected seeds 7 and 21 and compare publication patterns | Tests sensitivity to stochastic clustering | Mary Kate | ARI, evaluated coverage, outlier agreement, matches and publication changes | Team to confirm |
| Verify historical LDA figures and provide current exports and labels | Enables an aligned baseline comparison | Laura | Assignments, terms, topics, manifest, and available timings | Team to confirm |
| Run cross-method comparisons | Addresses dependence of findings on pipeline choice | Mary Kate and Laura | Coherence/diversity comparison, Jaccard heatmap, assignment contingency and runtime summary | Team to confirm |
| Complete independent article ratings | Adds interpretability evidence beyond automatic metrics | Two team reviewers; assign names before submission | Two original rating files and agreement/uncertainty summary | Team to confirm |
| Complete shared-period publication sensitivity | Evaluates unequal date coverage as an explanation | Mary Kate and Lauren | Date-restricted publication tables and interpretation | Team to confirm |
| Define and execute the held-out robustness protocol | Evaluates transfer with sparse-stratum and exploratory-exposure limitations documented | Mary Kate and Laura | Documented split/policy, train-only fits and appropriately qualified metrics | Team to confirm |
| Finalize figures, results, discussion, and conclusion | Turns computed outputs into a coherent paper | All; Lauren coordinates visualization | Captioned figures and article-supported findings | Team to confirm |
| Recheck completed-input notebook paths and address PR2 feedback | Validates real handoffs/ratings and meets the revision requirement | All | Reproducibility check, feedback response, and final manuscript review | Team to confirm |

The existing software tests are complete; validating the future **real** LDA and reviewer inputs is still necessary. Model choice, topic interpretation, and the paired comparison are core unfinished research tasks, not merely cosmetic final-report refinements. Prioritize them before presenting PR3 as approaching a complete paper.

## 8. Response to PR2 feedback

No PR2 feedback file was found. Do not write that all feedback has been addressed or substitute the PR1 responses under a new heading. Request the actual comments and build a short response table:

| PR2 comment | Revision made | Manuscript location | Evidence/status |
| --- | --- | --- | --- |
| Insert the actual comment | Describe the specific revision | Name the updated section/table | Link or identify the supporting output; distinguish pending work |

A factual **progress-since-PR2** paragraph can be written now, separately from the feedback response:

> Since PR2, we reran the complete modern configuration study on the shared deduplicated corpus, generated full-text embeddings and per-configuration publication outputs, reserved the independent human-review sample, and implemented the reproducible comparison and reviewer workflows. Model selection remains pending team article review, and the classical handoff, selected-model seed reruns, and real human ratings remain incomplete.

## 9. Figures, evidence links, and final editing checks

| Evidence or figure | Current source and use |
| --- | --- |
| Corrected six-run table | [experiments.csv](../code/modern-methods/Results/modern/experiments.csv); replace the old grid table. |
| Corpus publication summary | [corpus_by_publication.csv](../code/modern-methods/Results/modern/corpus_by_publication.csv); supports sample sizes and date ranges. |
| Publication figure example | [n30_c25_s42 heatmap PDF](../code/modern-methods/Results/modern/runs/n30_c25_s42/publication/publication_proportions.pdf); exploratory example only, **not** a model-selection decision. Equivalent files exist for each run. |
| Full topic and publication evidence | Each `Results/modern/runs/<run>/` folder contains `topic_inventory.csv`, `representative_ids.csv`, and `publication/` matrices. Full-text development examples remain local. |
| Existing monthly corpus figure | [PR2 monthly_articles.pdf](../progress-report-2/figures/monthly_articles.pdf). PR3 currently points to `figures/monthly_articles.pdf`, but there is no corresponding PR3 figure file. Correct the path or copy the figure when editing the manuscript. |
| Human-review procedure | [Coordinator workflow](../code/human-review/review_coordinator.ipynb), [reviewer 1](../code/human-review/reviewer_1.ipynb), and [reviewer 2](../code/human-review/reviewer_2.ipynb); procedural guidance, not evidence that ratings are complete. |
| Status and execution instructions | [STATUS.md](../code/modern-methods/STATUS.md) and [notebook README](../code/modern-methods/notebooks/README.md). |
| Existing evidence/completion exports | [pr3_evidence_checklist.csv](../code/modern-methods/Results/modern/pr3_evidence_checklist.csv) and [completion_plan.csv](../code/modern-methods/Results/modern/completion_plan.csv). |

Before submitting the edited manuscript:

- Remove outline headings, status-tag prose, obsolete November dates, and pre-deduplication results presented as current findings.
- Distinguish “implemented,” “executed on current data,” and “completed by human reviewers.”
- Keep mean coherence and silhouette at three decimals and percentages at one decimal; specify denominators and outlier exclusions in captions.
- Number, caption, and discuss each actual table/figure. Use the confirmed model's figure for the main thematic interpretation once selection is complete.
- Preserve and verify existing citations; this guide adds no newly verified literature claims or references.
- Use the approved conference format and stay within **eight pages excluding references**, as specified by the PR3 assignment.
- Compile the manuscript and check all figure paths and bibliography references after manually applying these edits. This document does not compile, modify, or certify the final manuscript.
