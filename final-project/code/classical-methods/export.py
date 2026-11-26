"""Write the classical handoff files that the joint comparison notebook reads."""
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared.corpus import SEED, corpus_hash, write_json
from shared.evaluation import validate_classical

from lda import CONFIG, OUT, LEARNING_METHOD, top_terms

def export_classical(df, model, theta, assignments, vocab, out=OUT):
    """Write assignments, mixtures, terms, topics, labels and manifest to out, then validate them."""
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    k = theta.shape[1]
    run_id = f"lda_k{k}_s{SEED}"

    # One row per article, in the row order of df.
    assignments = assignments.assign(article_id=df.article_id.astype(str).values, model='lda', run_id=run_id)
    assignments[['article_id', 'model', 'run_id', 'topic_id', 'membership_strength']].to_csv(out/'assignments.csv', index=False)

    # Full topic mixture per article, which the dominant topic alone throws away.
    mixtures = pd.DataFrame(theta, columns=[f'topic_{i}' for i in range(k)])
    mixtures.insert(0, 'article_id', df.article_id.astype(str).values)
    mixtures.to_csv(out/'mixtures.csv', index=False)

    terms = top_terms(model, vocab)
    terms.to_csv(out/'terms.csv', index=False)

    counts = assignments.topic_id.value_counts().reindex(range(k), fill_value=0)
    keywords = terms[terms['rank'] <= 4].groupby('topic_id').term.apply(lambda t: '_'.join(t))
    topics = pd.DataFrame(dict(topic_id=range(k), keyword_label=[f'{i}_{keywords[i]}' for i in range(k)],
                               count=counts.values))
    labels_path = out/'topic_labels.csv'
    if not labels_path.exists():
        topics.assign(manual_label='', evidence_notes='').to_csv(labels_path, index=False)
    manual = pd.read_csv(labels_path, keep_default_na=False).set_index('topic_id').manual_label
    topics['label'] = [manual.get(i, '').strip() or topics.keyword_label[i] for i in range(k)]
    topics[['topic_id', 'label', 'count']].to_csv(out/'topics.csv', index=False)

    write_json(out/'manifest.json', dict(corpus_hash=corpus_hash(df), run_id=run_id, seed=SEED,
                                         learning_method=LEARNING_METHOD, parameters=CONFIG))
    validate_classical(out, df.article_id.astype(str))
