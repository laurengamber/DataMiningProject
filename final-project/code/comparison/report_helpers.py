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
    naming_status = (f'{approved}/110 approved in assisted human review; naming decisions complete'
                     if approved == 110 else
                     f'11 batches ready; {approved}/110 approved in assisted human review; complete labels pending')
    audit_status = 'saved judgments blank; original or new human review required'
    audit_path = folder / 'audit_review/2026-11-25/human_judgments.csv'
    if audit_path.exists():
        audit = pd.read_csv(audit_path, keep_default_na=False)
        complete = audit[['reviewer_name', 'review_date', 'relevance', 'boilerplate', 'malformed']].ne('').all(axis=1).sum()
        audit_status = f'original judgments unavailable; new dated audit {complete}/{len(audit)} submitted; historical claim unsupported'
    rows = [
        ('Robustness', 'Exploratory 80/20 split', 'computed; prior full-corpus development disclosed', 'split_metrics.csv; split_protocol.json'),
        ('Robustness', 'Shared-period publication sensitivity', 'computed; existing fits restricted to coverage period', 'shared_period/'),
        ('Robustness', 'Seed/publication and hyperparameter sensitivity', 'computed; automatic matches require interpretation', 'sensitivity_summary.csv; principal_theme_sensitivity.csv'),
        ('Human validation', '110-topic label review preparation', naming_status, 'label_review/README.md; label_review/team_decisions.csv'),
        ('Data audit', '30-article manual audit evidence', audit_status, 'final-project/data/corpus_review.csv'),
    ]
    extra = pd.DataFrame(rows, columns=evidence.columns)
    extra['artifact'] = extra.artifact.map(lambda s: 'Results/robustness/2026-11-25/' + s if not s.startswith('final-project/') else s)
    evidence = pd.concat([evidence.loc[~evidence.evidence.isin(extra.evidence)], extra], ignore_index=True)
    done = ['Supply measured LDA runtime context', 'Held-out and shared-period sensitivity',
            'Modern held-out evaluation with rare-stratum policy', 'Modern shared-period publication sensitivity']
    completion = completion.loc[~completion.remaining_task.isin(done)].copy().reset_index(drop=True)
    # The notebook's authoritative input checks, not ledger count alone, establish readiness.
    labels_ready = evidence.loc[evidence.evidence.eq('Topic labels'), 'status'].eq('team confirmed').any()
    if labels_ready and approved == 110:
        completion = completion.loc[~completion.remaining_task.eq('Confirm both label sets')].copy().reset_index(drop=True)
        mask = evidence.evidence.eq('Topic labels')
        evidence.loc[mask, 'status'] = 'confirmed by Mary Kate during assisted naming; reservation attested'
        evidence.loc[mask, 'artifact'] = 'label_review/team_decisions.csv; label_review/reservation_attestation_2026-11-25.json; authoritative model label tables'
    modern_labels_ready = evidence.loc[evidence.evidence.eq('Topic labels and article support'), 'status'].eq('complete').any()
    if modern_labels_ready and approved == 110:
        completion = completion.loc[~completion.remaining_task.eq('Confirm modern topic labels')].copy().reset_index(drop=True)
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
