"""Boundary tests for the new exploratory follow-up, using temporary fixtures only."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'comparison'))
from robustness import stratified_split, cached, checksum
from robustness_reports import coverage_rule, publication_shares
from report_helpers import followup_checklists


class RobustnessTests(unittest.TestCase):
    def test_split_rare_strata_and_order_independence(self):
        df=pd.DataFrame({'article_id':[str(i) for i in range(15)],
                         'publication':['singleton']+['pair']*2+['large']*12,
                         'date':['2018-06-01']*15})
        split,strata=stratified_split(df)
        again,_=stratified_split(df.sample(frac=1,random_state=9))
        self.assertEqual(split.set_index('article_id').partition.to_dict(),again.set_index('article_id').partition.to_dict())
        self.assertEqual(split.loc[split.publication.eq('singleton'),'partition'].iloc[0],'train')
        self.assertEqual(set(split.loc[split.publication.eq('pair'),'partition']),{'train','heldout'})
        self.assertEqual(len(split),15)
        self.assertTrue(split.article_id.is_unique)
        self.assertTrue((strata.train+strata.heldout==strata.n).all())

    def test_coverage_uses_complete_years_and_separate_outlets(self):
        rows=[]
        for pub in ['Vice','Vice News']:
            for year in range(2016,2020):
                for day in ['01-01','12-31']:
                    rows.append(dict(publication=pub,date=f'{year}-{day}'))
        rows.append(dict(publication='Vice',date='2020-01-01'))
        rule,_,_=coverage_rule(pd.DataFrame(rows),minimum_annual=2)
        self.assertEqual((rule['start'],rule['end']),(2016,2019))
        self.assertEqual(rule['retained_publications'],['Vice','Vice News'])

    def test_outliers_remain_in_publication_denominators(self):
        df=pd.DataFrame(dict(article_id=['a','b','c'],publication=['one']*3))
        a=pd.DataFrame(dict(article_id=['c','b','a'],topic_id=[-1,1,1]))
        counts,shares=publication_shares(df,a)
        self.assertEqual(counts.loc['one'].sum(),3)
        self.assertAlmostEqual(shares.loc['one',1],2/3)
        self.assertAlmostEqual(shares.loc['one',-1],1/3)

    def test_completed_run_rejects_tampering_and_changed_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);p=folder/'assignments.csv';p.write_text('original')
            ident={'corpus_hash':'fixture','kind':'temporary test'}
            (folder/'manifest.json').write_text(json.dumps({'identity':ident,'files':{'assignments.csv':checksum(p)}}))
            self.assertTrue(cached(folder,ident))
            with self.assertRaises(ValueError):cached(folder,{'kind':'changed'})
            p.write_text('modified')
            with self.assertRaises(ValueError):cached(folder,ident)

    def test_partial_run_is_not_silently_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);(folder/'terms.csv').write_text('partial')
            with self.assertRaises(ValueError):cached(folder,{})

    def test_status_refresh_preserves_pending_human_work(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);folder=root/'Results/robustness/2026-11-25'
            for name in ['lda_full_s42','lda_full_s7','lda_full_s21','lda_split_s42','bertopic_full_s42_timing','bertopic_split_s42']:
                path=folder/name;path.mkdir(parents=True)
                (path/'manifest.json').write_text(json.dumps({'identity':{'corpus_hash':'fixture'}}))
            (folder/'shared_period').mkdir()
            for name in ['split_metrics.csv','sensitivity_summary.csv','shared_period/protocol.json']:
                (folder/name).write_text('temporary test fixture')
            evidence=pd.DataFrame([['Evaluation','Independent reviewer results','pending','none']],columns=['manuscript_section','evidence','status','artifact'])
            tasks=['Confirm both label sets','Supply measured LDA runtime context','Complete independent ratings and qualitative outlier review','Interpret cross-model publication patterns','Held-out and shared-period sensitivity']
            completion=pd.DataFrame([[t,'reason','team','output','pending'] for t in tasks],columns=['remaining_task','reason','responsible_member','expected_output','completion_date'])
            updated,remaining=followup_checklists(evidence,completion,root,'fixture')
            self.assertIn('Interpret cross-model publication patterns',set(remaining.remaining_task))
            self.assertIn('Complete independent ratings and qualitative outlier review',set(remaining.remaining_task))
            self.assertEqual(updated.loc[updated.evidence.eq('Independent reviewer results'),'status'].iloc[0],'pending')
            self.assertIn('Resolve 30-article audit evidence',set(remaining.remaining_task))

            # Removing completed naming must not let the audit row overwrite another pending task.
            (folder/'label_review').mkdir()
            pd.DataFrame({'decision':['approve']*110}).to_csv(folder/'label_review/team_decisions.csv',index=False)
            evidence.loc[len(evidence)]=['Interpretation','Topic labels','team confirmed','labels']
            updated,remaining=followup_checklists(evidence,completion,root,'fixture')
            self.assertNotIn('Confirm both label sets',set(remaining.remaining_task))
            self.assertIn('Interpret cross-model publication patterns',set(remaining.remaining_task))
            self.assertIn('Complete independent ratings and qualitative outlier review',set(remaining.remaining_task))
            self.assertIn('Resolve 30-article audit evidence',set(remaining.remaining_task))


if __name__=='__main__':unittest.main()
