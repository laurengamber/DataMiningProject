"""Separate, reproducible follow-up experiments; never write selected model exports.

Run with the repository .venv. Each completed run is immutable and checksum-bound.
The split is exploratory: full-corpus development already influenced fixed choices.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata as metadata
import json
import os
import platform
import sys
import time

import numpy as np
import pandas as pd

CODE = Path(__file__).resolve().parents[1]
ROOT = CODE.parents[1]
MODERN = CODE / 'modern-methods'
OUT = MODERN / 'Results/robustness/2026-11-25'
sys.path[:0] = [str(CODE), str(MODERN), str(CODE / 'classical-methods')]
from shared.corpus import load_corpus, corpus_hash, digest, write_json
from shared.evaluation import (aligned_assignments, coherence, reference_texts,
                               representation_text, stability)


def checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def environment():
    from threadpoolctl import threadpool_info
    return dict(platform=platform.platform(), machine=platform.machine(),
                processor=platform.processor(), cpu_count=os.cpu_count(), python=sys.version,
                packages={p: metadata.version(p) for p in ['numpy', 'scipy', 'scikit-learn',
                           'bertopic', 'hdbscan', 'umap-learn', 'gensim']},
                threadpools=threadpool_info(), thread_limit=1,
                cache='Pretrained article embeddings reused; no fitted topic model reused',
                timing='New wall-clock measurements, serial fits; imports and file writes excluded')


def stratified_split(df, seed=42):
    """Round 20% within publication/year, clamp to [1,n-1]; singleton -> training.

    Sorted IDs and groups make membership independent of input row order. This is
    approximately 80/20, not a forced global count that sacrifices tiny strata.
    """
    rng = np.random.default_rng(seed)
    result = df[['article_id', 'publication', 'date']].copy()
    result['year'] = pd.to_datetime(result.date).dt.year
    result['partition'] = 'train'
    rows = []
    for (publication, year), group in result.groupby(['publication', 'year'], sort=True):
        ids = sorted(group.article_id.astype(str))
        n = len(ids)
        count = min(n - 1, max(1, int(np.floor(n * .2 + .5)))) if n > 1 else 0
        held = set(rng.choice(ids, size=count, replace=False))
        result.loc[result.article_id.isin(held), 'partition'] = 'heldout'
        rows.append(dict(publication=publication, year=int(year), n=n,
                         train=n-count, heldout=count, singleton_train_only=n == 1))
    return result, pd.DataFrame(rows)


def prepare(df):
    OUT.mkdir(parents=True, exist_ok=True)
    split, strata = stratified_split(df)
    path = OUT / 'split_ids.csv'
    if path.exists():
        old = pd.read_csv(path, dtype={'article_id': str})
        pd.testing.assert_frame_equal(old, split, check_dtype=False)
    else:
        split.to_csv(path, index=False)
        strata.to_csv(OUT / 'split_strata.csv', index=False)
    protocol = dict(corpus_hash=corpus_hash(df), seed=42,
                    split_hash=digest(split[['article_id', 'partition']].values.tolist()),
                    n_train=int(split.partition.eq('train').sum()),
                    n_heldout=int(split.partition.eq('heldout').sum()),
                    singleton_strata=int(strata.singleton_train_only.sum()),
                    rule='Sorted publication/year strata and IDs; numpy default_rng(42); round half up 20%, clamp to 1..n-1; singletons training only',
                    disclosure='Exploratory robustness check, not untouched testing: full-corpus vocabulary/configuration development preceded this split. Fixed selected settings, no held-out tuning. Cached pretrained per-article embeddings allowed; training-only fitted vocabulary, UMAP, clustering and LDA.',
                    reservation='100 human-review IDs unchanged; reserved from naming, not unsupervised fitting',
                    duplicate_limit='Near duplicates and syndicated stories can cross partitions; this is not a story-group holdout')
    write_json(OUT / 'split_protocol.json', protocol)
    return split, protocol


def identity(df, kind, split=None):
    sources = [Path(__file__), CODE/'classical-methods/preprocessing.py',
               CODE/'classical-methods/representation.py', CODE/'classical-methods/lda.py',
               CODE/'shared/evaluation.py', CODE/'modern-methods/src/topic_helpers.py']
    return dict(corpus_hash=corpus_hash(df), kind=kind, split_hash=split,
                sources={str(p.relative_to(ROOT)): checksum(p) for p in sources},
                selected_lda=json.loads((CODE/'classical-methods/selected_configuration.json').read_text()))


def cached(folder, ident):
    manifest = folder / 'manifest.json'
    if not manifest.exists():
        if folder.exists() and any(folder.iterdir()):
            raise ValueError(f'Incomplete run {folder}; preserve it separately before retrying')
        folder.mkdir(parents=True, exist_ok=True)
        return False
    saved = json.loads(manifest.read_text())
    if saved['identity'] != ident:
        raise ValueError(f'Identity changed: preserve {folder} and use a new experiment directory')
    for name, expected in saved['files'].items():
        if checksum(folder/name) != expected:
            raise ValueError(f'Changed run artifact: {folder/name}')
    print(f'Reused verified exports: {folder.name}', flush=True)
    return True


def finish(folder, ident, metrics, timings, extra=None):
    files = {p.name: checksum(p) for p in folder.iterdir() if p.is_file() and p.name != 'manifest.json'}
    write_json(folder/'manifest.json', dict(identity=ident, metrics=metrics, timings=timings,
               environment=environment(), files=files, **(extra or {})))
    print(folder.name, metrics, timings, flush=True)


def fit_lda_runs(df, split, protocol):
    from preprocessing import tokenize, filter_tokens
    from representation import build_dtm
    from lda import fit_lda, top_terms
    from threadpoolctl import threadpool_limits
    for name, seed, use_split in [('lda_full_s42', 42, False), ('lda_full_s7', 7, False),
                                  ('lda_full_s21', 21, False), ('lda_split_s42', 42, True)]:
        folder = OUT/name
        ident = identity(df, name, protocol['split_hash'] if use_split else None)
        if cached(folder, ident):
            continue
        train = split.partition.eq('train').to_numpy() if use_split else np.ones(len(df), dtype=bool)
        timings = {}
        with threadpool_limits(limits=1):
            started = time.perf_counter()
            tokens = [filter_tokens(t) for t in tokenize(df)]
            timings['preprocessing_seconds'] = time.perf_counter()-started
            started = time.perf_counter()
            xtrain, vectorizer = build_dtm([t for t, keep in zip(tokens, train) if keep])
            timings['representation_train_seconds'] = time.perf_counter()-started
            started = time.perf_counter()
            xall = vectorizer.transform(tokens)
            timings['representation_all_transform_seconds'] = time.perf_counter()-started
            print(f'{name}: fitting {train.sum()} articles', flush=True)
            model, elapsed = fit_lda(xtrain, 40, seed)
            timings['fit_seconds'] = elapsed
            started = time.perf_counter()
            theta = model.transform(xall)
            timings['assignment_all_seconds'] = time.perf_counter()-started
            terms = top_terms(model, vectorizer.get_feature_names_out())
            started = time.perf_counter()
            reference = df.loc[~train] if use_split else df
            texts, dictionary = reference_texts(reference)
            per_topic = coherence(terms, texts, dictionary)
            metrics = dict(n_train=int(train.sum()), n_reference=len(reference),
                           topic_count=40, coherence=float(per_topic.coherence.mean()),
                           vocabulary_coverage=float(per_topic.vocabulary_coverage.mean()),
                           perplexity=float(model.perplexity(xall[~train] if use_split else xtrain)),
                           perplexity_reference='heldout' if use_split else 'training',
                           empty_train_rows=int((xtrain.getnnz(axis=1)==0).sum()),
                           empty_reference_rows=int((xall[~train if use_split else train].getnnz(axis=1)==0).sum()),
                           vocabulary_size=len(vectorizer.vocabulary_), n_iter=int(model.n_iter_))
            timings['evaluation_seconds'] = time.perf_counter()-started
        assignments = pd.DataFrame(dict(article_id=df.article_id, model='lda', run_id=name,
                                        topic_id=theta.argmax(axis=1), membership_strength=theta.max(axis=1)))
        if use_split:
            assignments['partition'] = split.partition
        assignments.to_csv(folder/'assignments.csv', index=False)
        np.save(folder/'mixtures.npy', theta)
        np.save(folder/'components.npy', model.components_)
        terms.to_csv(folder/'terms.csv', index=False)
        per_topic.to_csv(folder/'coherence.csv', index=False)
        write_json(folder/'vocabulary.json', vectorizer.vocabulary_)
        if not use_split:
            baseline = pd.read_csv(CODE/'classical-methods/results/assignments.csv', dtype={'article_id': str})
            baseline = aligned_assignments(df, baseline)
            metrics.update(stability(baseline.topic_id, assignments.topic_id))
            metrics['exact_assignment_fraction_vs_original_s42'] = float(np.mean(baseline.topic_id.to_numpy()==assignments.topic_id.to_numpy()))
        finish(folder, ident, metrics, timings)


def fit_modern_runs(df, split, protocol):
    from bertopic import BERTopic
    from umap import UMAP
    from hdbscan import HDBSCAN
    from sklearn.feature_extraction.text import CountVectorizer
    from src.topic_helpers import load_inputs, term_table
    from threadpoolctl import threadpool_limits
    import numba
    numba.set_num_threads(1)
    started = time.perf_counter()
    loaded, embeddings = load_inputs(MODERN)
    assert loaded.article_id.tolist() == df.article_id.tolist()
    embedding_load = time.perf_counter()-started
    for name, use_split in [('bertopic_full_s42_timing', False), ('bertopic_split_s42', True)]:
        folder = OUT/name
        ident = identity(df, name, protocol['split_hash'] if use_split else None)
        ident['embedding_pointer_hash'] = checksum(MODERN/'Results/modern/embedding_pointer.json')
        if cached(folder, ident):
            continue
        train = split.partition.eq('train').to_numpy() if use_split else np.ones(len(df), dtype=bool)
        timings = {'embedding_cache_load_validation_seconds': embedding_load,
                   'embedding_compute_seconds': None}
        with threadpool_limits(limits=1):
            started = time.perf_counter()
            documents = df.loc[train, 'text'].tolist()
            processed = [representation_text(t) for t in documents]
            timings['preprocessing_train_seconds'] = time.perf_counter()-started
            started = time.perf_counter()
            vocabulary = CountVectorizer(stop_words='english', min_df=5).fit(processed).vocabulary_
            timings['vocabulary_train_seconds'] = time.perf_counter()-started
            model = BERTopic(embedding_model=None,
                umap_model=UMAP(n_neighbors=30, n_components=5, min_dist=0, metric='cosine', random_state=42, n_jobs=1),
                hdbscan_model=HDBSCAN(min_cluster_size=25, min_samples=10, metric='euclidean',
                                     cluster_selection_method='eom', prediction_data=True, core_dist_n_jobs=1),
                vectorizer_model=CountVectorizer(stop_words='english', vocabulary=vocabulary),
                top_n_words=10, calculate_probabilities=False, verbose=False)
            print(f'{name}: fitting {train.sum()} articles', flush=True)
            started = time.perf_counter()
            labels, _ = model.fit_transform(documents, embeddings=embeddings[train])
            timings['fit_representation_seconds'] = time.perf_counter()-started
            assigned = np.full(len(df), -1, dtype=int)
            assigned[train] = labels
            started = time.perf_counter()
            if use_split:
                held, _ = model.transform(df.loc[~train, 'text'].tolist(), embeddings=embeddings[~train])
                assigned[~train] = held
            timings['heldout_assignment_seconds'] = time.perf_counter()-started
            terms = term_table(model)
            started = time.perf_counter()
            reference = df.loc[~train] if use_split else df
            texts, dictionary = reference_texts(reference)
            per_topic = coherence(terms, texts, dictionary)
            metrics = dict(n_train=int(train.sum()), n_reference=len(reference),
                           topic_count=int(len(set(labels)-{-1})),
                           coherence=float(per_topic.coherence.mean()),
                           vocabulary_coverage=float(per_topic.vocabulary_coverage.mean()),
                           train_outlier_fraction=float(np.mean(assigned[train]==-1)),
                           heldout_outlier_fraction=float(np.mean(assigned[~train]==-1)) if use_split else None,
                           vocabulary_size=len(vocabulary))
            timings['evaluation_seconds'] = time.perf_counter()-started
        assignments = pd.DataFrame(dict(article_id=df.article_id, model='bertopic', run_id=name, topic_id=assigned))
        if use_split:
            assignments['partition'] = split.partition
        assignments.to_csv(folder/'assignments.csv', index=False)
        terms.to_csv(folder/'terms.csv', index=False)
        per_topic.to_csv(folder/'coherence.csv', index=False)
        write_json(folder/'vocabulary.json', vocabulary)
        if not use_split:
            base = aligned_assignments(df, pd.read_csv(MODERN/'Results/modern/runs/n30_c25_s42/assignments.csv', dtype={'article_id': str}))
            metrics.update(stability(base.topic_id, assigned))
        finish(folder, ident, metrics, timings, {'warmup': 'First fit includes possible UMAP JIT compilation; second fit has warm process caches. No speed ranking from these single executions.'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['prepare', 'lda', 'modern'])
    args = parser.parse_args()
    df = load_corpus()
    split, protocol = prepare(df)
    if args.phase == 'lda':
        fit_lda_runs(df, split, protocol)
    elif args.phase == 'modern':
        fit_modern_runs(df, split, protocol)


if __name__ == '__main__':
    main()
