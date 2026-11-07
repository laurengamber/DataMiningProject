from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared.corpus import CORPUS_DIR, load_corpus
from preprocessing import tokenize

def load(folder=CORPUS_DIR):
    """Return the audited corpus, verified against the shared manifest's IDs and hash."""
    return load_corpus(folder)

if __name__ == '__main__':
    df = load()
    print(f'Loaded {len(df)} articles from {CORPUS_DIR}')

    tokenized_df = tokenize(df)
    print(f'Tokenized {len(tokenized_df)} articles')

