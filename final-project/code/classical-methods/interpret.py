"""Turn the selected LDA model into topic terms, article assignments, and representatives."""
import numpy
import pandas 

from lda import top_terms

def document_topics(model, X):
    """Return theta (articles x K, rows sum to 1) and each article's dominant topic."""
    theta = model.transform(X)
    assignments = pandas.DataFrame({
        'topic_id': theta.argmax(axis=1),
        'membership_strength': theta.max(axis=1),
    })
    return theta, assignments


def representatives(df, theta, n=5):
    """The n articles with the highest probability for each topic, to read when labeling."""
    rows = []
    for topic_id in range(theta.shape[1]):
        for rank, i in enumerate(theta[:, topic_id].argsort()[::-1][:n], 1):
            rows.append(dict(topic_id=topic_id, rank=rank, article_id=str(df.article_id.iloc[i]),
                             publication=df.publication.iloc[i], title=df.title.iloc[i],
                             theta=float(theta[i, topic_id])))
    return pandas.DataFrame(rows)