"""Reproducible article-level BERTopic workflow; imports are lazy for audit-only use."""
from pathlib import Path
import hashlib, html, json, platform, re, time
import importlib.metadata as metadata
import numpy as np
import pandas as pd

SEED = 42
MODEL = 'thenlper/gte-small'

def write_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=str))

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

def clean_text(text):
    # Only strip recognizable HTML tags, preserving comparisons and punctuation.
    text = re.sub(r'</?(?:p|div|span|br|a|strong|em|ul|li|h[1-6]|script|style)\b[^>]*>', ' ', str(text), flags=re.I)
    return re.sub(r'\s+', ' ', html.unescape(text)).strip()

def audit_corpus(root):
    root = Path(root); out = root/'Results/modern'; out.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(root.parent.parent/'self_driving_articles.csv')
    assert df.X1.notna().all() and df.X1.is_unique, 'Article IDs must be unique'
    df.insert(0, 'article_id', df.X1.astype(str))
    assert df.article.notna().all() and df.publication.notna().all()
    df['date'] = pd.to_datetime(df.date, errors='raise').dt.strftime('%Y-%m-%d')
    df['text'] = df.article.map(clean_text)
    assert df.text.str.len().gt(0).all()
    df['duplicate_body'] = df.article.duplicated(keep='first')
    df['measured_word_count'] = df.article.str.split().str.len()
    df['word_count_difference'] = df.measured_word_count - df.word_count
    summary = dict(rows=len(df), source_columns=15, publications=df.publication.nunique(),
                   date_min=df.date.min(), date_max=df.date.max(), duplicate_bodies=int(df.duplicate_body.sum()),
                   missing=df.isna().sum().to_dict(), word_count_mismatches=int(df.word_count_difference.ne(0).sum()),
                   word_quantiles=df.measured_word_count.quantile([0,.25,.5,.75,.9,.99,1]).to_dict())
    df.to_csv(out/'corpus.csv', index=False)
    write_json(out/'corpus_summary.json', summary)
    if not (out/'corpus_review.csv').exists():
        df.sample(min(30,len(df)), random_state=SEED).assign(boilerplate='', malformed='', relevance='', notes='').to_csv(out/'corpus_review.csv',index=False)
    write_json(out/'corpus_manifest.json', dict(article_ids=df.article_id.tolist(), corpus_hash=digest(df[['article_id','text']].values.tolist())))
    return df, summary

def token_chunks(text, tokenizer, size=480):
    ids = tokenizer.encode(text, add_special_tokens=False)
    if not ids: raise ValueError('Empty token sequence')
    chunks = [ids[i:i+size] for i in range(0,len(ids),size)]
    assert sum(map(len,chunks)) == len(ids)
    assert all(len(c)+tokenizer.num_special_tokens_to_add(pair=False) <= 512 for c in chunks)
    return chunks

def validate_embeddings(arr, n):
    if arr.shape != (n,384) or not np.isfinite(arr).all() or not np.allclose(np.linalg.norm(arr,axis=1),1,atol=1e-4):
        raise ValueError('Invalid or misaligned embeddings')

def embed_corpus(df, root, pilot=False):
    import torch
    from sentence_transformers import SentenceTransformer
    from huggingface_hub import model_info
    root=Path(root); cache=root/'Results/modern/cache'; cache.mkdir(parents=True,exist_ok=True)
    download_start=time.perf_counter()
    # Resolve mutable model name to an immutable revision and include it in cache identity.
    revision_path=cache/'model_revision.json'
    if revision_path.exists():
        revision=json.loads(revision_path.read_text())['revision']
    else:
        pointer_path=root/'Results/modern/embedding_pointer.json'
        revision=json.loads(pointer_path.read_text())['manifest']['revision'] if pointer_path.exists() else model_info(MODEL).sha
        write_json(revision_path,dict(model=MODEL,revision=revision))
    device='mps' if torch.backends.mps.is_available() else 'cpu'
    local=(cache/'models/models--thenlper--gte-small/snapshots'/revision).exists()
    model=SentenceTransformer(MODEL, revision=revision, device=device, cache_folder=str(cache/'models'),local_files_only=local)
    model.eval()
    download_seconds=time.perf_counter()-download_start
    manifest=dict(article_ids=df.article_id.astype(str).tolist(), text_hash=digest(df.text.tolist()), model=MODEL, revision=revision, chunk_tokens=480, pooling='token_weighted_mean_l2', dimension=384)
    key=digest(manifest); folder=cache/key; folder.mkdir(exist_ok=True)
    manifest_path=folder/'manifest.json'
    if manifest_path.exists() and json.loads(manifest_path.read_text()) != manifest: raise ValueError('Cache manifest mismatch')
    write_json(manifest_path,manifest)
    started=time.perf_counter(); vectors=[]; diagnostics=[]; reused=0
    for i,row in enumerate(df.itertuples()):
        path=folder/f'{i:05d}.npz'
        if path.exists():
            with np.load(path) as saved: v=saved['embedding']; counts=saved['counts']
            validate_embeddings(v[None,:],1); reused+=1
        else:
            chunks=token_chunks(row.text,model.tokenizer); counts=np.array(list(map(len,chunks)))
            outputs=[]
            for j in range(0,len(chunks),32):
                batch=[[model.tokenizer.cls_token_id]+c+[model.tokenizer.sep_token_id] for c in chunks[j:j+32]]
                width=max(map(len,batch))
                features={'input_ids':torch.tensor([c+[model.tokenizer.pad_token_id]*(width-len(c)) for c in batch],device=device),
                          'attention_mask':torch.tensor([[1]*len(c)+[0]*(width-len(c)) for c in batch],device=device)}
                with torch.no_grad(): outputs.append(model(features)['sentence_embedding'].cpu().numpy())
            v=np.average(np.concatenate(outputs),axis=0,weights=counts); v=(v/np.linalg.norm(v)).astype('float32')
            validate_embeddings(v[None,:],1)
            temp=path.with_suffix('.tmp.npz'); np.savez(temp,embedding=v,counts=counts); temp.replace(path)
        vectors.append(v); diagnostics.append(dict(article_id=row.article_id, chunks=len(counts), tokens=int(sum(counts)), largest_chunk=int(max(counts))))
        if (i+1)%200==0: print(f'Embedded {i+1}/{len(df)} articles',flush=True)
    arr=np.stack(vectors); validate_embeddings(arr,len(df))
    pd.DataFrame(diagnostics).to_csv(folder/'chunk_diagnostics.csv',index=False)
    np.save(folder/'embeddings.npy',arr)
    timing=dict(model_load_download_seconds=download_seconds,embedding_seconds=time.perf_counter()-started,reused_articles=reused,device=device)
    timing_path=folder/'timings.json'
    previous=json.loads(timing_path.read_text()) if timing_path.exists() else {}
    write_json(timing_path,dict(first_execution=previous.get('first_execution',previous or timing),latest_execution=timing))
    if not pilot: write_json(root/'Results/modern/embedding_pointer.json',dict(folder=str(folder.relative_to(root)),manifest=manifest))
    return arr, folder

def load_inputs(root):
    root=Path(root); df=pd.read_csv(root/'Results/modern/corpus.csv',dtype={'article_id':str})
    pointer=json.loads((root/'Results/modern/embedding_pointer.json').read_text()); m=pointer['manifest']
    if m['article_ids'] != df.article_id.tolist() or m['text_hash'] != digest(df.text.tolist()): raise ValueError('Corpus/cache mismatch')
    arr=np.load(root/pointer['folder']/'embeddings.npy'); validate_embeddings(arr,len(df))
    return df,arr

def representation_text(text):
    # Match BERTopic's English keyword preprocessing before fitting a fixed vocabulary.
    return re.sub(r'[^A-Za-z0-9 ]+', '', text.replace('\n',' ').replace('\t',' ')) or 'emptydoc'

def reference_texts(df):
    from sklearn.feature_extraction.text import CountVectorizer
    from gensim.corpora import Dictionary
    tokenizer=CountVectorizer(stop_words='english').build_analyzer()
    texts=[tokenizer(representation_text(t)) for t in df.text]; return texts,Dictionary(texts)

def term_table(model):
    return pd.DataFrame([dict(topic_id=t,rank=i+1,term=w,weight=float(v)) for t in model.get_topics() for i,(w,v) in enumerate(model.get_topic(t)) if w])

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

def silhouette(embeddings,labels,metric):
    from sklearn.metrics import silhouette_score
    labels=np.asarray(labels); indices=np.flatnonzero(labels>=0)
    if len(indices)>2000: indices=np.sort(np.random.default_rng(SEED).choice(indices,2000,replace=False))
    k=len(set(labels[indices]))
    if not 2<=k<len(indices): return np.nan,'Undefined: fewer than two clusters or all singleton clusters'
    return float(silhouette_score(embeddings[indices],labels[indices],metric=metric)),'ok'

def evaluate(model,embeddings,texts,dictionary):
    terms=term_table(model); c=coherence(terms,texts,dictionary); labels=np.array(model.topics_)
    top=terms[(terms.topic_id>=0)&(terms['rank']<=10)]
    s,reason=silhouette(embeddings,labels,'cosine'); u,ureason=silhouette(model.umap_model.embedding_,labels,'euclidean')
    return dict(topic_count=len(set(labels)-{-1}),outlier_fraction=float(np.mean(labels==-1)),coherence=float(c.coherence.mean()),vocabulary_coverage=float(c.vocabulary_coverage.mean()),keyword_diversity=top.term.nunique()/len(top) if len(top) else np.nan,silhouette_cosine=s,silhouette_status=reason,silhouette_umap=u,silhouette_umap_status=ureason,topic_sizes=pd.Series(labels).value_counts().to_dict()),c

class FixedReduction:
    """Return precomputed coordinates while retaining semantic embeddings in BERTopic."""
    def __init__(self, coordinates): self.embedding_ = coordinates
    def fit(self, X, y=None): return self
    def transform(self, X): return self.embedding_


def fit_run(df,embeddings,root,neighbors=15,cluster_size=50,seed=42):
    from bertopic import BERTopic
    from umap import UMAP
    from hdbscan import HDBSCAN
    from sklearn.feature_extraction.text import CountVectorizer
    run=f'n{neighbors}_c{cluster_size}_s{seed}'; folder=Path(root)/'Results/modern/runs'/run; folder.mkdir(parents=True,exist_ok=True)
    print(f'{run}: reduction',flush=True)
    start=time.perf_counter()
    reduction=UMAP(n_components=5,n_neighbors=neighbors,min_dist=0,metric='cosine',random_state=seed)
    reduced=reduction.fit_transform(embeddings); reduction_seconds=time.perf_counter()-start
    start=time.perf_counter(); cluster=HDBSCAN(min_cluster_size=cluster_size,min_samples=10,metric='euclidean',cluster_selection_method='eom',prediction_data=True).fit(reduced); clustering_seconds=time.perf_counter()-start
    # Fixed adapters prevent BERTopic from refitting the timed reduction/clustering.
    from bertopic.cluster import BaseCluster
    vocabulary=CountVectorizer(stop_words='english',ngram_range=(1,1),min_df=5).fit(df.text.map(representation_text)).vocabulary_
    model=BERTopic(embedding_model=None,umap_model=FixedReduction(reduced),hdbscan_model=BaseCluster(),vectorizer_model=CountVectorizer(stop_words='english',ngram_range=(1,1),vocabulary=vocabulary),top_n_words=10,verbose=False)
    start=time.perf_counter(); model.fit_transform(df.text.tolist(),embeddings=embeddings,y=cluster.labels_)
    representation_seconds=time.perf_counter()-start
    model.umap_model=reduction; model.hdbscan_model=cluster
    print(f'{run}: coherence and silhouettes',flush=True)
    texts,dictionary=reference_texts(df); start=time.perf_counter(); metrics,per_topic=evaluate(model,embeddings,texts,dictionary); evaluation_seconds=time.perf_counter()-start
    metrics.update(run_id=run,neighbors=neighbors,cluster_size=cluster_size,seed=seed,reduction_seconds=reduction_seconds,clustering_seconds=clustering_seconds,representation_seconds=representation_seconds,evaluation_seconds=evaluation_seconds)
    export_run(model,df,folder,run); per_topic.to_csv(folder/'coherence.csv',index=False)
    import pickle
    with open(folder/'model.pkl','wb') as f: pickle.dump(model,f)
    write_json(folder/'manifest.json',dict(metrics=metrics,corpus_hash=digest(df[['article_id','text']].values.tolist()),embedding_hash=digest(embeddings.tolist()),parameters=dict(n_components=5,n_neighbors=neighbors,min_dist=0,umap_metric='cosine',seed=seed,min_cluster_size=cluster_size,min_samples=10,cluster_metric='euclidean',cluster_selection_method='eom',vocabulary_min_article_frequency=5),hardware=platform.platform(),versions={p:metadata.version(p) for p in ['bertopic','sentence-transformers','gensim','umap-learn','hdbscan','scikit-learn']}))
    return model,metrics

def cached_run(df,embeddings,root,neighbors,cluster_size,seed=42):
    folder=Path(root)/'Results/modern/runs'/f'n{neighbors}_c{cluster_size}_s{seed}'
    path=folder/'manifest.json'
    if path.exists():
        manifest=json.loads(path.read_text())
        if manifest['corpus_hash']!=digest(df[['article_id','text']].values.tolist()) or manifest['embedding_hash']!=digest(embeddings.tolist()):
            raise ValueError('Existing experiment uses different corpus or embeddings; archive it before refitting')
        return load_model(folder),manifest['metrics']
    return fit_run(df,embeddings,root,neighbors,cluster_size,seed)


def export_run(model,df,folder,run):
    folder=Path(folder); folder.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(dict(article_id=df.article_id,model='bertopic',run_id=run,topic_id=model.topics_,membership_strength=model.hdbscan_model.probabilities_)).to_csv(folder/'assignments.csv',index=False)
    term_table(model).to_csv(folder/'terms.csv',index=False)
    model.get_topic_info().rename(columns={'Topic':'topic_id','Count':'count','Name':'label'}).to_csv(folder/'topics.csv',index=False)
    evidence=[]
    for topic,docs in model.get_representative_docs().items():
        for doc in docs[:3]:
            row=df[df.text==doc].iloc[0]; evidence.append(dict(topic_id=topic,article_id=row.article_id,title=row.title,text=doc))
    pd.DataFrame(evidence).to_csv(folder/'representatives.csv',index=False)

def load_model(folder):
    import pickle
    with open(Path(folder)/'model.pkl','rb') as f: return pickle.load(f)  # Trusted local artifacts only.

def shortlist(root):
    out=Path(root)/'Results/modern'; records=[json.loads(p.read_text())['metrics'] for p in (out/'runs').glob('*s42/manifest.json')]
    if not records: raise ValueError('No completed experiments; run the six fits first')
    table=pd.DataFrame(records); table.to_csv(out/'experiments.csv',index=False)
    finalists=table[table.topic_count.ge(2)].sort_values(['coherence','run_id'],ascending=[False,True]).head(3)
    if finalists.empty: raise ValueError('No run produced at least two topics; inspect coverage and revise the bounded study explicitly')
    reviews=[]
    for run in finalists.run_id:
        folder=out/'runs'/run; topics=pd.read_csv(folder/'topics.csv'); evidence=pd.read_csv(folder/'representatives.csv')
        for t in topics[topics.topic_id.ge(0)].nlargest(5,'count').itertuples():
            reviews.append(dict(run_id=run,topic_id=t.topic_id,keywords=t.label,representative_articles=' | '.join(evidence[evidence.topic_id==t.topic_id].article_id.astype(str)),semantic_consistency='',label_specificity='',notes=''))
    path=Path(root)/'selection_review/selection_review.csv'
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists(): pd.DataFrame(reviews).to_csv(path,index=False)
    else:
        existing=pd.read_csv(path)
        expected={(r['run_id'],r['topic_id']) for r in reviews}
        actual=set(zip(existing.run_id,existing.topic_id))
        if actual!=expected or existing.duplicated(['run_id','topic_id']).any(): raise ValueError('Selection review belongs to a different shortlist; archive it and regenerate')
    return table,finalists

def select_model(root):
    out=Path(root)/'Results/modern'; table,finalists=shortlist(root); reviews=pd.read_csv(Path(root)/'selection_review/selection_review.csv')
    scores=['semantic_consistency','label_specificity']
    if reviews.empty or reviews[scores].isna().any().any(): raise ValueError('Complete selection_review.csv with 1–5 ratings before selecting a model')
    if not reviews[scores].apply(lambda s:s.between(1,5)).all().all(): raise ValueError('Ratings must be 1–5')
    reviews['rating']=reviews[scores].mean(axis=1)
    chosen=finalists.merge(reviews.groupby('run_id').rating.mean(),on='run_id').sort_values(['rating','coherence','outlier_fraction','run_id'],ascending=[False,False,True,True]).iloc[0]
    write_json(out/'selected_run.json',chosen.to_dict()); return load_model(out/'runs'/chosen.run_id),chosen

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
