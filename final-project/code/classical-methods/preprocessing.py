from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared.evaluation import analyzer, representation_text

def tokenize(df):
    """Tokenize each article's text exactly as the shared coherence dictionary does."""
    start = time.time()
    tokenizer = analyzer()
    results = [tokenizer(representation_text(t)) for t in df.text]
    end = time.time()
    print(f"Tokenizing took {end-start} seconds")
    return results

# TODO: custom stopwords and number-only tokens
