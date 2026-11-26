"""Reports from fixed exports, kept outside the model/cache identity helpers."""
from pathlib import Path
import argparse
import json
import re
import numpy as np
import pandas as pd
from robustness import (CODE, ROOT, MODERN, OUT, checksum, load_corpus, corpus_hash,
                        write_json, aligned_assignments, seed_publication_comparison)

BASE = MODERN/'Results/modern/runs/n30_c25_s42'
CLASSICAL = CODE/'classical-methods/results'
COMPARISON = MODERN/'Results/comparison/n30_c25_s42'
THEMES = {'Tesla': (9, 0), 'Waymo': (35, 1), 'Litigation': (7, 2),
          'Freight': (11, 7), 'Congress': (4, 20), 'Urban mobility': (28, 16),
          'Hill.TV format': (1, 67)}


def read_assignments(folder, df):
    return aligned_assignments(df, pd.read_csv(folder/'assignments.csv', dtype={'article_id': str}))


def compare(df, baseline_folder, other_folder, output):
    base, other = read_assignments(baseline_folder, df), read_assignments(other_folder, df)
    summary = seed_publication_comparison(df, base, other, output)
    changes = pd.read_csv(output/'publication_changes.csv')
    main = changes.loc[changes.article_count.ge(50)]
    differences = main.difference.abs()
    summary.update(matched_topic_count=int(changes.baseline_topic.nunique()),
                   matched_publication_rows_n_ge_50=len(main),
                   median_abs_change_pp=float(differences.median()*100),
                   p95_abs_change_pp=float(differences.quantile(.95)*100),
                   max_abs_change_pp=float(differences.max()*100))
    terms = [pd.read_csv(p/'terms.csv') for p in [baseline_folder, other_folder]]
    wordsets = [{t: set(g.sort_values('rank').head(10).term) for t,g in frame.groupby('topic_id')} for frame in terms]
    matching = pd.read_csv(output/'topic_matches.csv')
    matching['baseline_count'] = matching.baseline_topic.map(base.topic_id.value_counts())
    matching['other_count'] = matching.other_topic.map(other.topic_id.value_counts())
    matching['baseline_retention'] = matching.overlap/matching.baseline_count
    matching['other_purity'] = matching.overlap/matching.other_count
    matching['keyword_jaccard'] = [len(wordsets[0][r.baseline_topic]&wordsets[1][r.other_topic])/len(wordsets[0][r.baseline_topic]|wordsets[1][r.other_topic]) for r in matching.itertuples()]
    for i, col in enumerate(['baseline_topic','other_topic']):
        matching[col+'_keywords'] = matching[col].map(terms[i].sort_values('rank').groupby('topic_id').term.agg(', '.join))
    matching.to_csv(output/'matched_topic_diagnostics.csv', index=False)
    write_json(output/'summary.json', summary)
    return summary, matching, changes


def coverage_rule(df, minimum_annual=20, minimum_years=3):
    """Choose period using coverage only, never topic assignments.

    Among >=3 contiguous complete calendar years, maximize number of outlets
    with >=20 articles EVERY year; ties: longest interval then earliest start.
    """
    dates = pd.to_datetime(df.date)
    counts = pd.crosstab(df.publication, dates.dt.year)
    years = [y for y in counts if dates.min() <= pd.Timestamp(y,1,1) and dates.max() >= pd.Timestamp(y,12,31)]
    candidates = []
    for i, start in enumerate(years):
        for end in years[i+minimum_years-1:]:
            period = list(range(start,end+1))
            if not set(period).issubset(years):
                continue
            eligible = counts.index[counts[period].ge(minimum_annual).all(axis=1)].tolist()
            candidates.append(dict(start=start, end=end, years=len(period),
                                   publications=len(eligible), retained_publications=eligible))
    if not candidates:
        raise ValueError('No adequate common period under prespecified coverage rule')
    candidates.sort(key=lambda r:(-r['publications'], -r['years'], r['start']))
    return candidates[0], pd.DataFrame(candidates), counts


def publication_shares(df, a):
    joined = df[['article_id','publication']].merge(a[['article_id','topic_id']], on='article_id', validate='one_to_one')
    counts = pd.crosstab(joined.publication, joined.topic_id)
    return counts, counts.div(counts.sum(axis=1), axis=0)


def shared_period(df):
    folder = OUT/'shared_period'; folder.mkdir(exist_ok=True)
    rule, candidates, coverage = coverage_rule(df)
    candidates.to_csv(folder/'candidate_periods.csv', index=False)
    coverage.to_csv(folder/'annual_coverage.csv')
    dates = pd.to_datetime(df.date)
    keep = dates.dt.year.between(rule['start'],rule['end']) & df.publication.isin(rule['retained_publications'])
    restricted = df.loc[keep].reset_index(drop=True)
    counts = df.groupby('publication').agg(full_count=('article_id','size'), full_first=('date','min'), full_last=('date','max'))
    in_period = df.loc[dates.dt.year.between(rule['start'],rule['end'])].groupby('publication').agg(period_count=('article_id','size'), period_first=('date','min'), period_last=('date','max'))
    counts = counts.join(in_period)
    counts['retained'] = counts.index.isin(rule['retained_publications'])
    counts.to_csv(folder/'publication_coverage.csv')
    restricted[['article_id','publication','date']].to_csv(folder/'retained_ids.csv', index=False)
    write_json(folder/'protocol.json', dict(**rule, n_retained=len(restricted),
        corpus_hash=corpus_hash(df), minimum_articles_each_year=20,
        rule='Complete calendar-year blocks of at least 3 years; maximize eligible outlets (>=20 articles in every year), then longest block, then earliest start; determined from coverage only',
        limitation='Coverage sensitivity using existing fitted assignments; not temporal refitting or coverage of all outlet output; Vice and Vice News never grouped'))
    summaries=[]; examples=[]
    for model, source, pos in [('lda',CLASSICAL,0),('bertopic',BASE,1)]:
        a = read_assignments(source,df)
        full_counts, full = publication_shares(df,a)
        sub_counts, sub = publication_shares(restricted,a[a.article_id.isin(restricted.article_id)])
        sub = sub.reindex(columns=full.columns,fill_value=0)
        sub_counts = sub_counts.reindex(columns=full.columns,fill_value=0)
        sub.to_csv(folder/f'{model}_proportions.csv'); sub_counts.to_csv(folder/f'{model}_counts.csv')
        delta = sub-full.loc[sub.index]
        delta.to_csv(folder/f'{model}_changes.csv')
        tv=.5*delta.abs().sum(axis=1)
        for pub in tv.index:
            summaries.append(dict(model=model,publication=pub,n_full=int(full_counts.loc[pub].sum()),
                n_period=int(sub_counts.loc[pub].sum()),total_variation=float(tv[pub]),
                max_abs_change_pp=float(delta.loc[pub].abs().max()*100)))
        for theme, ids in THEMES.items():
            for pub in sub.index:
                t=ids[pos]
                examples.append(dict(model=model,theme=theme,topic_id=t,publication=pub,
                    n_full=int(full_counts.loc[pub].sum()),n_period=int(sub_counts.loc[pub].sum()),
                    full_share=float(full.loc[pub,t]),period_share=float(sub.loc[pub,t]),
                    change_pp=float(delta.loc[pub,t]*100)))
    pd.DataFrame(summaries).to_csv(folder/'distribution_changes.csv',index=False)
    pd.DataFrame(examples).to_csv(folder/'principal_theme_shares.csv',index=False)


def sensitivity(df):
    summaries=[]; tracked=[]
    experiments=pd.read_csv(MODERN/'Results/modern/experiments.csv')
    alternatives=[('bertopic_grid',r,BASE,MODERN/'Results/modern/runs'/r,1) for r in experiments.run_id if r!='n30_c25_s42']
    alternatives += [('lda_seed',f'lda_full_s{s}',CLASSICAL,OUT/f'lda_full_s{s}',0) for s in [7,21] if (OUT/f'lda_full_s{s}/manifest.json').exists()]
    for kind, name, baseline, other, pos in alternatives:
        folder=OUT/kind/name
        summary,matches,changes=compare(df,baseline,other,folder)
        summaries.append(dict(kind=kind,run=name,**{k:v for k,v in summary.items() if not isinstance(v,list)} ,
                         unmatched_baseline_n=len(summary['unmatched_baseline_topics']),
                         unmatched_other_n=len(summary['unmatched_other_topics']),
                         split_candidates_n=len(summary['split_candidates']),merge_candidates_n=len(summary['merge_candidates'])))
        for theme,ids in THEMES.items():
            topic=ids[pos]
            match=matches[matches.baseline_topic.eq(topic)]
            if match.empty:
                tracked.append(dict(kind=kind,run=name,theme=theme,baseline_topic=topic,status='unmatched'))
                continue
            row=match.iloc[0]
            for r in changes[changes.baseline_topic.eq(topic)].itertuples():
                tracked.append(dict(kind=kind,run=name,theme=theme,status='automatic overlap match; inspect keywords',
                    baseline_topic=topic, other_topic=int(row.other_topic),
                    retention=float(row.baseline_retention),purity=float(row.other_purity),
                    keyword_jaccard=float(row.keyword_jaccard),other_keywords=row.other_topic_keywords,
                    publication=r.publication,n=r.article_count,baseline_share=r.baseline_share,
                    other_share=r.other_share,change_pp=r.difference*100))
    pd.DataFrame(summaries).to_csv(OUT/'sensitivity_summary.csv',index=False)
    pd.DataFrame(tracked).to_csv(OUT/'principal_theme_sensitivity.csv',index=False)


def split_reports(df):
    rows=[]; shifts=[]; pubshifts=[]; timing=[]
    for folder in sorted(OUT.iterdir()):
        if not folder.is_dir() or not (folder/'manifest.json').exists(): continue
        m=json.loads((folder/'manifest.json').read_text())
        timing.append(dict(run=folder.name,**m['timings']))
        if 'split' not in folder.name: continue
        a=read_assignments(folder,df)
        train=a.partition.eq('train'); held=~train
        counts=pd.crosstab(a.topic_id,a.partition).reindex(columns=['train','heldout'],fill_value=0)
        shares=counts.div(counts.sum(axis=0),axis=1)
        shifts.append(shares.reset_index().assign(model=a.model.iloc[0],difference=shares.heldout.values-shares.train.values))
        model=a.model.iloc[0]
        for pub,idx in df.groupby('publication').groups.items():
            aa=a.loc[idx]
            c=pd.crosstab(aa.topic_id,aa.partition).reindex(columns=['train','heldout'],fill_value=0)
            n=c.sum()
            tv=float(.5*(c.heldout/n.heldout-c.train/n.train).abs().sum()) if n.min()>0 else None
            pubshifts.append(dict(model=model,publication=pub,n_train=int(n.train),n_heldout=int(n.heldout),total_variation=tv))
        rows.append(dict(model=model,run=folder.name,**m['metrics'],
                         total_variation=float(.5*(shares.heldout-shares.train).abs().sum()),
                         max_topic_change_pp=float((shares.heldout-shares.train).abs().max()*100),
                         n_heldout=int(held.sum()),heldout_outlier_count=int((a.loc[held,'topic_id']==-1).sum())))
        rows[-1]['train_outlier_fraction'] = float(a.loc[train, 'topic_id'].eq(-1).mean())
        rows[-1]['heldout_outlier_fraction'] = float(a.loc[held, 'topic_id'].eq(-1).mean())
    pd.DataFrame(timing).to_csv(OUT/'new_stage_timings.csv',index=False)
    if rows:
        pd.DataFrame(rows).to_csv(OUT/'split_metrics.csv',index=False)
        pd.concat(shifts).to_csv(OUT/'split_topic_proportions.csv',index=False)
        pd.DataFrame(pubshifts).to_csv(OUT/'split_publication_shifts.csv',index=False)


def historical_evidence():
    """Preserve verbatim table fragments with source hashes, not fabricated run logs."""
    folder=OUT/'historical_lda';folder.mkdir(exist_ok=True)
    source=ROOT/'final-project/progress-report-3/pr3-submission.tex'
    text=source.read_text()
    for name in ['max-iter','alpha','eta']:
        table=next(t for t in re.findall(r'\\begin\{table\}.*?\\end\{table\}',text,re.S) if f'\\label{{tab:{name}}}' in t)
        (folder/f'{name}_source_table.tex').write_text(table+'\n')
    write_json(folder/'provenance.json',dict(source=str(source.relative_to(ROOT)),sha256=checksum(source),
        evidence_status='Historical manuscript tables only; not independently rerun; rounded values, no raw search logs recovered',
        k_search='PR2/PR3 document K=10,20,...,70 at max_iter=20; no raw per-K numerical results recovered in tracked files or local result folders',
        code_caveat='Current explore_configuration.py reads the selected configuration, so rerunning it is NOT reproduction of historical defaults',
        prior_caveat='Prior tables contain 1.0, omitted from prose grid; alpha 0.5 has higher rounded coherence than selected alpha 0.1. Dominant probability is not assignment accuracy.'))


def main():
    df=load_corpus();OUT.mkdir(parents=True,exist_ok=True)
    shared_period(df);sensitivity(df);split_reports(df);historical_evidence()
    write_json(OUT/'report_provenance.json',dict(corpus_hash=corpus_hash(df),
        reporting_code_sha256=checksum(Path(__file__)),
        sources={str(p.relative_to(ROOT)):checksum(p) for p in [BASE/'manifest.json',CLASSICAL/'manifest.json']},
        human_status='Awaiting actual label confirmations and independent ratings; none generated'))
    print('Saved coverage, matching, split/timing (when complete), and historical-evidence reports',flush=True)


if __name__=='__main__': main()
