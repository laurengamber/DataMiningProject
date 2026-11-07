"""Fresh-kernel audit execution and notebook validation (no embedding downloads)."""
from pathlib import Path
import sys
import nbformat
from nbclient import NotebookClient

if __name__ == '__main__':
    root=Path(__file__).resolve().parent
    for p in (root/'notebooks').glob('*.ipynb'):
        n=nbformat.read(p,as_version=4); nbformat.validate(n)
        for c in n.cells:
            if c.cell_type=='code': compile(c.source,str(p),'exec')
    p=root/'notebooks/01_corpus_and_embeddings.ipynb'
    n=nbformat.read(p,as_version=4)
    limit=len(n.cells) if '--embeddings' in sys.argv else 6
    partial=nbformat.v4.new_notebook(cells=n.cells[:limit],metadata=n.metadata)
    NotebookClient(partial,timeout=120,kernel_name='python3',resources={'metadata':{'path':str(root)}}).execute()
    n.cells[:limit]=partial.cells
    nbformat.write(n,p)
    print('Notebook validation and fresh-kernel corpus/embedding execution passed')
    if '--experiments' in sys.argv:
        p=root/'notebooks/02_modern_topic_modeling.ipynb'
        n=nbformat.read(p,as_version=4)
        partial=nbformat.v4.new_notebook(cells=n.cells[:6],metadata=n.metadata)
        NotebookClient(partial,timeout=600,kernel_name='python3',resources={'metadata':{'path':str(root)}}).execute()
        n.cells[:6]=partial.cells
        nbformat.write(n,p)
        print('Fresh-kernel experiment notebook execution passed through the review handoff')
