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

### Final-project analysis

Our project code is in [final-project/code](final-project/code/README.md).
We compare LDA and BERTopic on the same 7,332 articles after removing duplicates.
The source data are in `data/self_driving_articles.csv`.

Start with the [modern notebooks](final-project/code/modern-methods/notebooks/README.md)
for article embeddings, six BERTopic settings, and publication results. Notebook 01 reserves
100 articles for human review before we choose topic names. Run the [classical notebooks](final-project/code/classical-methods/README.md) for the LDA grid and exports.
After choosing both models, use the [comparison notebook](final-project/code/comparison/README.md)
to compare the methods.

Once both sets of labels are final, the [reviewer notebooks](final-project/code/human-review/README.md)
guide the independent ratings. Missing inputs show as pending. The notebooks save tables and
figures for PR3; we write the report separately.
