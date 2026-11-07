The classical pipeline follows four stages

(1) data preprocessing
(2) document-term representation
(3) topic model fitting
(4) topic interpretation

We tokenize article bodies, remove English stopwords, and build a document-term count matrix. LDA provides an interpretable baseline through its topic-word distributions and article-level topic mixtures. We compare a small set of topic counts and assign each article its highest-weight (dominant) topic for publication summaries, while retaining the full topic mixture.

We use **sklearn's `LatentDirichletAllocation`** over gensim's `LdaModel`, because it plugs straight into the same `CountVectorizer` analyzer. 

## 3) Code plan

**Where things go:** your code lives in `final-project/classical-methods/`. `preprocessing.py` exists but is empty. Outputs go to `final-project/modern-methods/Results/classical/`, which is where notebook 03 looks.

**Step 0: get the corpus.** `corpus.csv` is gitignored and isn't on your machine. You need to run notebook 01 or `audit_corpus()`, or get the file from Mary Kate. Paths look broken since the recent `refactor` commit:
- The notebooks still set `ROOT = REPO/'modern-methods/project'`.
- `audit_corpus` reads `self_driving_articles.csv` from the repo root, but the file is in `data/`.

Ask Mary Kate about this before you rely on her scripts.

**Modules and steps:**

1. **`load_corpus`**
   - Read `corpus.csv` with `article_id` as a string.
   - Check that the IDs match `corpus_manifest.json`.
   - Recompute the hash by importing `digest` from `topic_helpers`; don't reimplement it.
2. **`preprocessing.py`**
   - Apply `representation_text`, then the shared analyzer.
   - Add your extra filters: custom stopwords and number-only tokens.
   - Time this stage.
3. **`representation.py` (document-term matrix)**
   - Build a `CountVectorizer` with your `min_df`/`max_df`, giving a sparse matrix.
   - Log vocabulary size and sparsity.
4. **`fit_lda.py`**
   - Grid over the number of topics K, for example {10, 15, 20, 25, 30, 40}; the modern runs found 24–70 topics. Fix `random_state=42` and record `max_iter`, the priors (`doc_topic_prior`, `topic_word_prior`) and `learning_method`.
   - For each K, record perplexity, c_v coherence on the top 10 terms (reuse `h.coherence` so you're scored the same way), keyword diversity and fit time.
   - Pick K using coherence plus reading the topics yourself.
   - Refit the chosen K with seeds 7 and 21 and compare runs with `h.stability`, which gives the Adjusted Rand Index (ARI), to mirror the modern study.
5. **`interpret.py`**
   - Topic-word weights come from `components_`, normalized per topic; take the top 10 or more terms.
   - Get the document-topic mixture θ from `transform()`, take the dominant topic with argmax, and keep its probability.
   - For each topic, pull the articles with the highest θ as representatives.
   - Write labels by hand from those articles.
6. **`export.py` (the handoff contract)**
   - `assignments.csv`: `article_id`, `model='lda'`, `run_id`, `topic_id`, with exactly one row per article.
   - The full topic mixtures in a separate file, such as `mixtures.csv`.
   - `terms.csv`: `topic_id`, `rank` (starting at 1), `term`, `weight`.
   - `topics.csv`: `topic_id`, `label`, `count`. Counts must equal the dominant-topic counts.
   - `manifest.json`: `corpus_hash`, parameters, seeds, package versions, hardware, and stage timings (preprocessing, fitting, representation, evaluation). Record first-run and cached-run times separately.
   - Before handing off, run `h.validate_classical()` on your folder.
7. **Driver:** a `run_classical.py` script or notebook that runs steps 1–6 in order.
8. **Optional extras:** publication breakdowns with `h.publication_exports`, and a pyLDAvis visualization.

**Libraries:**

| Purpose | Library | Already in `pyproject.toml`? |
|---|---|---|
| Data, arrays | `pandas`, `numpy` | yes |
| Sparse matrix | `scipy.sparse` | yes, comes with sklearn |
| Tokenize, document-term matrix, LDA | `scikit-learn` (`CountVectorizer`, `LatentDirichletAllocation`) | yes |
| Coherence | `gensim` (through `topic_helpers.coherence`) | yes |
| Plots | `matplotlib` | yes |
| Manifest | stdlib `json`, `time`, `platform`, `importlib.metadata`, `hashlib` | built in |
| Interactive topic view | `pyLDAvis` | no, would need `uv add` |
| Lemmatization (not recommended) | `nltk` / `spaCy` | no |