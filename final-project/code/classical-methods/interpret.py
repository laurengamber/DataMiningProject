"""Turn the selected LDA model into topic terms, article assignments, and representatives."""

# TODO: imports
#   - numpy, pandas; top_terms from lda.py.

# TODO: document_topics(model, X)
#   - theta = model.transform(X): an articles x K matrix whose rows sum to 1.
#   - dominant topic = theta.argmax(axis=1); dominant probability = theta.max(axis=1).
#   - LDA has no outlier topic, so every article gets a topic_id >= 0. Mention this in the paper,
#     since BERTopic leaves 17% of articles at -1.
#   - Optional: flag articles whose dominant probability is low (e.g. < 0.3) as "mixed". This is
#     a good comparison point with BERTopic's outliers.

# TODO: representatives(df, theta, n=5)
#   - For each topic, take the n articles with the highest theta[:, k]. Keep article_id,
#     publication, title, and the theta value.
#   - These are what you read to write labels. Save them as representatives.csv, like the modern run.

# TODO: labels
#   - Write a short human label per topic in a hand-edited CSV (topic_id, label, evidence_notes)
#     from the top terms and representative articles. Mirror modern-methods/Results/modern/topic_labels.csv.
#   - Don't overwrite hand labels when the script reruns: only create the file if it doesn't exist.
#   - Leakage rule from the experimental design: label topics BEFORE the 100-article human review
#     sample is drawn, and don't look at those articles while labeling.

# TODO: topic sizes
#   - count = number of articles whose dominant topic is k. These must equal the dominant-topic
#     counts exactly, or validate_classical() will raise 'Classical topic counts disagree'.
