"""Validation and provisional interpretation for saved comparison artifacts.

Kept outside fitting helpers so reporting changes do not invalidate model caches.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd


def comparison_classical_labels(folder, source, topics, manifest, reservation_hash):
    """Apply comparison-owned names to a copy, binding them to untouched LDA exports."""
    folder, source = Path(folder), Path(source)
    names = ['classical_labels.csv', 'classical_labels_identity.json']
    present = [(folder / name).exists() for name in names]
    if not any(present):
        return topics.copy(), False, {}
    if not all(present):
        raise ValueError('Classical comparison labels require both table and identity')
    identity = json.loads((folder / names[1]).read_text())
    if (identity['corpus_hash'] != manifest['corpus_hash'] or
            identity['run_id'] != manifest['run_id'] or
            identity['review_reservation_hash'] != reservation_hash):
        raise ValueError('Classical comparison label corpus, run or reservation differs')
    required = ['assignments.csv', 'terms.csv', 'topics.csv', 'manifest.json']
    hashes = {name: hashlib.sha256((source / name).read_bytes()).hexdigest()
              for name in required}
    if identity['source_files'] != hashes:
        raise ValueError('Classical comparison labels belong to different source exports')
    label_hash = hashlib.sha256((folder / names[0]).read_bytes()).hexdigest()
    if identity['labels_sha256'] != label_hash:
        raise ValueError('Classical comparison labels changed after confirmation')
    labels = pd.read_csv(folder / names[0], keep_default_na=False).set_index('topic_id')
    if not labels.index.is_unique or set(labels.index) != set(topics.topic_id):
        raise ValueError('Classical comparison label topic IDs differ')
    if labels.manual_label.str.strip().eq('').any() or labels.evidence_notes.str.strip().eq('').any():
        raise ValueError('Classical comparison labels require names and evidence notes')
    ready = identity.get('labels_confirmed') is True
    if ready and set(identity.get('confirmed_topic_ids', [])) != set(topics.topic_id):
        raise ValueError('Classical comparison confirmation must cover every topic')
    result = topics.copy()
    if ready:
        result['label'] = result.topic_id.map(labels.manual_label)
    binding = {name: hashlib.sha256((folder / name).read_bytes()).hexdigest() for name in names}
    return result, ready, binding


# Status rows for the completed November 25 follow-up (paths relative to modern-methods/).
ROBUSTNESS_EVIDENCE = [
    ('Robustness', 'Exploratory 80/20 split', 'computed; prior full-corpus development disclosed',
     'Results/robustness/2026-11-25/split_metrics.csv; split_protocol.json'),
    ('Robustness', 'Shared-period publication sensitivity', 'computed; existing fits restricted to coverage period',
     'Results/robustness/2026-11-25/shared_period/'),
    ('Robustness', 'Seed/publication and hyperparameter sensitivity', 'computed; automatic matches require interpretation',
     'Results/robustness/2026-11-25/sensitivity_summary.csv; principal_theme_sensitivity.csv'),
    ('Human validation', '110-topic label review', '110/110 approved in assisted naming review',
     'Results/robustness/2026-11-25/label_review/team_decisions.csv'),
    ('Data audit', '30-article corpus audit', 'new dated assisted audit complete (30/30); original PR2 judgments unavailable',
     'Results/robustness/2026-11-25/audit_review/2026-11-25/human_judgments.csv'),
]


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
