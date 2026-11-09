"""Fit LDA over a grid of topic counts and score each run with the shared metrics."""
from pathlib import Path
import sys
import time

import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared.corpus import SEED
from shared.evaluation import coherence, stability

K_GRID = [10, 20, 30, 40, 50, 60, 70]
SEEDS = [SEED, 7, 21]
LEARNING_METHOD = 'batch'
MAX_ITER = 20  
DOC_TOPIC_PRIOR = None
TOPIC_WORD_PRIOR = None
OUT = Path(__file__).resolve().parents[1]/'modern-methods/Results/classical'

def fit_lda(X, k, seed):
    """Fit one LDA model with k topics; return (model, fit_seconds)."""
    model = LatentDirichletAllocation(n_components=k, random_state=seed, learning_method=LEARNING_METHOD,
                                      max_iter=MAX_ITER, doc_topic_prior=DOC_TOPIC_PRIOR,
                                      topic_word_prior=TOPIC_WORD_PRIOR)
    start = time.time()
    model.fit(X)
    return model, time.time() - start

def top_terms(model, vocab, n=10):
    """Top n words per topic as topic_id, rank (from 1), term, weight, the terms.csv schema."""
    rows = []
    for topic_id, row in enumerate(model.components_):
        weights = row / row.sum()
        for rank, index in enumerate(weights.argsort()[::-1][:n], 1):
            rows.append(dict(topic_id=topic_id, rank=rank, term=vocab[index], weight=float(weights[index])))
    return pd.DataFrame(rows)

def score_run(model, X, terms, texts, dictionary, k, seed, fit_seconds):
    """Perplexity, mean c_v coherence, and keyword diversity for one fitted model."""
    start = time.time()
    per_topic = coherence(terms, texts, dictionary)
    top = terms[terms['rank'] <= 10]
    metrics = dict(run_id=f'lda_k{k}_s{seed}', k=k, seed=seed,
                   perplexity=float(model.perplexity(X)),
                   coherence=float(per_topic.coherence.mean()),
                   vocabulary_coverage=float(per_topic.vocabulary_coverage.mean()),
                   keyword_diversity=top.term.nunique() / len(top),
                   n_iter=int(model.n_iter_), doc_topic_prior=float(model.doc_topic_prior_),
                   topic_word_prior=float(model.topic_word_prior_), fit_seconds=fit_seconds)
    metrics['evaluation_seconds'] = time.time() - start
    return metrics

def run_grid(X, vocab, texts, dictionary, out=OUT):
    """Fit and score every K in K_GRID with seed 42; save experiments.csv and each run's top terms."""
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    records, all_terms = [], []
    for k in K_GRID:
        model, fit_seconds = fit_lda(X, k, SEED)
        terms = top_terms(model, vocab)
        metrics = score_run(model, X, terms, texts, dictionary, k, SEED, fit_seconds)
        print(f"{metrics['run_id']}: c_v={metrics['coherence']:.3f}, perplexity={metrics['perplexity']:.0f}, "
              f"diversity={metrics['keyword_diversity']:.3f}, fit={fit_seconds:.0f}s", flush=True)
        records.append(metrics)
        all_terms.append(terms.assign(run_id=metrics['run_id']))
    grid = pd.DataFrame(records)
    grid.to_csv(out/'experiments.csv', index=False)
    # Top terms for every K, to read when choosing K by hand.
    pd.concat(all_terms).to_csv(out/'grid_terms.csv', index=False)
    return grid

def stability_check(X, k_chosen, base_model=None, out=OUT):
    """Refit k_chosen with seeds 7 and 21 and compare dominant topics with seed 42 using ARI."""
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    if base_model is None:
        base_model, _ = fit_lda(X, k_chosen, SEED)
    base = base_model.transform(X).argmax(axis=1)
    rows = []
    for seed in SEEDS[1:]:
        other, _ = fit_lda(X, k_chosen, seed)
        rows.append(dict(seed=seed, **stability(base, other.transform(X).argmax(axis=1))))
    table = pd.DataFrame(rows)
    table.to_csv(out/'stability.csv', index=False)
    return table
