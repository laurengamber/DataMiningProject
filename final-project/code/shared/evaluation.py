"""Shared evaluation vocabulary, metrics, and joint comparison; imports are lazy."""
from pathlib import Path
import json, re
import numpy as np
import pandas as pd
from .corpus import SEED, write_json, digest

def representation_text(text):
    # Match BERTopic's English keyword preprocessing before fitting a fixed vocabulary.
    return re.sub(r'[^A-Za-z0-9 ]+', '', text.replace('\n',' ').replace('\t',' ')) or 'emptydoc'

def analyzer():
    # Lowercase word tokens without English stopwords; shared by coherence and classical preprocessing.
    from sklearn.feature_extraction.text import CountVectorizer
    return CountVectorizer(stop_words='english').build_analyzer()

def reference_texts(df):
    from gensim.corpora import Dictionary
    tokenizer=analyzer()
    texts=[tokenizer(representation_text(t)) for t in df.text]; return texts,Dictionary(texts)

def coherence(terms,texts,dictionary):
    from gensim.models import CoherenceModel
    groups=[]
    for t,g in terms[terms.topic_id.ge(0)].groupby('topic_id'):
        words=g.sort_values('rank').term.head(10).tolist()
        known=[w for w in words if w in dictionary.token2id]
        groups.append((t,known,len(known)/len(words) if words else 0))
    valid=[g for g in groups if len(g[1])>=2]
    values=CoherenceModel(topics=[g[1] for g in valid],texts=texts,dictionary=dictionary,coherence='c_v',processes=1).get_coherence_per_topic() if valid else []
    scores={g[0]:float(v) for g,v in zip(valid,values)}
    return pd.DataFrame([dict(topic_id=t,coherence=scores.get(t,np.nan),vocabulary_coverage=coverage) for t,words,coverage in groups],columns=['topic_id','coherence','vocabulary_coverage'])

def stability(a,b):
    from sklearn.metrics import adjusted_rand_score
    a=np.array(a); b=np.array(b); mask=(a>=0)&(b>=0)
    return dict(adjusted_rand_index=float(adjusted_rand_score(a[mask],b[mask])) if mask.sum()>1 else np.nan,evaluated_fraction=float(mask.mean()),outlier_agreement=float(np.mean((a==-1)==(b==-1))))

def jaccard_table(a,b):
    def sets(df): return {t:set(g.sort_values('rank').term.head(10)) for t,g in df[df.topic_id.ge(0)].groupby('topic_id')}
    aa,bb=sets(a),sets(b)
    return pd.DataFrame({j:{i:len(x&y)/len(x|y) if x|y else 0 for i,x in aa.items()} for j,y in bb.items()})

def validate_classical(folder,ids):
    folder=Path(folder); a=pd.read_csv(folder/'assignments.csv',dtype={'article_id':str}); terms=pd.read_csv(folder/'terms.csv'); topics=pd.read_csv(folder/'topics.csv')
    required={'article_id','model','run_id','topic_id'}
    if not required.issubset(a.columns) or not a.article_id.is_unique or set(a.article_id)!=set(ids): raise ValueError('Classical assignments must contain exactly one row per shared article')
    if not {'topic_id','rank','term','weight'}.issubset(terms.columns) or not {'topic_id','label','count'}.issubset(topics.columns): raise ValueError('Invalid classical terms/topics schema')
    if a.topic_id.isna().any() or terms[['topic_id','rank','term']].isna().any().any(): raise ValueError('Missing topic IDs or terms')
    if not set(a.topic_id).issubset(set(topics.topic_id)): raise ValueError('Unknown classical topic')
    actual=a.topic_id.value_counts().sort_index()
    declared=topics.set_index('topic_id')['count'].sort_index()
    if not actual.equals(declared.reindex(actual.index)): raise ValueError('Classical topic counts disagree')
    for frame in [a,terms,topics]:
        values=pd.to_numeric(frame.topic_id,errors='raise')
        if not values.mod(1).eq(0).all(): raise ValueError('Topic IDs must be integers')
        frame['topic_id']=values.astype(int)
    if not pd.to_numeric(terms['rank'],errors='raise').gt(0).all(): raise ValueError('Term ranks must be positive')
    if terms.duplicated(['topic_id','rank']).any(): raise ValueError('Duplicate term ranks')
    return a.set_index('article_id').loc[list(ids)].reset_index(),terms,topics

def publication_exports(df,assignments,out):
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    joined=df[['article_id','publication']].merge(assignments,on='article_id',validate='one_to_one')
    counts=pd.crosstab(joined.publication,joined.topic_id); counts[-1]=counts.get(-1,0)
    counts.to_csv(out/'publication_counts.csv'); proportions=counts.div(counts.sum(axis=1),axis=0); proportions.to_csv(out/'publication_proportions.csv')
    import matplotlib.pyplot as plt
    main=proportions.loc[counts.sum(axis=1)>=50]; fig,ax=plt.subplots(figsize=(12,7)); im=ax.imshow(main,aspect='auto'); ax.set_yticks(range(len(main)),main.index); ax.set_xticks(range(len(main.columns)),main.columns,rotation=90); ax.set_xlabel('Topic (−1 = outlier)'); fig.colorbar(im,ax=ax,label='Within-publication proportion'); fig.tight_layout(); fig.savefig(out/'publication_proportions.png',dpi=180); plt.close(fig)
    return counts,proportions

def review_packets(df,modern,classical,out,labels):
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    frames=[modern] + ([classical] if classical is not None else [])
    ids=df.sample(min(100,len(df)),random_state=SEED).article_id.tolist(); records=[]; rng=np.random.default_rng(SEED)
    for article in ids:
        row=df.set_index('article_id').loc[article]
        for index in rng.permutation(len(frames)):
            a=frames[index].set_index('article_id').loc[article]; model=str(a.model)
            records.append(dict(article_id=article,model=model,run_id=a.run_id,topic_id=a.topic_id,label=labels.get((model,int(a.topic_id)),'Outlier / unlabeled'),title=row.title,text=row.text))
    packet=pd.DataFrame(records)
    packet_hash=digest(packet.to_dict('records'))
    freeze=out/'review_freeze.json'
    if freeze.exists() and json.loads(freeze.read_text())['packet_hash']!=packet_hash: raise ValueError('Review models or labels changed; archive old review files before creating a new packet')
    write_json(freeze,dict(packet_hash=packet_hash))
    packet.to_csv(out/'review_packet.csv',index=False)
    for reviewer in ['reviewer_1','reviewer_2']:
        path=out/f'{reviewer}.csv'
        if not path.exists(): packet.drop(columns=['text']).assign(fit_rating='',irrelevant='',ambiguous_label='',notes='').to_csv(path,index=False)
    outlier_ids=modern[modern.topic_id.eq(-1)].sample(min(20,int(modern.topic_id.eq(-1).sum())),random_state=SEED).article_id
    df[df.article_id.isin(outlier_ids)].to_csv(out/'outlier_review.csv',index=False)
    write_json(out/'review_status.json',dict(joint_comparison_ready=classical is not None,sampled_articles=len(ids),instructions='Two independent reviewers: fit_rating 1–5, irrelevant/ambiguous_label true or false. Freeze labels before review.'))
    return packet

def summarize_reviews(out):
    from sklearn.metrics import cohen_kappa_score
    out=Path(out); a=pd.read_csv(out/'reviewer_1.csv'); b=pd.read_csv(out/'reviewer_2.csv'); keys=['article_id','model','run_id']
    if a.fit_rating.isna().any() or b.fit_rating.isna().any(): return 'Human evaluation pending: complete both reviewer CSVs.'
    for frame in [a,b]:
        if frame.duplicated(keys).any() or not frame.fit_rating.between(1,5).all() or not frame.fit_rating.mod(1).eq(0).all(): raise ValueError('Invalid review ratings or duplicate rows')
        for flag in ['irrelevant','ambiguous_label']:
            if not frame[flag].astype(str).str.lower().isin(['true','false']).all(): raise ValueError('Complete true/false review flags')
    joined=a.merge(b,on=keys,validate='one_to_one',suffixes=('_1','_2'))
    if len(joined)!=len(a) or len(joined)!=len(b): raise ValueError('Reviewer samples differ')
    result=[]
    for model,g in joined.groupby('model'):
        result.append(dict(model=model,mean_1=g.fit_rating_1.mean(),mean_2=g.fit_rating_2.mean(),exact_agreement=float(g.fit_rating_1.eq(g.fit_rating_2).mean()),weighted_kappa=cohen_kappa_score(g.fit_rating_1,g.fit_rating_2,weights='quadratic')))
    pd.DataFrame(result).to_csv(out/'human_evaluation.csv',index=False)
    pd.concat([a.assign(reviewer=1),b.assign(reviewer=2)]).groupby(['model','reviewer','fit_rating']).size().to_csv(out/'rating_distributions.csv')
    joined.sort_values('fit_rating_1').to_csv(out/'review_examples.csv',index=False)
    return pd.DataFrame(result)
