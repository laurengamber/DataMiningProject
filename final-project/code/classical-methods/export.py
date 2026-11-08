"""Write the classical handoff files that the joint comparison notebook reads."""

# TODO: output folder
#   - OUT = Path(__file__).resolve().parents[1]/'modern-methods/Results/classical', which is where
#     notebook 03 looks for Laura's four classical artifacts (see modern-methods/STATUS.md).

# TODO: assignments.csv
#   - Columns: article_id (str), model='lda', run_id, topic_id (int), plus optionally
#     membership_strength = dominant probability, matching the modern assignments.csv.
#   - Exactly one row per article in the shared corpus. Read article_id as str everywhere.

# TODO: mixtures.csv
#   - The full theta matrix: article_id plus one column per topic (topic_0 ... topic_{K-1}).
#     Not required by the validator, but it keeps the mixed-membership information that
#     dominant-topic assignment throws away.

# TODO: terms.csv
#   - topic_id, rank (starting at 1), term, weight: the top_terms() output for the selected model.
#     Use at least the top 10 per topic, since coherence and jaccard_table both use the top 10.

# TODO: topics.csv
#   - topic_id, label, count. Use your hand label if it exists, otherwise a keyword label like
#     the modern '0_tesla_autopilot_musk_teslas'.

# TODO: manifest.json (use shared.corpus.write_json and corpus_hash)
#   - corpus_hash: corpus_hash(df), so the comparison can confirm both pipelines used the same 7,332 articles.
#   - parameters: k, seed, learning_method, max_iter, doc_topic_prior, topic_word_prior,
#     min_df, max_df, custom stopword list.
#   - metrics: perplexity, coherence, keyword_diversity, topic_count.
#   - hardware: platform.platform(); also note CPU/RAM by hand for the paper's compute section.
#   - versions: importlib.metadata.version() for scikit-learn, gensim, numpy, pandas.
#   - stage timings: preprocessing_seconds, representation_seconds, fit_seconds, evaluation_seconds.
#     Record first-run and rerun times separately.

# TODO: validate before handing off
#   - shared.evaluation.validate_classical(OUT, df.article_id) must run without raising.

# TODO (optional): publication breakdowns
#   - shared.evaluation.publication_exports(df, assignments, OUT) writes the publication heat map
#     with the same layout as the modern one, ready to put side by side in the paper.
