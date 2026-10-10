"""Run notebook 01's expensive embedding stage with resumable local caches."""
from pathlib import Path
from src.topic_helpers import audit_corpus, embed_corpus

if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    df, _ = audit_corpus(root)
    embed_corpus(df.sample(200, random_state=42).sort_index(), root, pilot=True)
    embed_corpus(df, root)
