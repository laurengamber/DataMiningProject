## 10/5 Meeting

### Final Lecture
- Lauren will do Foundations and Classical Preprocessing
- Mary Cate will do Classical Modeling and Modern Methods
- Laura will do LDA Deep Dive
- Lauren and Laura will create an interactive R Shiny app activity

### Final Project 
- Laura will do a classical pipeline for text mining hidden themes in Python
- Mary Kate will do a modern pipeline for text mining hidden themes in Python
- Lauren will do theory writing and data visualization in R.



### Python notebook setup

Install [uv](https://docs.astral.sh/uv/) if needed, then run:

```sh
uv sync
uv run jupyter lab
```

Open `Chapter 5 - Text Clustering and Topic Modeling.ipynb` in JupyterLab. The
environment is created in `.venv`; select its Python kernel if Jupyter asks.
The notebook downloads a Hugging Face dataset and models when run. Its OpenAI
example also requires an API key. The R Markdown file uses R packages
`tidyverse` and `lubridate`, which are managed separately from this Python
environment.
Lecture Proposal: 

### Modern project workflow

The [modern-methods notebooks](final-project/code/modern-methods/notebooks/README.md)
cover corpus/embeddings, a six-configuration BERTopic study, publication/evaluation outputs,
and separate [human-review notebooks](final-project/code/human-review/README.md) with commented
rating-entry cells for reviewer 1 and reviewer 2.
Run them in order. The source dataset is `data/self_driving_articles.csv`; both pipelines use
the shared deduplicated 7,332-article corpus. Notebook 01 reserves human-evaluation IDs before
development review. Choose a run with a written rationale, confirm topic labels, and provide
Laura's exports to enable the joint comparison. Missing team inputs are explicitly pending.
The notebooks generate PR3 evidence without editing the manuscript.
