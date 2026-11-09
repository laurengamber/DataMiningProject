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
