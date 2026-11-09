from pathlib import Path
import statistics
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared.corpus import CORPUS_DIR, load_corpus
from shared.evaluation import reference_texts

from preprocessing import tokenize, filter_tokens, analyze_tokens
from representation import build_dtm
from lda import run_grid, stability_check

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

    # Identify any necessary custom stop words
    # analyze_tokens(filtered_tokenized_articles)

    texts, dictionary = reference_texts(df) # shared coherence reference

    start = time.time()
    X, vectorizer = build_dtm(filtered_tokenized_articles)
    end = time.time()
    print(f"Building the document term matrix took {end-start} seconds")

    # Anaylze different options for k
    # vocab = vectorizer.get_feature_names_out()
    # grid = run_grid(X, vocab, texts, dictionary) # creates experiments.csv
   
    K_CHOSEN = 40
    stability_check(X, K_CHOSEN) # Creates stability.csv (seeds 7, 21)
    
    # theta, assignments = document_topics(model, X)  # interpret.py
    #   7. Write representatives, then label topics by hand.
    #   8. Export the files and run validate_classical()   # export.py

