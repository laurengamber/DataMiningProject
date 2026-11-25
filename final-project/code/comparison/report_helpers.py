"""Validation and provisional interpretation for saved comparison artifacts.

Kept outside fitting helpers so reporting changes do not invalidate model caches.
"""
from pathlib import Path
import numpy as np
import pandas as pd


def validate_mixtures(folder, assignments, topics):
    """Check optional full LDA mixtures against aligned dominant assignments."""
    path = Path(folder) / 'mixtures.csv'
    if not path.exists():
        return {'mixtures_status': 'unavailable'}
    mixtures = pd.read_csv(path, dtype={'article_id': str})
    if not mixtures.article_id.is_unique or set(mixtures.article_id) != set(assignments.article_id):
        raise ValueError('LDA mixture article IDs differ from assignments')
    ids = sorted(topics.topic_id.astype(int))
    columns = [f'topic_{t}' for t in ids]
    if set(mixtures.columns) != {'article_id', *columns}:
        raise ValueError('LDA mixture columns differ from topics')
    values = mixtures.set_index('article_id').loc[assignments.article_id, columns].to_numpy()
    if not np.isfinite(values).all() or (values < 0).any() or not np.allclose(values.sum(axis=1), 1):
        raise ValueError('Invalid LDA mixture probabilities')
    if not np.array_equal(np.array(ids)[values.argmax(axis=1)], assignments.topic_id):
        raise ValueError('LDA mixture dominant topics differ from assignments')
    dominant = values.max(axis=1)
    if 'membership_strength' in assignments and not np.allclose(dominant, assignments.membership_strength):
        raise ValueError('LDA mixture strengths differ from assignments')
    return dict(mixtures_status='validated', article_count=len(values),
                mean_dominant_probability=float(dominant.mean()),
                median_dominant_probability=float(np.median(dominant)),
                fraction_dominant_below_half=float((dominant < .5).mean()))


def draft_inventory(model, topics, terms, scores, representatives, out, reserved_ids):
    """Preserve editable drafts; never promote them to confirmed review labels."""
    out = Path(out)
    assigned = topics.loc[topics.topic_id.ge(0)].copy()
    reps = representatives.copy()
    reps['article_id'] = reps.article_id.astype(str)
    if set(reps.article_id) & set(map(str, reserved_ids)):
        raise ValueError('Reserved review articles appear in development evidence')
    evidence = reps.sort_values(['topic_id', 'rank']).groupby('topic_id').article_id.agg(' | '.join)
    path = out / f'{model}_draft_labels.csv'
    if not path.exists():
        pd.DataFrame(dict(topic_id=assigned.topic_id,
                          proposed_label='', evidence_notes='',
                          evidence_ids=assigned.topic_id.map(evidence).fillna(''),
                          label_status='assistant draft; unconfirmed')).to_csv(path, index=False)
    drafts = pd.read_csv(path, keep_default_na=False, dtype={'evidence_ids': str})
    if drafts.topic_id.duplicated().any() or set(drafts.topic_id) != set(assigned.topic_id):
        raise ValueError('Draft label topic IDs differ from model topics')
    for row in drafts.itertuples():
        ids = {x.strip() for x in row.evidence_ids.split('|') if x.strip()}
        if not ids.issubset(set(reps.loc[reps.topic_id.eq(row.topic_id), 'article_id'])):
            raise ValueError('Draft evidence must use nonreserved topic representatives')
        if row.proposed_label.strip() and (not ids or not row.evidence_notes.strip()):
            raise ValueError('Draft labels require evidence IDs and notes')
        if row.label_status != 'assistant draft; unconfirmed':
            raise ValueError('Comparison drafts cannot confirm team labels')
    inventory = assigned.merge(drafts, on='topic_id', validate='one_to_one')
    inventory['model'] = model
    inventory['prevalence'] = inventory['count'] / topics['count'].sum()
    inventory['keywords'] = inventory.topic_id.map(
        terms.sort_values('rank').groupby('topic_id').term.agg(', '.join))
    inventory = inventory.merge(scores, on='topic_id', validate='one_to_one')
    inventory.to_csv(out / f'{model}_draft_inventory.csv', index=False)
    return inventory
