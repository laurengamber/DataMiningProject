"""Fit LDA over a grid of topic counts and score each run with the shared metrics."""

# TODO: imports
#   - time, pandas, sklearn.decomposition.LatentDirichletAllocation.
#   - sys.path setup like preprocessing.py, then
#     `from shared.evaluation import coherence, reference_texts, stability` and
#     `from shared.corpus import SEED`.

# TODO: settings (copy them into manifest.json and the paper's hyperparameter table)
#   - K_GRID = [10, 15, 20, 25, 30, 40]  (the modern runs found 24-70 topics; cover that range)
#   - SEEDS = [42, 7, 21]                (42 for the grid; 7 and 21 for the stability refits)
#   - learning_method='batch', max_iter (start at ~20 and check perplexity has leveled off).
#   - Priors: the paper says "learned alpha, eta", but sklearn doesn't learn them.
#     Either set doc_topic_prior / topic_word_prior explicitly (sklearn defaults to 1/K)
#     or reword the paper. Record whichever you use.

# TODO: fit_lda(X, k, seed)
#   - LatentDirichletAllocation(n_components=k, random_state=seed, ...).fit(X)
#   - Time the fit (fit_seconds).
#   - Return the fitted model.

# TODO: top_terms(model, vocab, n=10)
#   - For each topic row of model.components_, normalize to sum to 1 and take the top n words.
#   - Return a DataFrame with columns topic_id, rank (from 1), term, weight. This is the same
#     schema as terms.csv, so coherence() and export.py can both use it unchanged.

# TODO: score_run(model, X, terms, texts, dictionary)
#   - perplexity: model.perplexity(X). Lower is better; report it but don't pick K by it alone.
#   - coherence: coherence(terms, texts, dictionary).coherence.mean(). Build texts and
#     dictionary ONCE with reference_texts(df) so LDA and BERTopic are scored identically.
#   - keyword_diversity: unique top-10 terms / (10 * K). This matches the modern metric.
#   - Return a dict with run_id like f'lda_k{k}_s{seed}', plus k, seed, the metrics, and fit_seconds.

# TODO: run_grid(X, vocab, texts, dictionary)
#   - Loop over K_GRID with seed 42, collecting score_run() dicts into a DataFrame.
#   - Save it as Results/classical/experiments.csv (it becomes the LDA grid table in the paper,
#     next to modern-methods/STATUS.md).

# TODO: choose K
#   - Use coherence, and read the top terms of the 2-3 best K values yourself. Note that c_v
#     tends to rise with K. Write down why you picked it, because the paper needs that reasoning.

# TODO: stability_check(X, k_chosen)
#   - Refit k_chosen with seeds 7 and 21. Take each article's dominant topic
#     (argmax of model.transform(X)) and compare each pair against seed 42 with stability(a, b),
#     which gives ARI.
#   - Save as Results/classical/stability.csv to mirror modern-methods/Results/modern/stability.csv.
