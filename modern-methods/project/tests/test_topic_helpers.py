import unittest, tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from src import topic_helpers as h

class Tokenizer:
    def encode(self,text,add_special_tokens=False): return list(range(int(text)))
    def num_special_tokens_to_add(self,pair=False): return 2

class Tests(unittest.TestCase):
    def test_chunk_boundaries(self):
        for n in [1,480,481,960,961]:
            chunks=h.token_chunks(str(n),Tokenizer())
            self.assertEqual(sum(map(len,chunks)),n)
            self.assertEqual(sum(chunks,[]),list(range(n)))
        with self.assertRaises(ValueError): h.token_chunks('0',Tokenizer())
    def test_silhouette_undefined(self):
        for labels in [[-1,-1],[0,0],[0,1]]:
            score,reason=h.silhouette(np.eye(2),labels,'cosine')
            self.assertTrue(np.isnan(score)); self.assertIn('Undefined',reason)
    def test_jaccard(self):
        a=pd.DataFrame({'topic_id':[0,0,-1],'rank':[1,2,1],'term':['a','b','noise']})
        b=pd.DataFrame({'topic_id':[2,2],'rank':[1,2],'term':['b','c']})
        self.assertAlmostEqual(h.jaccard_table(a,b).loc[0,2],1/3)
    def test_cache_validation(self):
        with self.assertRaises(ValueError): h.validate_embeddings(np.zeros((2,384)),2)
        self.assertNotEqual(h.digest(['a','b']),h.digest(['b','a']))
        h.validate_embeddings(np.tile(np.ones(384)/np.sqrt(384),(2,1)),2)
    def test_classical_alignment(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)
            pd.DataFrame({'article_id':['b','a'],'model':['lda']*2,'run_id':['r']*2,'topic_id':[0,1]}).to_csv(p/'assignments.csv',index=False)
            pd.DataFrame({'topic_id':[0,1],'rank':[1,1],'term':['car','law'],'weight':[.1,.2]}).to_csv(p/'terms.csv',index=False)
            pd.DataFrame({'topic_id':[0,1],'label':['car','law'],'count':[1,1]}).to_csv(p/'topics.csv',index=False)
            a,_,_=h.validate_classical(p,['a','b']); self.assertEqual(a.topic_id.tolist(),[1,0])
            with self.assertRaises(ValueError): h.validate_classical(p,['a','c'])

if __name__=='__main__': unittest.main()

class CacheAndReviewTests(unittest.TestCase):
    def test_cache_rejects_reordered_corpus(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); out=root/'output/modern'; out.mkdir(parents=True)
            df=pd.DataFrame({'article_id':['a','b'],'text':['car','law']})
            df.to_csv(out/'corpus.csv',index=False)
            h.write_json(out/'embedding_pointer.json',{'folder':'cache','manifest':{'article_ids':['b','a'],'text_hash':h.digest(df.text.tolist())}})
            with self.assertRaises(ValueError): h.load_inputs(root)
    def test_review_freeze_rejects_label_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            df=pd.DataFrame({'article_id':['a'],'text':['car road'],'title':['Car']})
            a=pd.DataFrame({'article_id':['a'],'model':['bertopic'],'run_id':['r'],'topic_id':[0]})
            h.review_packets(df,a,None,temp,{('bertopic',0):'Safety'})
            with self.assertRaises(ValueError): h.review_packets(df,a,None,temp,{('bertopic',0):'Law'})
