"""Shared corpus construction and hashing so both pipelines fit the same articles."""
from pathlib import Path
import hashlib, html, json, re
import pandas as pd

SEED = 42
DATA = Path(__file__).resolve().parents[2]/'data/self_driving_articles.csv'

def write_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=str))

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

def corpus_hash(df):
    return digest(df[['article_id','text']].values.tolist())

def clean_text(text):
    # Only strip recognizable HTML tags, preserving comparisons and punctuation.
    text = re.sub(r'</?(?:p|div|span|br|a|strong|em|ul|li|h[1-6]|script|style)\b[^>]*>', ' ', str(text), flags=re.I)
    return re.sub(r'\s+', ' ', html.unescape(text)).strip()

def audit_corpus(root, source=DATA):
    root = Path(root); out = root/'Results/modern'; out.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(source)
    assert df.X1.notna().all() and df.X1.is_unique, 'Article IDs must be unique'
    df.insert(0, 'article_id', df.X1.astype(str))
    assert df.article.notna().all() and df.publication.notna().all()
    df['date'] = pd.to_datetime(df.date, errors='raise').dt.strftime('%Y-%m-%d')
    df['text'] = df.article.map(clean_text)
    assert df.text.str.len().gt(0).all()
    df['duplicate_body'] = df.article.duplicated(keep='first')
    df['measured_word_count'] = df.article.str.split().str.len()
    df['word_count_difference'] = df.measured_word_count - df.word_count
    summary = dict(rows=len(df), source_columns=15, publications=df.publication.nunique(),
                   date_min=df.date.min(), date_max=df.date.max(), duplicate_bodies=int(df.duplicate_body.sum()),
                   missing=df.isna().sum().to_dict(), word_count_mismatches=int(df.word_count_difference.ne(0).sum()),
                   word_quantiles=df.measured_word_count.quantile([0,.25,.5,.75,.9,.99,1]).to_dict())
    df.to_csv(out/'corpus.csv', index=False)
    write_json(out/'corpus_summary.json', summary)
    if not (out/'corpus_review.csv').exists():
        df.sample(min(30,len(df)), random_state=SEED).assign(boilerplate='', malformed='', relevance='', notes='').to_csv(out/'corpus_review.csv',index=False)
    write_json(out/'corpus_manifest.json', dict(article_ids=df.article_id.tolist(), corpus_hash=corpus_hash(df)))
    return df, summary

def load_corpus(root):
    """Read the audited corpus and verify it against its manifest."""
    out = Path(root)/'Results/modern'
    df = pd.read_csv(out/'corpus.csv', dtype={'article_id':str})
    manifest = json.loads((out/'corpus_manifest.json').read_text())
    if manifest['article_ids'] != df.article_id.tolist() or manifest['corpus_hash'] != corpus_hash(df): raise ValueError('Corpus/manifest mismatch')
    return df
