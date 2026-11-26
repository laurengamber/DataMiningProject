"""Document-term count matrix for LDA."""
from sklearn.feature_extraction.text import CountVectorizer

def build_dtm(token_lists, min_df=5, max_df=0.5):
    """Count pre-tokenized articles into a sparse articles x vocabulary matrix.

    min_df: number of articles a word must appear in to be kept
    max_df: words in more than 50% of articles are dropped
    """

    # The articles are already tokenized, so pass each token list through unchanged.
    vectorizer = CountVectorizer(analyzer=lambda tokens: tokens, min_df=min_df, max_df=max_df)
    # Learns vocabulary from articles, then turns into count matrix
    X = vectorizer.fit_transform(token_lists)

    n_articles, n_terms = X.shape
    empty = int((X.getnnz(axis=1) == 0).sum())
    print(f'Document-term matrix: {n_articles} articles x {n_terms} terms (min_df={min_df}, max_df={max_df})')
    print(f'Sparsity: {1 - X.nnz / (n_articles * n_terms):.4f}')
    print(f'Articles with no remaining terms: {empty}')
    if empty:
        print('WARNING: some articles have an all-zero row; decide how to handle them before fitting LDA')
    return X, vectorizer


def validate_matrix(X, vocabulary, article_ids):
    import numpy as np
    if X.shape != (len(article_ids), len(vocabulary)) or len(set(vocabulary)) != len(vocabulary):
        raise ValueError('Matrix dimensions or vocabulary do not match the article IDs')
    if len(set(article_ids)) != len(article_ids):
        raise ValueError('Duplicate article IDs in representation')
    if not np.isfinite(X.data).all() or (X.data < 0).any() or not np.equal(X.data, np.floor(X.data)).all():
        raise ValueError('LDA requires finite nonnegative counts')
    empty = [article_ids[i] for i in np.flatnonzero(X.getnnz(axis=1) == 0)]
    if empty:
        raise ValueError(f'Articles have no remaining terms; do not drop rows: {empty}')
    if len(vocabulary) < 10:
        raise ValueError('At least ten vocabulary terms are required for the shared metrics')


def preparation_identity(df, min_df=5, max_df=0.5):
    from shared.corpus import corpus_hash, digest
    from preprocessing import CUSTOM_STOPWORDS
    from pathlib import Path
    from notebook_artifacts import environment
    root = Path(__file__).resolve().parent
    return dict(corpus_hash=corpus_hash(df), article_ids=df.article_id.tolist(),
                min_df=min_df, max_df=max_df, custom_stopwords=sorted(CUSTOM_STOPWORDS),
                implementation_hash=digest([(root/p).read_text() for p in
                    ['preprocessing.py', 'representation.py', '../shared/evaluation.py']]),
                versions=environment()['versions'])


def load_representation(df, out, min_df=5, max_df=0.5):
    import json
    from pathlib import Path
    from scipy.sparse import load_npz
    from notebook_artifacts import verify_files
    out = Path(out)
    manifest = json.loads((out/'manifest.json').read_text())
    if manifest['identity'] != preparation_identity(df, min_df, max_df):
        raise ValueError('Stale count matrix; preserve its cache separately before rebuilding')
    verify_files(out, manifest['files'])
    X = load_npz(out/'counts.npz')
    vocabulary = json.loads((out/'vocabulary.json').read_text())
    validate_matrix(X, vocabulary, df.article_id.tolist())
    return X, vocabulary, manifest


def prepare_representation(df, out, min_df=5, max_df=0.5):
    """Save counts and their ordered vocabulary once; retain original measured timings."""
    import json
    import time
    import numpy as np
    import pandas as pd
    from pathlib import Path
    from scipy.sparse import save_npz
    from shared.corpus import write_json
    from preprocessing import tokenize, filter_tokens
    from notebook_artifacts import file_hash, environment
    out = Path(out)
    if (out/'manifest.json').exists():
        return load_representation(df, out, min_df, max_df)
    out.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    tokens = [filter_tokens(t) for t in tokenize(df)]
    preprocessing_seconds = time.perf_counter() - start
    lengths = np.array([len(t) for t in tokens])
    start = time.perf_counter()
    X, vectorizer = build_dtm(tokens, min_df=min_df, max_df=max_df)
    vocabulary = vectorizer.get_feature_names_out().tolist()
    validate_matrix(X, vocabulary, df.article_id.tolist())
    representation_seconds = time.perf_counter() - start
    save_npz(out/'counts.npz', X)
    write_json(out/'vocabulary.json', vocabulary)
    # Include counts, not article text or tokens, in the committed diagnostic table.
    pd.DataFrame(dict(article_id=df.article_id, filtered_tokens=lengths,
                      distinct_terms=X.getnnz(axis=1))).to_csv(out/'article_diagnostics.csv', index=False)
    manifest = dict(identity=preparation_identity(df, min_df, max_df),
                    summary=dict(articles=X.shape[0], vocabulary=X.shape[1],
                                 sparsity=1-X.nnz/(X.shape[0]*X.shape[1]), empty_rows=0,
                                 token_min=int(lengths.min()), token_median=float(np.median(lengths)),
                                 token_mean=float(lengths.mean()), token_max=int(lengths.max())),
                    timings=dict(preprocessing_seconds=preprocessing_seconds,
                                 representation_seconds=representation_seconds), environment=environment(),
                    files={name: file_hash(out/name) for name in
                           ['counts.npz', 'vocabulary.json', 'article_diagnostics.csv']})
    write_json(out/'manifest.json', manifest)
    return X, vocabulary, manifest
