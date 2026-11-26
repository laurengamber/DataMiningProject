"""Artifacts for the separate 100-iteration notebook exploration; the selected CLI pipeline uses export.py."""

from pathlib import Path
import hashlib
import importlib.metadata as metadata
import json
import os
import pickle
import platform
import shutil
import sys
import tempfile
import numpy as np
import pandas as pd
from shared.corpus import corpus_hash, digest, write_json
from shared.evaluation import validate_classical
from notebook_interpret import document_topics, representatives, validate_mixtures, labels_table


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def environment():
    return dict(platform=platform.platform(), machine=platform.machine(), processor=platform.processor(),
                logical_cpu_count=os.cpu_count(),
                python=sys.version, versions={name: metadata.version(name)
                for name in ['scikit-learn', 'gensim', 'numpy', 'pandas', 'scipy']})


def verify_files(folder, files):
    for name, checksum in files.items():
        path = Path(folder)/name
        if not path.is_file() or file_hash(path) != checksum:
            raise ValueError(f'Missing or changed artifact: {path}')


def load_reservation(path, df):
    path = Path(path)
    if not path.exists():
        raise ValueError('Run modern notebook 01 first to reserve the shared human-review sample')
    record = json.loads(path.read_text())
    ids = record['article_ids']
    eligible = record['eligible_article_ids']
    excluded = record['excluded_article_ids']
    if (record['corpus_hash'] != corpus_hash(df) or len(ids) != record['sample_size']
            or len(set(ids)) != len(ids) or not set(ids).issubset(eligible)
            or set(ids) & set(excluded) or set(eligible) & set(excluded)
            or set(eligible) | set(excluded) != set(df.article_id)):
        raise ValueError('Review reservation does not match the corpus or eligibility rules')
    expected = pd.Series(eligible).sample(record['sample_size'], random_state=record['seed']).tolist()
    if ids != expected:
        raise ValueError('Review reservation IDs do not match the saved sampling settings')
    return record


def implementation_hash(root, notebook):
    notebook = json.loads(Path(notebook).read_text())
    fit_source = ''.join(''.join(c['source']) for c in notebook['cells']
                         if 'model-fit' in c.get('metadata', {}).get('tags', []))
    return digest([fit_source] + [(Path(root)/p).read_text() for p in
                  ['lda.py', 'interpret.py', 'notebook_interpret.py', 'notebook_artifacts.py', 'preprocessing.py', 'representation.py',
                   '../shared/corpus.py', '../shared/evaluation.py']])


def run_identity(df, preparation, parameters, implementation, reservation):
    return dict(corpus_hash=corpus_hash(df), article_ids_hash=digest(df.article_id.tolist()),
                representation_hash=digest(preparation), parameters=parameters,
                implementation_hash=implementation, review_reservation_hash=digest(reservation),
                versions=environment()['versions'])


def save_checkpoint(folder, model, identity, fit_seconds):
    """Save a completed fit before scoring; interrupted scoring can resume."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    temporary = folder/'model.pkl.tmp'
    with temporary.open('wb') as stream:
        pickle.dump(model, stream)
    temporary.replace(folder/'model.pkl')
    write_json(folder/'fit_checkpoint.json', dict(identity=identity, fit_seconds=fit_seconds,
               environment=environment(), files={'model.pkl': file_hash(folder/'model.pkl')}))


def load_checkpoint(folder, identity):
    folder = Path(folder)
    path = folder/'fit_checkpoint.json'
    if not path.exists():
        return None
    checkpoint = json.loads(path.read_text())
    if checkpoint['identity'] != identity:
        raise ValueError(f'Stale fit at {folder}; preserve it separately before refitting')
    verify_files(folder, checkpoint['files'])
    with (folder/'model.pkl').open('rb') as stream:
        model = pickle.load(stream)  # Trusted, locally generated project artifacts only.
    return model, checkpoint['fit_seconds']


def export_run(model, X, df, terms, per_topic, folder, run_id, reserved_ids):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    theta, dominant = document_topics(model, X)
    assignments = pd.DataFrame(dict(article_id=df.article_id, model='lda', run_id=run_id,
                                    topic_id=dominant, membership_strength=theta.max(axis=1)))
    counts = pd.Series(dominant).value_counts().reindex(range(model.n_components), fill_value=0)
    keywords = terms.sort_values('rank').groupby('topic_id').term.agg(lambda s: '_'.join(s.head(4)))
    topics = pd.DataFrame(dict(topic_id=range(model.n_components), count=counts.to_numpy()))
    topics['label'] = topics.topic_id.astype(str) + '_' + topics.topic_id.map(keywords)
    assignments.to_csv(folder/'assignments.csv', index=False)
    terms.to_csv(folder/'terms.csv', index=False)
    topics.to_csv(folder/'topics.csv', index=False)
    per_topic.to_csv(folder/'coherence.csv', index=False)
    np.save(folder/'mixtures.npy', theta, allow_pickle=False)
    reps = representatives(df, theta, reserved_ids)
    reps.to_csv(folder/'representatives.csv', index=False)
    reps.drop(columns='text').to_csv(folder/'representative_ids.csv', index=False)
    validate_classical(folder, df.article_id.tolist())
    return theta


def save_run_manifest(folder, identity, metrics, timings):
    folder = Path(folder)
    names = ['model.pkl', 'assignments.csv', 'terms.csv', 'topics.csv', 'coherence.csv',
             'representative_ids.csv', 'representatives.csv', 'mixtures.npy']
    checkpoint = json.loads((folder/'fit_checkpoint.json').read_text())
    write_json(folder/'manifest.json', dict(identity=identity, corpus_hash=identity['corpus_hash'],
               parameters=identity['parameters'], metrics=metrics, timings=timings,
               environment=checkpoint['environment'],
               files={name: file_hash(folder/name) for name in names}))


def load_run(folder, expected=None, load_model=True):
    folder = Path(folder)
    manifest = json.loads((folder/'manifest.json').read_text())
    if expected is not None and manifest['identity'] != expected:
        raise ValueError(f'Stale run at {folder}; preserve it separately before refitting')
    verify_files(folder, manifest['files'])
    model = None
    if load_model:
        with (folder/'model.pkl').open('rb') as stream:
            model = pickle.load(stream)
    return model, manifest


def selection_record(out, df, runs):
    path = Path(out)/'selection.json'
    if not path.exists():
        write_json(path, dict(corpus_hash=corpus_hash(df), run_id='', rationale='', selected_by=''))
    record = json.loads(path.read_text())
    if record.get('corpus_hash') != corpus_hash(df):
        raise ValueError('Selection belongs to a different corpus')
    if not str(record.get('run_id', '')).strip():
        if (Path(out)/'manifest.json').exists():
            raise ValueError('Selection is blank but a published handoff exists; preserve the old handoff separately')
        return None
    if record['run_id'] not in runs or any(not str(record.get(k, '')).strip()
                                           for k in ['rationale', 'selected_by']):
        raise ValueError('Choose a completed seed-42 run and supply a rationale and team selector')
    return record


def publish_handoff(folder, selected, out, df, reservation):
    """Validate a staged handoff; changed exports cannot overwrite an existing comparison."""
    folder, selected, out = Path(folder), Path(selected), Path(out)
    _, manifest = load_run(folder, load_model=False)
    if (manifest['corpus_hash'] != corpus_hash(df)
            or manifest['identity']['review_reservation_hash'] != digest(reservation)):
        raise ValueError('Selected run differs from the current corpus or review reservation')
    selection = selection_record(out, df, [manifest['metrics']['run_id']])
    if selection is None:
        raise ValueError('Record the team selection before publishing a handoff')
    identity = dict(run_id=manifest['metrics']['run_id'], corpus_hash=corpus_hash(df),
                    run_identity_hash=digest(manifest['identity']))
    labels = labels_table(folder, selected, identity)
    topics = pd.read_csv(folder/'topics.csv')
    confirmed = labels.loc[labels.confirmed.astype(str).str.lower().eq('true')].set_index('topic_id')
    mask = topics.topic_id.isin(confirmed.index)
    topics.loc[mask, 'label'] = topics.loc[mask, 'topic_id'].map(confirmed.proposed_label)
    theta = np.load(folder/'mixtures.npy', allow_pickle=False)
    validate_mixtures(theta, len(df), len(topics))
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out, prefix='.handoff-') as temp:
        stage = Path(temp)
        for name in ['assignments.csv', 'terms.csv']:
            shutil.copyfile(folder/name, stage/name)
        topics.to_csv(stage/'topics.csv', index=False)
        mixtures = pd.DataFrame(theta, columns=[f'topic_{i}' for i in range(theta.shape[1])])
        mixtures.insert(0, 'article_id', df.article_id.to_numpy())
        mixtures.to_csv(stage/'mixtures.csv', index=False)
        files = {name: file_hash(stage/name) for name in ['assignments.csv', 'terms.csv', 'topics.csv', 'mixtures.csv']}
        if (selected/'stability.csv').exists():
            shutil.copyfile(selected/'stability.csv', stage/'stability.csv')
            files['stability.csv'] = file_hash(stage/'stability.csv')
        handoff = dict(corpus_hash=corpus_hash(df), run_id=identity['run_id'], identity=manifest['identity'],
                       selection=selection,
                       parameters=manifest['parameters'], metrics=manifest['metrics'],
                       timings=manifest['timings'], environment=manifest['environment'], files=files,
                       labels_confirmed=len(confirmed) == len(topics), review_reservation_hash=digest(reservation),
                       timing_note='Original measured stages; cache loads are recorded separately in execution.json.')
        write_json(stage/'manifest.json', handoff)
        validate_classical(stage, df.article_id.tolist())
        names = [*files, 'manifest.json']
        changed = any(not (out/name).exists() or file_hash(out/name) != file_hash(stage/name) for name in names)
        comparisons = out.parent/'comparison'
        # Only active comparisons bind these exports; explicitly archived copies remain immutable.
        if changed and comparisons.exists() and any(comparisons.glob('*/comparison_identity.json')):
            raise ValueError('Classical exports changed: archive the active comparison folder before publishing. '
                             'Never replace a frozen review or its answers; finish that review or start a separately identified study.')
        if changed:
            for name in names:  # Manifest is replaced last, after all validated data files.
                (stage/name).replace(out/name)
    return handoff


def publication_results(df, assignments, inventory, out):
    """Use shared plots/denominators and retain zero-count topics in complete CSVs."""
    from shared.evaluation import publication_exports
    counts, proportions = publication_exports(df, assignments, out, dict(zip(inventory.topic_id, inventory.label)))
    columns = sorted(set(inventory.topic_id) | {-1})
    counts = counts.reindex(columns=columns, fill_value=0)
    proportions = counts.div(counts.sum(axis=1), axis=0)
    counts.to_csv(Path(out)/'publication_counts.csv')
    proportions.to_csv(Path(out)/'publication_proportions.csv')
    return counts, proportions
