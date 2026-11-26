"""Validation and provisional interpretation for saved comparison artifacts.

Kept outside fitting helpers so reporting changes do not invalidate model caches.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd


def followup_checklists(evidence, completion, root, corpus_hash, scope='comparison'):
    """Reflect separate follow-up results without promoting labels or human ratings."""
    folder = Path(root) / 'Results/robustness/2026-11-25'
    required = ['lda_full_s42', 'lda_full_s7', 'lda_full_s21',
                'lda_split_s42', 'bertopic_full_s42_timing', 'bertopic_split_s42']
    manifests = []
    for name in required:
        path = folder / name / 'manifest.json'
        if not path.exists():
            return evidence, completion
        record = json.loads(path.read_text())
        if record['identity']['corpus_hash'] != corpus_hash:
            raise ValueError('Follow-up evidence belongs to a different corpus')
        manifests.append(record)
    if not all((folder/name).exists() for name in ['split_metrics.csv', 'sensitivity_summary.csv',
                                                   'shared_period/protocol.json']):
        return evidence, completion
    evidence = evidence.copy()
    timing = evidence.evidence.eq('Comparable measured runtimes')
    evidence.loc[timing, 'status'] = 'new stage measurements available; historical LDA timing unavailable; no end-to-end speed ranking'
    evidence.loc[timing, 'artifact'] = 'Results/robustness/2026-11-25/new_stage_timings.csv'
    ledger_path = folder / 'label_review/team_decisions.csv'
    approved = int(pd.read_csv(ledger_path, keep_default_na=False).decision.eq('approve').sum()) if ledger_path.exists() else 0
    rows = [
        ('Robustness', 'Exploratory 80/20 split', 'computed; prior full-corpus development disclosed', 'split_metrics.csv; split_protocol.json'),
        ('Robustness', 'Shared-period publication sensitivity', 'computed; existing fits restricted to coverage period', 'shared_period/'),
        ('Robustness', 'Seed/publication and hyperparameter sensitivity', 'computed; automatic matches require interpretation', 'sensitivity_summary.csv; principal_theme_sensitivity.csv'),
        ('Human validation', '110-topic label review preparation', f'11 batches ready; {approved}/110 approved in assisted human review; complete labels pending', 'label_review/README.md; label_review/team_decisions.csv'),
        ('Data audit', '30-article manual audit evidence', 'saved judgments blank; original or new human review required', 'final-project/data/corpus_review.csv'),
    ]
    extra = pd.DataFrame(rows, columns=evidence.columns)
    extra['artifact'] = extra.artifact.map(lambda s: 'Results/robustness/2026-11-25/' + s if not s.startswith('final-project/') else s)
    evidence = pd.concat([evidence.loc[~evidence.evidence.isin(extra.evidence)], extra], ignore_index=True)
    done = ['Supply measured LDA runtime context', 'Held-out and shared-period sensitivity',
            'Modern held-out evaluation with rare-stratum policy', 'Modern shared-period publication sensitivity']
    completion = completion.loc[~completion.remaining_task.isin(done)].copy().reset_index(drop=True)
    if not completion.remaining_task.eq('Resolve 30-article audit evidence').any():
        completion.loc[len(completion)] = ['Resolve 30-article audit evidence', 'PR2 claim lacks saved judgments',
            'Team', 'original judgments or new dated human audit', 'Team to confirm']
    return evidence, completion.reset_index(drop=True)


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
