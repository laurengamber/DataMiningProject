from pathlib import Path
import statistics
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared.corpus import CORPUS_DIR, load_corpus
from shared.evaluation import reference_texts
from shared.corpus import SEED

from preprocessing import tokenize, filter_tokens, analyze_tokens
from representation import build_dtm
from lda import fit_lda, stability_check, K_CHOSEN, OUT
from interpret import document_topics, representatives
from export import export_classical

def load(folder=CORPUS_DIR):
    """Return the audited corpus, verified against the shared manifest's IDs and hash."""
    return load_corpus(folder)

if __name__ == '__main__':
    df = load()
    print(f'Loaded {len(df)} articles from {CORPUS_DIR}')

    start = time.time()
    tokenized_articles = tokenize(df)
    end = time.time()
    print(f"Tokenizing took {end-start} seconds")
    print(f'Tokenized {len(tokenized_articles)} articles')

    start = time.time()
    filtered_tokenized_articles = [filter_tokens(t) for t in tokenized_articles]
    end = time.time()
    print(f"Filtering tokens took {end-start} seconds")
    print(f'{len(filtered_tokenized_articles)} articles remain after filtering')

    token_lengths = [len(t) for t in filtered_tokenized_articles]
    print(f'Smallest article size: {min(token_lengths)} tokens')
    print(f'Largest article size: {max(token_lengths)} tokens')
    print(f'Median token per article count: {statistics.median(token_lengths)}')
    print(f'Mean token per article count: {statistics.mean(token_lengths)}')

    texts, dictionary = reference_texts(df) # shared coherence reference

    start = time.time()
    X, vectorizer = build_dtm(filtered_tokenized_articles) # x is a vocabulary matrix
    end = time.time()
    print(f"Building the document term matrix took {end-start} seconds")

    start = time.time()
    model, fit_seconds = fit_lda(X, K_CHOSEN, SEED)
    end = time.time()
    print(f"Fitting the LDA model took {end-start} seconds")

    stability_check(X, K_CHOSEN, base_model=model) # Creates stability.csv (seeds 7, 21)

    theta, assignments = document_topics(model, X)  # interpret.py


    OUT.mkdir(parents=True, exist_ok=True)
    representatives(df, theta).to_csv(OUT/'representatives.csv', index=False)  # read these to label topics by hand

    # Writes assignments, mixtures, terms, topics, topic_labels (created once) and manifest, then validates.
    # Fill in manual_label in topic_labels.csv, then rerun to put your labels in topics.csv.
    export_classical(df, model, theta, assignments, vectorizer.get_feature_names_out())
