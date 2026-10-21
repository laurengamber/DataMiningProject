# Progress Report 1 completion plan

Prepared October 20, 2026. Target submission: October 25, 2026, as recorded in `pr1.tex`; confirm the submission time in the course system.

Confirmed by Mary Kate: LDA is the classical method, but Laura has not completed analysis. No human data, model-selection, or topic-label review is complete. The group has reviewed the project- and lecture-proposal sources; new sources remain pending reading. The selected working audience is **FLAIRS Applied Natural Language Processing**; PR1 keeps the required IEEE format. The draft now lives in `pr1.tex`, with companion reading and conference shortlists in `scholarly-sources-to-review.md` and `potential-conferences.md`.

## Deliverable and scope

Produce one IEEE conference-format PDF, at most **four pages of report content, excluding references**. It should be a detailed blueprint for the final paper, with preliminary introduction and literature synthesis, evidence of data inspection, and a credible methods/evaluation/completion plan. Completed model experiments are optional at this stage. The priority is making the research logic and remaining work explicit.

Use `pr1.tex` as the manuscript starting point and `updated-proposal.tex` as reusable draft material. Organize the report as the anticipated paper itself. Fold the current separate assignment-prompt headings into the corresponding paper sections, rather than writing the outline and then repeating the same material underneath it.

Suggested working title: **Themes in Autonomous Vehicle News Coverage Across Publications, 2016–2020: An LDA and BERTopic Comparison**.

Keep Laura Banaszewski, Mary Kate Carara, and Lauren Gamber as authors. Use the substantive research question from the instructor's feedback:

> What themes characterize news coverage of autonomous vehicles from 2016 to 2020, and how does their prevalence differ across publications?

Supporting question: How does using LDA versus BERTopic affect theme interpretation and publication-level conclusions? The contribution is a reproducible, critically evaluated application and comparison. The articles describe news coverage; they do not directly measure public opinion.

## What is already available

| Evidence | Available material | How to use it |
|---|---|---|
| Instructor feedback addressed in draft | `updated-proposal.tex` names the substantive question, algorithms, coherence metric, and review plan | Reuse and tighten; verify claims before transferring |
| Data access and audit | Root `self_driving_articles.csv`; `../modern-methods/Results/modern/corpus_summary.json` | Populate the Data section and one compact audit table |
| Modern implementation | Three notebooks, helper code, experiment manifests and outputs under `../modern-methods/` | Describe implemented stages and exploratory experiments accurately |
| Prior division of work | Root README and proposals | Preserve Laura/classical, Mary Kate/modern, Lauren/theory and visualization |
| Initial bibliography | `../proposal/references.bib`; `../../lecture/modern-methods/sources.bib` | Seed a focused scholarly reading list; do not copy unrelated citations |

The CSV was inspected while preparing this plan: **7,337 articles, 15 source columns, 25 publications, January 1, 2016–March 26, 2020**, with five duplicate bodies beyond their first occurrences. The existing audit reports 1,381 missing author values and 3,668 missing section values, no missing article bodies or publications, and median article length 496 words. Publication counts are highly unequal: TechCrunch has 1,214 articles, while the smallest publication has one. This makes publication sample sizes and comparison rules essential.

**Recovered extraction provenance:** Mary Kate confirmed the original Kaggle source, David McKinley's All the News Dataset. The tracked script is `../../data/Text Mining News Articles.Rmd`; it reads `all-the-news-2-1.csv` in 100,000-row chunks and searches titles and bodies case-insensitively using:

```text
self[- ]driving|driverless|autonomous (car|vehicle|truck|driving)|robo[- ]?taxi|waymo|tesla'?s? autopilot
```

It first selects a title or body match, then requires a title match or at least three body matches, requires at least 150 whitespace-delimited words, parses dates, and retains the first occurrence of each exact title. Checks on the available subset found no threshold violations, no duplicate titles, and exact agreement with the stored title-match/body-hit fields. The root and `data/` subset copies are byte-identical. Full-source re-extraction has not been repeated; license verification and the manual relevance audit remain pending. Title deduplication is distinct from the five repeated bodies still present.

**Confirmed status:** `STATUS.md` says model selection is pending, but `selected_run.json` and downstream outputs exist. The selection-review CSV explicitly labels its scores as assistant suggestions, and manual topic labels are blank. Mary Kate confirms no human review is complete. Report these as exploratory outputs until the team verifies selection and completes human review. Classical LDA is confirmed, with analysis not yet begun.

## Tasks to complete before submission

### 1. Agree on the study contract — all three members, October 20–21

- Approve the primary and supporting research questions and limit the comparison to LDA and BERTopic.
- Freeze the common article IDs and cleaning/duplicate policy. The current handoff retains all 7,337 articles and flags duplicate bodies; keep that primary corpus unless both pipelines are deliberately regenerated. Plan a deduplicated sensitivity check.
- State that article bodies are inputs, with publication/date used as metadata. There is no supervised target.
- Agree on publication comparison eligibility. A practical starting proposal is to display publications with at least 50 articles, disclose all counts, and examine sensitivity to that cutoff and shared date coverage. Tiny publications can be described without ranking them.
- Confirm actual completed work and record owners for every remaining task.

### 2. Finish the initial data understanding — Mary Kate and Lauren, October 21

- Reuse the existing audit and recovered R Markdown extraction rules above. Preserve the script and its source filename; distinguish verification of the available subset from a full-source re-extraction.
- Have a team member inspect the existing seeded 30-article audit sample for relevance, incidental mentions, boilerplate, and malformed text. Report findings and whether cleaning changes are needed.
- Produce one compact table with corpus size, dates, publications, missingness, duplicates, and length summary. Inspect publication-by-year counts; include a small figure only if space permits.
- Verify the original dataset citation, access link, license, and redistribution conditions. Do not equate Kaggle availability with permission to redistribute article text. Include the code repository link: <https://github.com/laurengamber/DataMiningProject>.
- State that data access is already secured. The fallback for computing limits is a documented, seeded subset shared by both pipelines; retain the full corpus for descriptive counts.

### 3. Build a comparative related-work section — Lauren leads; everyone reads, October 21–22

Aim for approximately 6–10 relevant scholarly sources, plus dataset/model/software citations as appropriate. This is a workload target, not an assignment minimum. Read and verify every source actually cited.

Organize the discussion around three comparisons:

1. Count-based topic models versus embedding-based topic models: assumptions, topic mixtures versus hard clusters, and interpretability. Start with the original LDA and BERTopic papers; add primary sources for embedding, UMAP, and HDBSCAN choices where needed.
2. Automated coherence versus human interpretation: find the primary source for the chosen `c_v` measure and a scholarly discussion of topic-model evaluation limitations.
3. Topic modeling of news or autonomous-vehicle media coverage: find at least one closely related application, compare corpus, research question, methods, and evaluation, and identify what this project adds.

Keep a small reading matrix: source, claim supported, comparison with this project, and reader. The proposal's books and tutorial are useful background, but the related-work argument needs scholarly method and application evidence. This plan does not claim these additional sources have already been read or verified.

### 4. Specify the methods and credible evaluation — Laura and Mary Kate, October 22–23

**Baseline:** LDA on a cleaned document-term count matrix. Explain its role as a meaningful classical baseline with article-topic mixtures. Agree on a small topic-count grid, for example 10, 20, 30, and 50, plus documented vocabulary thresholds, priors, fitting settings, and seeds. Label this grid as proposed until Laura confirms it.

**Modern method:** GTE-small article embeddings → UMAP → HDBSCAN → class-based TF-IDF within BERTopic. Describe minimal contextual cleaning and the implemented long-article strategy: 480-token chunks, token-weighted mean pooling, and normalization. The current exploratory grid uses UMAP neighborhood sizes 15/30 and minimum cluster sizes 25/50/100. Record other settings, model revision, package versions, hardware, and cache use.

**Evaluation decisions to write explicitly:**

- Use mean and per-topic `c_v` coherence from top-ten unigram terms with a shared reference corpus and evaluation preprocessing. Also report topic count, sizes, keyword diversity, and BERTopic's unassigned fraction; coherence alone does not determine the winner.
- Compare topic words with a pairwise Jaccard heat map. Topic IDs do not align across models, and word overlap measures lexical agreement rather than semantic equivalence. Discuss unequal topic counts/granularity when interpreting differences.
- Use cosine silhouette in the original embedding space only as a supplementary modern diagnostic; disclose exclusion of unassigned articles. It is not a common performance score for both methods.
- Plan two independent reviewers on the same 100 seeded articles after configurations and labels are frozen. Define a 1–5 article/topic-fit rubric with anchors, record unassigned cases separately, and summarize ratings and agreement. Use separate articles for model selection and naming. Reading the final review sample must not guide later tuning without disclosing that reuse.
- Explain the validation setting: this is a descriptive analysis of an observed corpus. A supervised train/validation/test split is not automatically appropriate. Separate development review from final human assessment, and do not claim out-of-sample predictive performance. If prediction on future articles becomes an objective, add a chronological holdout and fit all learned preprocessing on training data only.
- Keep publication/date out of modeling features. Check duplicate or syndicated stories and uneven time coverage as dependence concerns. For robustness, use selected configurations with seeds 7/21/42, duplicate removal, and a comparison restricted to common dates or publication-year strata where counts support it.
- Define each heat-map cell as articles assigned to a topic divided by all eligible articles from that publication. Include an unassigned category for BERTopic; show sample sizes. Treat LDA dominant-topic summaries as a simplification of its mixtures.
- Compare stage timings on documented hardware, including modern embedding cost and distinguishing cached from initial runs. Do not declare success solely because one pipeline has the highest coherence. Success means evidence-supported themes and publication findings with documented sensitivity and uncertainty.

For PR1, specify these procedures; completing the final 100-article review and all experiments can remain scheduled work.

### 5. Turn `pr1.tex` into a paragraph-level blueprint — all members, October 23–24

Each substantive section should state its purpose, supporting evidence/literature, planned displays, completed work, and remaining work. Use compact prose with explicit **Completed** and **Planned** statements where useful.

| Paper component | Content and evidence to include | Approximate space |
|---|---|---|
| Title/authors, abstract, venue | Specific title; concise motivation, corpus, question, proposed comparison, and current status | 0.45 page |
| Introduction | Problem, practical gap, research questions, descriptive contribution | 0.45 page |
| Related work | Comparative synthesis of methods, evaluation, and domain research | 0.50 page |
| Data | Provenance, observation/variables, audit table, quality concerns, access/license | 0.55 page |
| Methodology | LDA baseline and modern stages with rationale and design choices; proposed pipeline diagram if useful | 0.65 page |
| Experimental design | Selection/review separation, metrics, dependence, publication denominators, robustness, success criteria | 0.70 page |
| Results; Discussion | Separate short subsections describing planned evidence and interpretation; identify any actual pilot findings as preliminary | 0.25 page |
| Limitations/responsible use; Conclusion | Filtering/coverage bias, copyright, author metadata, limits of media/public-opinion inference; anticipated contribution | 0.20 page |
| Project plan and responsibilities | Compact milestones/owners plus dependencies and contingencies | 0.25 page |
| References | Verified sources in IEEE style | Excluded from four-page allowance |

The allocations total four pages and are drafting targets, not formatting rules. Cut repetition before shrinking anything. Results notes should anticipate a topic/representative-article table, a model-quality/timing table, a publication-proportion heat map, and a lexical-overlap heat map; only the most useful preliminary display needs to appear in PR1.

**Selected venue:** FLAIRS' Applied Natural Language Processing track is the working audience confirmed by Mary Kate. Its [organizers' call](https://sites.google.com/view/flairs-anlp/anlp-2027) includes contextual representations, applications, and evaluation. Explain the fit without promising acceptance or actual submission. Use the [official IEEE conference template](https://conferences.ieeeauthorcenter.ieee.org/write-your-paper/authoring-tools-and-templates/) for PR1 as the assignment requires; an actual FLAIRS submission would follow its own format. The assignment's four-page limit excluding references governs PR1.

**LaTeX cleanup:** Replace the generic title and repeated author section; preserve IEEE formatting; replace every “Item 1”; remove the duplicate prompt sections after integrating their requirements. The current `itemize[leftmargin=...]` uses an option without a supporting package—prefer ordinary IEEE list formatting or prose. Add working citation/bibliography commands; for an IEEE BibTeX workflow use `IEEEtran` bibliography style and a verified `.bib` file. Compile early enough to catch citation and layout problems.

### 6. Review and submit — all members, October 24–25

- October 24: Assemble the full draft and compile it. Each member reviews the entire paper; cross-check every assignment requirement and the three instructor feedback points against actual text.
- October 25: Resolve comments, verify citations and hyperlinks, check the rendered PDF, and submit one group PDF before the course-system deadline.
- Definition of done: all required paper sections contain meaningful notes; the introduction and related work have preliminary substance; data access/inspection is evidenced; methods/evaluation are specific; every completion claim is accurate; numbered displays have captions and text references; report content fits within four pages, with references separate.

## Project milestones to include in PR1

These continue the team's existing plan; confirm the final course deadlines before submitting.

| Date | Deliverable | Lead and dependencies |
|---|---|---|
| October 21 | Shared corpus/policy and audit confirmed; classical baseline status checked | Mary Kate + Laura; Lauren summarizes audit |
| October 25 | PR1 PDF | All; Lauren leads literature/visualization, Laura classical methods, Mary Kate modern methods/evaluation integration |
| November 4 | Both pipelines, limited comparisons, verified selection, topic labels, literature synthesis | Laura + Mary Kate technical; Lauren literature/visuals; all review evidence |
| November 18 | Quantitative/human evaluation, seed sensitivity, and publication comparisons | Both model exports and frozen labels required; two members independently review; all interpret |
| December 2 | Final manuscript, figures/tables, and presentation preparation | All; each member reviews the full technical argument |

Key dependencies and contingencies: publication comparisons require common corpus IDs and verified assignments; final human review requires frozen labels; cross-method evaluation requires Laura's exports. If classical outputs arrive later, PR1 states their actual status and planned handoff. If compute is limiting, reuse validated embeddings and reduce the search or use a shared documented subset. If topics are too fragmented, prioritize a small set of interpretable configurations and disclose the selection criteria. If date/publication cells are sparse, narrow the comparison and present counts rather than unstable rankings. Everyone should understand both pipelines and contribute technical review and manuscript work.
