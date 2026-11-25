
from pathlib import Path
import statistics
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared.corpus import CORPUS_DIR, load_corpus
from shared.evaluation import reference_texts

from preprocessing import tokenize, filter_tokens, analyze_tokens
from representation import build_dtm
from sklearn.decomposition import LatentDirichletAllocation

from shared.corpus import SEED
from lda import run_grid, stability_check, top_terms, score_run, K_CHOSEN, MAX_ITER, LEARNING_METHOD, DOC_TOPIC_PRIOR, TOPIC_WORD_PRIOR, OUT

def load(folder=CORPUS_DIR):
    """Return the audited corpus, verified against the shared manifest's IDs and hash."""
    return load_corpus(folder)

def get_filtered_tokenized_articles():
    df = load()
    print(f'Loaded {len(df)} articles from {CORPUS_DIR}')

    tokenized_articles = tokenize(df)
    filtered_tokenized_articles = [filter_tokens(t) for t in tokenized_articles]

    token_lengths = [len(t) for t in filtered_tokenized_articles]
    print(f'Smallest article size: {min(token_lengths)} tokens')
    print(f'Largest article size: {max(token_lengths)} tokens')
    print(f'Median token per article count: {statistics.median(token_lengths)}')
    print(f'Mean token per article count: {statistics.mean(token_lengths)}')

    return df, filtered_tokenized_articles

def identify_stop_words():
    _, filtered_tokenized_articles = get_filtered_tokenized_articles()
    analyze_tokens(filtered_tokenized_articles)

def check_k():
    """Pick K"""
    df, filtered_tokenized_articles = get_filtered_tokenized_articles()
    texts, dictionary = reference_texts(df) # shared coherence reference

    X, vectorizer = build_dtm(filtered_tokenized_articles) # x is a vocabulary matrix

    vocab = vectorizer.get_feature_names_out()
    grid = run_grid(X, vocab, texts, dictionary) # creates experiments.csv

def check_convergence(k=40, iter_grid=(10, 25, 50, 100, 200)):
    """Pick max_iter: refit K=k at increasing max_iter and look for where perplexity levels off."""
    _, filtered_tokenized_articles = get_filtered_tokenized_articles()
    X, _ = build_dtm(filtered_tokenized_articles)

    for max_iter in iter_grid:
        model = LatentDirichletAllocation(n_components=k, random_state=SEED, learning_method=LEARNING_METHOD,
                                          max_iter=max_iter, doc_topic_prior=DOC_TOPIC_PRIOR,
                                          topic_word_prior=TOPIC_WORD_PRIOR).fit(X)
        print(f'max_iter={max_iter}: perplexity={model.perplexity(X):.1f}', flush=True)

def score_priors(alpha_values, eta_values):
    """Fit K_CHOSEN at each (doc_topic_prior, topic_word_prior) pair and print the shared metrics."""
    df, filtered_tokenized_articles = get_filtered_tokenized_articles()
    texts, dictionary = reference_texts(df)
    X, vectorizer = build_dtm(filtered_tokenized_articles)
    vocab = vectorizer.get_feature_names_out()

    for alpha in alpha_values:
        for eta in eta_values:
            start = time.time()
            model = LatentDirichletAllocation(n_components=K_CHOSEN, random_state=SEED, learning_method=LEARNING_METHOD,
                                              max_iter=MAX_ITER, doc_topic_prior=alpha, topic_word_prior=eta).fit(X)
            fit_seconds = time.time() - start
            m = score_run(model, X, top_terms(model, vocab), texts, dictionary, K_CHOSEN, SEED, fit_seconds)
            print(f"alpha={alpha}, eta={eta}: c_v={m['coherence']:.3f}, diversity={m['keyword_diversity']:.3f}, "
                  f"perplexity={m['perplexity']:.0f}, "
                  f"mean_dominant_prob={model.transform(X).max(axis=1).mean():.3f}", flush=True)

def check_doc_topic_prior(values=(0.01, 0.025, 0.1, 0.5, 1.0)):
    """Pick doc_topic_prior (alpha): keeps topic_word_prior fixed"""
    score_priors(values, [TOPIC_WORD_PRIOR])

def check_topic_word_prior(doc_topic_prior=DOC_TOPIC_PRIOR, values=(0.01, 0.025, 0.1, 0.5, 1.0)):
    """Pick topic_word_prior (eta): keeps doc_topic_prior fixed"""
    score_priors([doc_topic_prior], values)

check_topic_word_prior()