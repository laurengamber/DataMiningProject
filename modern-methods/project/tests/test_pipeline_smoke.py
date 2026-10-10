"""Small real BERTopic integration check; synthetic data are never project results."""
import tempfile, unittest
from pathlib import Path
import numpy as np
import pandas as pd
from src.topic_helpers import fit_run

class PipelineSmoke(unittest.TestCase):
    def test_real_pipeline_and_exports(self):
        rng=np.random.default_rng(42); x=rng.normal(size=(80,384))
        x[:40,:10]+=5; x[40:,10:20]+=5; x/=np.linalg.norm(x,axis=1)[:,None]
        texts=['vehicle road autonomous safety crash café crash-report' if i<40 else 'policy regulation senate bill testing' for i in range(80)]
        df=pd.DataFrame({'article_id':list(map(str,range(80))),'text':texts,'title':['Synthetic']*80})
        with tempfile.TemporaryDirectory() as temp:
            model,metrics=fit_run(df,x,Path(temp),15,10)
            self.assertGreaterEqual(metrics['topic_count'],2)
            self.assertEqual(model.topic_embeddings_.shape[1],384)
            exported=pd.read_csv(Path(temp)/'Results/modern/runs/n15_c10_s42/assignments.csv')
            self.assertEqual(len(exported),80)
            self.assertEqual(exported.topic_id.tolist(),model.topics_)
