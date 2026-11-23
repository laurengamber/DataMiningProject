"""Real synthetic LDA and notebook integration; fixtures never become study results."""
from pathlib import Path
import json
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT.parent)]
import lda as ld
import representation as rep
import interpret as interpretation
import export as artifacts
from shared import evaluation as ev
from shared.corpus import corpus_hash, digest, write_json


class ClassicalPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name)/'Results/classical'
        self.out.mkdir(parents=True)
        words = ['road safety driver traffic sensor crash wheel truck highway engine camera motor',
                 'policy law bill senate regulation state government public rule agency debate vote']
        self.df = pd.DataFrame(dict(article_id=[str(i) for i in range(36)],
            text=[words[i % 2] for i in range(36)], title=[f'Synthetic {i}' for i in range(36)],
            publication=['Synthetic outlet']*36))
        self.reservation = ev.reserve_review_ids(self.df, Path(self.temp.name)/'reservation.json', n=4)
        self.X, self.vocabulary, self.preparation = rep.prepare_representation(self.df, self.out/'cache/representation')
        self.notebook = json.loads((ROOT/'notebooks/02_classical_topic_modeling.ipynb').read_text())
        self.fit_source = ''.join(next(c for c in self.notebook['cells'] if 'model-fit' in c.get('metadata',{}).get('tags',[]))['source'])
        self.ctx = dict(OUT=self.out, df=self.df, X=self.X, vocabulary=self.vocabulary,
                        preparation=self.preparation, reservation=self.reservation,
                        implementation='synthetic-test', execution_rows=[], artifacts=artifacts,
                        ld=ld, ev=ev, np=np, pd=pd, json=json, time=time)
        self.ctx['texts'], self.ctx['dictionary'] = ev.reference_texts(self.df)
        exec(compile(self.fit_source, 'notebook-model-fit', 'exec'), self.ctx)

    def fit(self):
        return self.ctx['fit_configuration'](2)

    def select(self, manifest):
        run_id = manifest['metrics']['run_id']
        write_json(self.out/'selection.json', dict(corpus_hash=corpus_hash(self.df), run_id=run_id,
                   rationale='Synthetic only', selected_by='Test'))
        folder, selected = self.out/'runs'/run_id, self.out/'selected'/run_id
        identity = dict(run_id=run_id, corpus_hash=corpus_hash(self.df), run_identity_hash=digest(manifest['identity']))
        labels = interpretation.labels_table(folder, selected, identity)
        return folder, selected, labels, identity

    def test_real_fit_reload_resume_and_stale_identity(self):
        model, manifest = self.fit()
        folder = self.out/'runs'/manifest['metrics']['run_id']
        theta = np.load(folder/'mixtures.npy')
        self.assertTrue(np.allclose(theta.sum(axis=1), 1))
        assignments, terms, topics = ev.validate_classical(folder, self.df.article_id.tolist())
        self.assertEqual(assignments.topic_id.tolist(), theta.argmax(axis=1).tolist())
        reps = pd.read_csv(folder/'representative_ids.csv',dtype={'article_id':str})
        self.assertFalse(set(reps.article_id) & set(self.reservation['article_ids']))
        with patch.object(ld, 'fit_lda', side_effect=AssertionError('must not refit')):
            reloaded, same = self.fit()
            self.assertEqual(manifest, same)
            self.assertTrue(np.allclose(model.components_, reloaded.components_))
            (folder/'manifest.json').unlink()  # Interrupted after a completed fit.
            resumed, again = self.fit()
            self.assertEqual(again['metrics']['fit_seconds'], manifest['metrics']['fit_seconds'])
        self.ctx['implementation'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'Stale run'):
            self.fit()

    def test_cache_integrity_alignment_and_empty_rows(self):
        artifacts.load_reservation(Path(self.temp.name)/'reservation.json', self.df)
        with self.assertRaisesRegex(ValueError, 'Stale count matrix'):
            rep.load_representation(self.df.iloc[::-1], self.out/'cache/representation')
        with self.assertRaisesRegex(ValueError, 'no remaining terms'):
            rep.validate_matrix(csr_matrix((1, 10)), list('abcdefghij'), ['empty-article'])
        with self.assertRaisesRegex(ValueError, 'normalized'):
            interpretation.validate_mixtures(np.array([[.1,.2]]),1,2)
        path = self.out/'cache/representation/vocabulary.json'
        path.write_text('[]')
        with self.assertRaisesRegex(ValueError, 'changed artifact'):
            rep.load_representation(self.df, self.out/'cache/representation')

    def test_zero_count_topics_representatives_and_publication_denominators(self):
        model, _ = ld.fit_lda(self.X, 3, 42, max_iter=2)
        theta = np.tile([.7,.2,.1], (len(self.df),1))
        terms = ld.top_terms(model, np.asarray(self.vocabulary))
        per_topic = ev.coherence(terms, self.ctx['texts'], self.ctx['dictionary'])
        folder = self.out/'zero-count'
        with patch.object(model, 'transform', return_value=theta):
            artifacts.export_run(model,self.X,self.df,terms,per_topic,folder,'synthetic',self.reservation['article_ids'])
        assignments, _, topics = ev.validate_classical(folder,self.df.article_id.tolist())
        self.assertEqual(topics['count'].tolist(), [36,0,0])
        reps = pd.read_csv(folder/'representative_ids.csv',dtype={'article_id':str})
        self.assertEqual(reps.groupby('topic_id').size().tolist(),[3,3,3])
        self.assertFalse(set(reps.article_id)&set(self.reservation['article_ids']))
        eligible = sorted(set(self.df.article_id)-set(self.reservation['article_ids']))[:3]
        self.assertEqual(reps.query('topic_id == 2').article_id.tolist(),eligible)
        inventory = interpretation.topic_inventory(folder,folder,len(self.df))
        counts, proportions = artifacts.publication_results(self.df,assignments,inventory,folder/'publication')
        self.assertEqual(counts.sum(axis=1).tolist(),[36])
        self.assertEqual(counts.columns.tolist(),[-1,0,1,2])
        self.assertTrue(np.allclose(proportions.sum(axis=1),1))

    def test_labels_handoff_preservation_confirmation_and_comparison_guard(self):
        _, manifest = self.fit()
        folder, selected, labels, identity = self.select(manifest)
        labels.loc[0,'proposed_label'] = 'Team draft'
        labels.to_csv(selected/'topic_labels.csv',index=False)
        again = interpretation.labels_table(folder,selected,identity)
        self.assertEqual(again.loc[0,'proposed_label'],'Team draft')
        preliminary = artifacts.publish_handoff(folder,selected,self.out,self.df,self.reservation)
        self.assertFalse(preliminary['labels_confirmed'])
        self.assertEqual(preliminary['review_reservation_hash'],digest(self.reservation))
        for i in labels.index:
            labels.loc[i,['proposed_label','evidence_notes','confirmed']] = [f'Team topic {i}','Synthetic evidence only',True]
        labels.to_csv(selected/'topic_labels.csv',index=False)
        confirmed = artifacts.publish_handoff(folder,selected,self.out,self.df,self.reservation)
        self.assertTrue(confirmed['labels_confirmed'])
        before = (self.out/'manifest.json').read_bytes()
        self.assertEqual(artifacts.publish_handoff(folder,selected,self.out,self.df,self.reservation),confirmed)
        self.assertEqual(before,(self.out/'manifest.json').read_bytes())
        ev.validate_classical(self.out,self.df.article_id.tolist())
        mixture = pd.read_csv(self.out/'mixtures.csv',dtype={'article_id':str})
        self.assertEqual(mixture.article_id.tolist(),self.df.article_id.tolist())
        comparison = self.out.parent/'comparison/modern-test'
        write_json(comparison/'comparison_identity.json',{'existing':'comparison'})
        labels.loc[0,'proposed_label']='Changed label'
        labels.to_csv(selected/'topic_labels.csv',index=False)
        with self.assertRaisesRegex(ValueError,'archive the active comparison'):
            artifacts.publish_handoff(folder,selected,self.out,self.df,self.reservation)
        self.assertEqual(before,(self.out/'manifest.json').read_bytes())
        labels.loc[0,'evidence_ids']=self.reservation['article_ids'][0]
        labels.to_csv(selected/'topic_labels.csv',index=False)
        with self.assertRaisesRegex(ValueError,'nonreserved'):
            interpretation.labels_table(folder,selected,identity)

    def test_pending_and_completed_notebook_paths(self):
        import matplotlib.pyplot as plt
        from IPython.display import Image
        nb=json.loads((ROOT/'notebooks/03_classical_results_and_exports.ipynb').read_text())
        cells={tag:''.join(c['source']) for c in nb['cells'] for tag in c.get('metadata',{}).get('tags',[])}
        ctx=dict(self.ctx, interpretation=interpretation, display=lambda *args:None,
                 write_json=write_json, corpus_hash=corpus_hash,digest=digest,Image=Image,
                 complete_runs=[],selection=None,plt=plt)
        for tag in ['publication','handoff','readiness']:
            exec(cells[tag],ctx)
        self.assertFalse((self.out/'assignments.csv').exists())
        self.assertFalse(json.loads((self.out/'status.json').read_text())['handoff_ready'])
        _, manifest = self.fit()
        folder,selected,labels,identity=self.select(manifest)
        selection=dict(corpus_hash=corpus_hash(self.df),run_id=manifest['metrics']['run_id'],rationale='Synthetic only',selected_by='Test')
        write_json(self.out/'selection.json',selection)
        ctx.update(complete_runs=[selection['run_id']],selection=selection)
        for tag in ['publication','handoff','readiness']:
            exec(cells[tag],ctx)
        self.assertTrue(json.loads((self.out/'status.json').read_text())['handoff_ready'])
        self.ctx.update(selection=selection,experiments=pd.DataFrame([manifest['metrics']]),
                        write_json=write_json,corpus_hash=corpus_hash,digest=digest,
                        interpretation=interpretation,display=lambda *args:None)
        selected_source=''.join(next(c for c in self.notebook['cells'] if 'selected' in c.get('metadata',{}).get('tags',[]))['source'])
        exec(selected_source,self.ctx)
        stability=pd.read_csv(selected/'stability.csv')
        self.assertEqual(stability.seed.tolist(),[7,21])
        self.assertTrue(stability.evaluated_fraction.eq(1).all())
        for seed in [7,21]:
            self.assertTrue((selected/f'seed_{seed}/publication_changes.csv').exists())
        handoff = artifacts.publish_handoff(folder, selected, self.out, self.df, self.reservation)
        self.assertEqual(handoff['files']['stability.csv'], artifacts.file_hash(selected/'stability.csv'))
        self.assertEqual(pd.read_csv(self.out/'stability.csv').seed.tolist(), [7,21])

    def test_selection_requires_team_and_valid_completed_run(self):
        self.assertIsNone(artifacts.selection_record(self.out,self.df,[]))
        write_json(self.out/'selection.json',dict(corpus_hash=corpus_hash(self.df),run_id='lda_k40_s42',rationale='',selected_by=''))
        with self.assertRaisesRegex(ValueError,'completed seed-42'):
            artifacts.selection_record(self.out,self.df,[])
        write_json(self.out/'selection.json',dict(corpus_hash=corpus_hash(self.df),run_id='',rationale='',selected_by=''))
        write_json(self.out/'manifest.json',{'old':'handoff'})
        with self.assertRaisesRegex(ValueError,'published handoff exists'):
            artifacts.selection_record(self.out,self.df,[])

    def test_real_exports_feed_joint_comparison_and_frozen_review(self):
        import importlib.util
        import shutil
        modern_root = ROOT.parent/'modern-methods'
        sys.path.insert(0, str(modern_root))
        spec = importlib.util.spec_from_file_location('comparison_fixture', modern_root/'tests/test_comparison_notebook.py')
        fixture_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixture_module)
        case = fixture_module.ComparisonNotebookTests()
        case.setUp()
        self.addCleanup(case.doCleanups)
        X, vocabulary, preparation = rep.prepare_representation(case.df, case.lda/'cache/representation')
        ctx = dict(self.ctx, OUT=case.lda, df=case.df, X=X, vocabulary=vocabulary,
                   preparation=preparation, reservation=case.reservation, execution_rows=[])
        ctx['texts'], ctx['dictionary'] = ev.reference_texts(case.df)
        exec(self.fit_source,ctx)
        _, manifest = ctx['fit_configuration'](2)
        run_id=manifest['metrics']['run_id']
        folder,selected=case.lda/'runs'/run_id,case.lda/'selected'/run_id
        write_json(case.lda/'selection.json',dict(corpus_hash=corpus_hash(case.df),run_id=run_id,
                   rationale='Synthetic only',selected_by='Test'))
        identity=dict(run_id=run_id,corpus_hash=corpus_hash(case.df),run_identity_hash=digest(manifest['identity']))
        labels=interpretation.labels_table(folder,selected,identity)
        baseline=pd.read_csv(folder/'assignments.csv',dtype={'article_id':str})
        stability_rows=[]
        for seed in [7,21]:
            _, other_manifest=ctx['fit_configuration'](2,seed)
            other=pd.read_csv(case.lda/'runs'/other_manifest['metrics']['run_id']/'assignments.csv',dtype={'article_id':str})
            stability_rows.append(dict(seed=seed,**ev.stability(baseline.topic_id,other.topic_id)))
        pd.DataFrame(stability_rows).to_csv(selected/'stability.csv',index=False)
        artifacts.publish_handoff(folder,selected,case.lda,case.df,case.reservation)
        case.load_models()
        for tag in ['metrics','overlap','publications','runtime','review-packet','human-summary','evidence']:
            case.run_cell(tag)
        self.assertIsNone(case.ctx['review_folder'])
        self.assertIsNotNone(case.ctx['comparison_metrics'])
        # Preserve the provisional comparison before publishing confirmed labels.
        active=case.ctx['COMPARISON']
        archive=active.parent/'archive/provisional'
        archive.parent.mkdir()
        shutil.move(str(active),str(archive))
        labels['proposed_label']=['Synthetic roads','Synthetic policy']
        labels['evidence_notes']='Synthetic development evidence'
        labels['confirmed']=True
        labels.to_csv(selected/'topic_labels.csv',index=False)
        artifacts.publish_handoff(folder,selected,case.lda,case.df,case.reservation)
        case.load_models()
        for tag in ['metrics','overlap','publications','runtime','review-packet','human-summary','evidence']:
            case.run_cell(tag)
        review=case.ctx['review_folder']
        self.assertIsNotNone(review)
        before={p:p.read_bytes() for p in review.glob('reviewer_*.csv')}
        artifacts.publish_handoff(folder,selected,case.lda,case.df,case.reservation)
        case.run_cell('review-packet')
        for path,contents in before.items():
            self.assertEqual(path.read_bytes(),contents)
        self.assertTrue(case.ctx['pipeline_comparison'].mean_1.isna().all())
        with (case.lda/'terms.csv').open('a') as stream:
            stream.write('\n')
        with self.assertRaisesRegex(ValueError,'Classical export changed'):
            case.run_cell('classical-input')

if __name__ == '__main__':
    unittest.main()
