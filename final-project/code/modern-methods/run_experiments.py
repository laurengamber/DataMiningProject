"""Run the bounded six-configuration study, stopping before human selection."""
from pathlib import Path
from src.topic_helpers import load_inputs, cached_run, shortlist

if __name__ == '__main__':
    root=Path(__file__).resolve().parent
    df,embeddings=load_inputs(root)
    for neighbors in [15,30]:
        for size in [25,50,100]:
            _,metrics=cached_run(df,embeddings,root,neighbors,size)
            print(metrics,flush=True)
    _,finalists=shortlist(root)
    print(finalists.to_string(index=False))
    print('Complete selection_review/selection_review.csv, then resume notebook 02.')
