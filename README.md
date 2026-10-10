## 10/5 Meeting

### Final Lecture
- Lauren will do Foundations and Classical Preprocessing
- Mary Cate will do Classical Modeling and Modern Methods
- Laura will do LDA Deep Dive
- Lauren and Laura will create an interactive R Shiny app activity

### Final Project 
- Laura will do a classical pipeline for text mining hidden themes in Python
- Mary Cate will do a modern pipeline for text mining hidden themes in Python
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

Mary Kate’s implementation is in three numbered [project notebooks](modern-methods/project/notebooks/README.md): corpus and full-text embeddings, BERTopic experiments, and modern/classical evaluation. Run them in order; model selection, topic naming, and two-person evaluation use explicit human review files. Laura’s classical export contract and project milestones are documented there.
