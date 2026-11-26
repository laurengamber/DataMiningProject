"""Boundary tests for the new exploratory follow-up, using temporary fixtures only."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'comparison'))
from robustness import stratified_split, cached, checksum
from robustness_reports import coverage_rule, publication_shares


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


if __name__=='__main__':unittest.main()
