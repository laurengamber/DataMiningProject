"""LDA mixtures, nonreserved development examples, and editable team labels."""

from pathlib import Path
import json
import numpy as np
import pandas as pd
from shared.corpus import write_json


def document_topics(model, X):
    theta = model.transform(X)
    validate_mixtures(theta, X.shape[0], model.n_components)
    return theta, theta.argmax(axis=1)


def validate_mixtures(theta, rows, topics):
    if (theta.shape != (rows, topics) or not np.isfinite(theta).all()
            or (theta < 0).any() or not np.allclose(theta.sum(axis=1), 1)):
        raise ValueError('Topic mixtures must be finite, nonnegative, normalized, and aligned')


def representatives(df, theta, reserved_ids, n=3):
    """Highest per-topic probabilities, including topics with no dominant articles."""
    validate_mixtures(theta, len(df), theta.shape[1])
    reserved = set(map(str, reserved_ids))
    eligible = [i for i, article_id in enumerate(df.article_id) if article_id not in reserved]
    evidence = []
    for topic in range(theta.shape[1]):
        ordered = sorted(eligible, key=lambda i: (-float(theta[i, topic]), str(df.iloc[i].article_id)))[:n]
        for rank, i in enumerate(ordered, 1):
            row = df.iloc[i]
            evidence.append(dict(topic_id=topic, rank=rank, article_id=row.article_id,
                                 title=row.title, publication=row.publication, text=row.text,
                                 topic_probability=float(theta[i, topic]),
                                 dominant_topic=int(theta[i].argmax())))
    return pd.DataFrame(evidence, columns=['topic_id', 'rank', 'article_id', 'title',
                                         'publication', 'text', 'topic_probability', 'dominant_topic'])


def labels_table(folder, out, identity):
    """Preserve human edits and require evidence belonging to this run and topic."""
    folder, out = Path(folder), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    binding, path = out/'labels_identity.json', out/'topic_labels.csv'
    if binding.exists() and json.loads(binding.read_text()) != identity:
        raise ValueError('Labels belong to a different selected run')
    if path.exists() and not binding.exists():
        raise ValueError('Existing labels lack a run identity')
    topics = pd.read_csv(folder/'topics.csv')
    reps = pd.read_csv(folder/'representative_ids.csv', dtype={'article_id': str})
    if not path.exists():
        table = topics.rename(columns={'label': 'keyword_label'})
        table['proposed_label'] = ''
        table['evidence_ids'] = table.topic_id.map(reps.groupby('topic_id').article_id.agg(' | '.join)).fillna('')
        table['evidence_notes'] = ''
        table['confirmed'] = False
        write_json(binding, identity)
        table.to_csv(path, index=False)
    table = pd.read_csv(path, keep_default_na=False)
    required = {'topic_id', 'proposed_label', 'evidence_ids', 'evidence_notes', 'confirmed'}
    if not required.issubset(table.columns):
        raise ValueError('Label table is missing required columns')
    if table.topic_id.duplicated().any() or set(table.topic_id) != set(topics.topic_id):
        raise ValueError('Label topic IDs do not match the selected model')
    if not table.confirmed.astype(str).str.lower().isin(['true', 'false']).all():
        raise ValueError('Label confirmation must be true or false')
    for row in table.itertuples():
        evidence = {v.strip() for v in str(row.evidence_ids).split('|') if v.strip()}
        valid = set(reps.loc[reps.topic_id.eq(row.topic_id), 'article_id'])
        if not evidence.issubset(valid):
            raise ValueError('Label evidence must use this topic’s nonreserved development representatives')
        if str(row.confirmed).lower() == 'true' and (
                not evidence or not row.proposed_label.strip() or not row.evidence_notes.strip()):
            raise ValueError('Confirmed labels require a name and supporting evidence')
    return table


def topic_inventory(folder, out, n_articles, labels=None):
    folder, out = Path(folder), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    topics = pd.read_csv(folder/'topics.csv').rename(columns={'label': 'keyword_label'})
    terms = pd.read_csv(folder/'terms.csv')
    reps = pd.read_csv(folder/'representative_ids.csv', dtype={'article_id': str})
    topics['keywords'] = topics.topic_id.map(terms.sort_values('rank').groupby('topic_id').term.agg(', '.join))
    topics['prevalence'] = topics['count'] / n_articles
    topics['representative_article_ids'] = topics.topic_id.map(reps.groupby('topic_id').article_id.agg(' | '.join)).fillna('')
    topics = topics.merge(pd.read_csv(folder/'coherence.csv'), on='topic_id', validate='one_to_one')
    topics['label'] = topics.keyword_label
    topics['label_status'] = 'keywords only; team interpretation pending'
    if labels is not None:
        confirmed = labels.loc[labels.confirmed.astype(str).str.lower().eq('true')].set_index('topic_id')
        mask = topics.topic_id.isin(confirmed.index)
        topics.loc[mask, 'label'] = topics.loc[mask, 'topic_id'].map(confirmed.proposed_label)
        topics.loc[mask, 'label_status'] = 'team confirmed'
    topics.to_csv(out/'topic_inventory.csv', index=False)
    return topics
