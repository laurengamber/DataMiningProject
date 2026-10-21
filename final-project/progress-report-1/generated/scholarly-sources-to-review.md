# Scholarly sources to review

Prepared October 20, 2026. The team has reviewed the sources in the project-proposal and lecture-proposal bibliographies, as confirmed by Mary Kate. All additions below are **awaiting group reading**. Titles, publication information, and the relevance notes were checked against primary publisher, author, or research-group pages. This is a reading guide, not a claim that the group has verified each paper's methods or findings.

The report's `pr1-references.bib` includes the existing foundations actually cited and the four priority additions below, with pending-review notes. Retain those notes until the relevant group review is complete. The other suggestions can be added when the group has read them and decides they support a specific claim.

## First four readings for PR1

### 1. The modern model's original description

**Maarten Grootendorst (2022). “BERTopic: Neural topic modeling with a class-based TF-IDF procedure.” arXiv:2203.05794.** This is an author preprint; do not describe it as a peer-reviewed conference article. [Author's paper](https://arxiv.org/abs/2203.05794)

The paper describes the embedding–clustering–topic-representation architecture. Use it to explain what BERTopic contributes beyond applying a generic clustering algorithm. **Read for:** the role of class-based TF-IDF, assumptions behind clustering as topic modeling, and what the paper's benchmarks do and do not establish. Compare its setup with the project's GTE-small, long-article pooling, and chosen clustering settings. **Suggested lead:** Mary Kate. **Report use:** Related Work and Methodology.

### 2. The basis of the chosen coherence measure

**Michael Röder, Andreas Both, and Alexander Hinneburg (2015). “Exploring the Space of Topic Coherence Measures.” WSDM, pp. 399–408. DOI: 10.1145/2684822.2685324.** [Research-group record](https://wse-research.org/publications/2015_acm_2684822.2685324), [author-hosted paper](https://svn.aksw.org/papers/2015/WSDM_Topic_Evaluation/public.pdf)

This paper organizes coherence measures through component choices and evaluates their association with human judgments. **Read for:** the construction of `c_v`, reference-corpus choices, word co-occurrence windows, and limits of transferring reported human correlations to this particular corpus. Record exactly which settings the implementation uses. **Suggested leads:** Laura and Mary Kate. **Report use:** Experimental Design; justification for a shared evaluation corpus and documented preprocessing.

### 3. Applied interpretation and the limits of coherence

**Caitlin Doogan and Wray Buntine (2021). “Topic Model or Topic Twaddle? Re-evaluating Semantic Interpretability Measures.” NAACL-HLT, pp. 3824–3848. DOI: 10.18653/v1/2021.naacl-main.300.** [Publisher record and open paper](https://aclanthology.org/2021.naacl-main.300/)

The authors examine how evaluation tasks relate to applied interpretability, including open labeling and specialized collections. **Read for:** the different meanings of interpretability, why a convenient automatic score may not select the most useful model, and how human tasks can match the research objective. Explain how the proposed article/topic-fit review differs from their tasks; do not call the project's 1–5 rubric a validated instrument from this paper. **Suggested lead:** Lauren; discuss jointly. **Report use:** Related Work, human evaluation, and Discussion.

### 4. Closely related autonomous-vehicle news research

**Praveena Penmetsa, Sunday Okafor, Emmanuel Adanu, Matthew Hudnall, Somayeh Bakhtiari Ramezani, Steven Holiday, and Steven Jones (2023). “How is automated and self-driving vehicle technology presented in the news media?” Technology in Society 74, 102290. DOI: 10.1016/j.techsoc.2023.102290.** [Publisher article](https://doi.org/10.1016/j.techsoc.2023.102290)

This is a particularly useful domain comparator because it analyzes news about the same technology using sentiment methods. **Read for:** retrieval terms, relevance screening, article/title treatment, source coverage, and the interpretation of media sentiment. Compare its objective with the project's thematic and publication-level questions. The publisher's indexed material was accessible during research, while direct article retrieval was intermittent; obtain and read the full paper before relying on detailed design claims. **Suggested lead:** Lauren. **Report use:** Introduction and domain-related-work comparison. It does not establish that news coverage is a representative measure of public opinion.

## Next reading: evaluation across model families

**Alexander Hoyle, Pranav Goel, Andrew Hian-Cheong, Denis Peskov, Jordan Boyd-Graber, and Philip Resnik (2021). “Is Automated Topic Model Evaluation Broken? The Incoherence of Coherence.” NeurIPS 34.** [Official proceedings record and paper](https://papers.neurips.cc/paper_files/paper/2021/hash/0f83556a305d789b1d71815e8ea4f4b0-Abstract.html)

The study compares automated coherence with human topic-rating and word-intrusion tasks and identifies problems with treating automatic model rankings as sufficient evidence. **Read for:** shared evaluation settings, disagreement between evidence types, and the specific model families studied. **Suggested leads:** Laura and Mary Kate. **Report use:** strengthen the rationale for combining metrics with people. Do not generalize its empirical findings into a claim that this project's BERTopic model must perform poorly; that requires this project's evidence.

## Supporting method sources

| Source | Why review it | Concrete question to answer |
|---|---|---|
| **Zehan Li, Xin Zhang, Yanzhao Zhang, Dingkun Long, Pengjun Xie, and Meishan Zhang (2023), “Towards General Text Embeddings with Multi-stage Contrastive Learning,” arXiv:2308.03281** — [author preprint](https://arxiv.org/abs/2308.03281) | Original GTE model-family paper; useful alongside the exact model resource | What training/evaluation assumptions support choosing GTE-small, and what remains untested on long news articles? Cite the [GTE-small model card](https://huggingface.co/thenlper/gte-small) for its 384 dimensions, 512-token limit, model license, and exact resource; the project's chunk-pooling rule is its own design choice. |
| **Leland McInnes, John Healy, and James Melville, “UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction,” arXiv:1802.03426** — [author preprint](https://arxiv.org/abs/1802.03426) | Explains the reduction stage | What do neighborhood scale and reduced dimension control? Explain why a five-dimensional fit supports clustering and why a two-dimensional plot is a display rather than validation. First submitted 2018; the current record is revised 2020, so cite a consistent version/date. |
| **Leland McInnes, John Healy, and Steve Astels (2017), “hdbscan: Hierarchical density based clustering,” Journal of Open Source Software 2(11), 205, DOI: 10.21105/joss.00205** — [publisher article](https://joss.theoj.org/papers/10.21105/joss.00205) | Peer-reviewed software paper for the clustering implementation | How do minimum cluster size, minimum samples, and unassigned observations affect interpretation? Distinguish citing this implementation from claiming it is the original mathematical derivation of HDBSCAN. |

**Suggested owner:** Mary Kate for these three, with a short explanation to the whole team. They support specific implementation choices; they need not each become a separate related-work paragraph.

## Optional robustness reading

**Alexander Hoyle, Pranav Goel, Rupak Sarkar, and Philip Resnik (2022). “Are Neural Topic Models Broken?” Findings of EMNLP, pp. 5321–5344. DOI: 10.18653/v1/2022.findings-emnlp.390.** [Publisher record](https://aclanthology.org/2022.findings-emnlp.390/)

This is a different paper from the 2021 coherence study. It studies stability and alignment with human-determined categories. **Use if time permits:** refine seed-stability interpretation and explain why stable assignments and useful categories are separate questions. Verify the evaluated model families before transferring conclusions to BERTopic; adding the paper's ensembling methods is outside the current project scope.

## How to turn the reading into a synthesis

Organize Related Work around claims and comparisons:

1. **Representation:** use the already-reviewed LDA paper/books and the original BERTopic paper to contrast topic mixtures with contextual clustering and keyword representation.
2. **Evaluation:** connect the coherence framework to applied-interpretation and human-evaluation studies; explain why common preprocessing and human article evidence are both needed.
3. **Domain contribution:** compare the news-media sentiment study with the proposed thematic/publication analysis. Do not claim this is the first autonomous-vehicle news topic study without a broader literature search.

For each paper, record: who read it; the sections read; the exact claim it supports; a method or dataset limitation; and how it changes the plan. A useful shared review sheet is:

| Source | Reader / date | Claim supported | Limit or mismatch with our project | Action in report |
|---|---|---|---|---|
| BERTopic | Pending | Pending reading | Pending reading | Method architecture |
| Coherence framework | Pending | Pending reading | Pending reading | Specify metric settings |
| Topic Twaddle | Pending | Pending reading | Pending reading | Human-review rationale |
| AV news study | Pending | Pending reading | Pending reading | Domain comparison |

Before submission, read all newly cited sources or revise the manuscript so it accurately describes them as a planned literature search. The plan's explicit pending status preserves honesty, but completing the priority readings will make PR1's literature section materially stronger. Cite software and exact resources separately when needed; software versions and manifests establish reproducibility, while research papers support scholarly claims.
