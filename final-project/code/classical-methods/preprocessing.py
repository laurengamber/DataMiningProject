from collections import Counter
from pathlib import Path
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared.evaluation import analyzer, representation_text

CUSTOM_STOPWORDS = {
    # reporting verbs and filler
    "said", "says", "say", "told", "according", "like", "just", "thats", "dont", "did",
    "going", "think", "lot", "right", "way", "make", "making", "use", "used", "using",
    "need", "want", "come", "able", "called", "including", "big", "long", "far", "better",
    "end", "number", "new", "time", "year", "years", "week", "today", "early", "earlier",
    # words that define the corpus and appear in most articles
    "selfdriving", "autonomous", "cars", "car", "vehicles", "vehicle",
    "company", "companies", "companys", "technology",
}
STOPWORDS = ENGLISH_STOP_WORDS | CUSTOM_STOPWORDS

def tokenize(df):
    """Tokenize each article's text exactly as the shared coherence dictionary does."""
    tokenizer = analyzer()
    results = [tokenizer(representation_text(t)) for t in df.text]
    return results


def analyze_tokens(tokenized_articles, n=100):
    """Print the n tokens found in the most articles, to help pick CUSTOM_STOPWORDS by hand.

    Ranked by document frequency (how many articles contain the token), not raw count, since a
    stopword is a word that shows up everywhere rather than one that is repeated a lot in a few
    articles. Expects articles that have already been through filter_tokens().
    """
    doc_counts = Counter()
    total_counts = Counter()
    for tokens in tokenized_articles:
        doc_counts.update(set(tokens))
        total_counts.update(tokens)

    num_articles = len(tokenized_articles)
    print(f"{'rank':>4}  {'token':<16} {'articles':>8} {'% articles':>10} {'total':>7}")
    for rank, (token, count) in enumerate(doc_counts.most_common(n), 1):
        print(f"{rank:>4}  {token:<16} {count:>8} {count / num_articles:>10.0%} {total_counts[token]:>7}")

def filter_tokens(tokens):
    """Drop stopwords, number-only tokens, and 1-2 character tokens from one article's tokens."""
    filtered_tokens = [t for t in tokens if t not in STOPWORDS and not t.isdigit() and len(t) >= 3]
    return filtered_tokens
