"""Document-term count matrix for LDA."""

# TODO: imports
#   - time, numpy, and sklearn.feature_extraction.text.CountVectorizer.

# TODO: build_dtm(token_lists, min_df=5, max_df=0.5)
#   - The articles are already tokenized by preprocessing.tokenize(), so stop CountVectorizer
#     from re-tokenizing them:
#         CountVectorizer(analyzer=lambda tokens: tokens, min_df=min_df, max_df=max_df)
#   - Use counts, not TF-IDF: LDA's generative model assumes integer word counts.
#   - min_df=5 / max_df=0.5 match the paper's proposed hyperparameters and BERTopic's
#     vocabulary_min_article_frequency=5. If you change them, update the paper.
#   - Return (X, vectorizer): X is the sparse articles x vocab matrix, and the vectorizer
#     carries get_feature_names_out(), which interpret.py needs to map columns back to words.

# TODO: log matrix statistics (report these in the Methodology section)
#   - Vocabulary size: len(vectorizer.vocabulary_).
#   - Sparsity: 1 - X.nnz / (X.shape[0] * X.shape[1]).
#   - Articles left with an all-zero row after min_df/max_df (should be 0; if not, decide
#     whether to drop them and document it, because validate_classical() requires every article).
#   - Seconds taken (manifest stage timing: representation_seconds).
