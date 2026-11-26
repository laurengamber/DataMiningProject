"""Build the 110-topic label-review index, decision ledger, and local HTML article cards."""
from html import escape
import json
import re
import pandas as pd
from robustness import ROOT, MODERN, OUT, checksum
from shared.corpus import load_corpus, write_json
from robustness_reports import COMPARISON, BASE, CLASSICAL, read_assignments


def prepare():
    df=load_corpus()
    reserved=set(json.loads((MODERN/'Results/modern/review_sample.json').read_text())['article_ids'])
    folder=OUT/'label_review';folder.mkdir(parents=True,exist_ok=True)
    records=[]; sources={}
    for kind,source in [('classical',CLASSICAL),('modern',BASE)]:
        path=COMPARISON/f'{kind}_draft_inventory.csv'
        drafts=pd.read_csv(path,keep_default_na=False)
        sources[str(path.relative_to(ROOT))]=checksum(path)
        a=read_assignments(source,df)
        joined=df[['article_id','publication']].merge(a,on='article_id',validate='one_to_one')
        lower=drafts.coherence.quantile(.2)
        for row in drafts.itertuples():
            ids=[s.strip() for s in row.evidence_ids.split('|') if s.strip()]
            if set(ids)&reserved: raise ValueError('Reserved evaluation ID in label evidence')
            if not ids or not set(ids).issubset(set(a.loc[a.topic_id.eq(row.topic_id),'article_id'])):
                raise ValueError('Evidence must belong to the proposed topic')
            pubs=joined.loc[joined.topic_id.eq(row.topic_id),'publication'].value_counts(normalize=True)
            flags=[]
            if row.coherence<=lower:flags.append('lower coherence quintile (diagnostic, not a human judgment)')
            if pubs.iloc[0]>=.8:flags.append('source concentrated: >=80% from one publication')
            if re.search('mixed|peripheral',row.proposed_label,re.I):flags.append('draft explicitly mixed/peripheral')
            if re.search('interview|transcript|roundup|newsletter|page artifact|promotion|commentary|discussion',row.proposed_label,re.I):flags.append('possible format-driven topic')
            records.append(dict(model=kind,topic_id=row.topic_id,draft_label=row.proposed_label,
                keywords=row.keywords,count=row.count,coherence=row.coherence,evidence_ids=row.evidence_ids,
                draft_evidence_notes=row.evidence_notes,leading_publication=pubs.index[0],
                leading_publication_share=float(pubs.iloc[0]),review_flags='; '.join(flags) or 'No automatic flag; still requires review'))
    table=pd.DataFrame(records)
    # Flags first, then larger topics; each topic appears exactly once in 11 batches.
    table['priority']=table.review_flags.ne('No automatic flag; still requires review').astype(int)
    table=table.sort_values(['priority','count','model','topic_id'],ascending=[False,False,True,True]).reset_index(drop=True)
    table['batch']=table.index//10+1
    table.to_csv(folder/'topic_review_index.csv',index=False)
    decision=table[['batch','model','topic_id','draft_label','evidence_ids']].copy()
    for field in ['decision','approved_label','reviewer_names','review_date','evidence_notes','reservation_attestation']:
        decision[field]=''
    decision_path=folder/'team_decisions.csv'
    if not decision_path.exists(): decision.to_csv(decision_path,index=False)
    else:
        old=pd.read_csv(decision_path,keep_default_na=False)
        pd.testing.assert_frame_equal(old[['model','topic_id','draft_label','evidence_ids']],decision[['model','topic_id','draft_label','evidence_ids']],check_dtype=False)
    actual_decisions = pd.read_csv(decision_path, keep_default_na=False)
    approved = int(actual_decisions.decision.eq('approve').sum())
    lines=['# Team topic-label review','',
        f'The starting inventory contains 110 assistant drafts. {approved} labels have explicit human approval recorded in the decision ledger; {110-approved} remain pending. These are assisted naming decisions, not independent fit ratings.',
        'Work through one 10-topic batch at a time. Start with flagged topics; read full representative articles in the local HTML cards. '
        'Keywords and examples can reveal mixed themes, source identity, newsletters, transcripts and page artifacts. '
        'Do not interpret low coherence or these automatic flags as human findings.',
        '', 'Record actual decisions in `team_decisions.csv`: `approve`, `revise`, or `defer`; final approved label; '
        'reviewer names; review date; article evidence notes; and an explicit reservation attestation only if true. '
        'All supplied evidence IDs exclude the reserved 100 articles. New supporting evidence must also be nonreserved and belong to the topic. '
        'Leave undecided entries blank. Rerunning preparation preserves the decision file.', '',
        '| Batch | Topics | Full local article cards |','| --- | ---: | --- |']
    corpus=df.set_index('article_id')
    for batch,group in table.groupby('batch'):
        cards=[]
        for row in group.itertuples():
            evidence=[]
            for aid in row.evidence_ids.split('|'):
                aid=aid.strip(); article=corpus.loc[aid]
                evidence.append(f'<details><summary>{escape(aid)} — {escape(str(article.title))} '
                    f'({escape(str(article.publication))}, {escape(str(article.date))})</summary>'
                    f'<p>{escape(str(article.text))}</p></details>')
            cards.append(f'<section><h2>{escape(row.model)} {row.topic_id}: {escape(row.draft_label)}</h2>'
                f'<p>{row.count} articles · c_v {row.coherence:.3f} · Leading source: '
                f'{escape(row.leading_publication)} ({row.leading_publication_share:.1%})</p>'
                f'<p><b>Review flags:</b> {escape(row.review_flags)}</p>'
                f'<p><b>Keywords:</b> {escape(row.keywords)}</p>'
                f'<p>{escape(row.draft_evidence_notes)}</p>'+''.join(evidence)+'</section>')
        filename=f'batch_{batch:02d}.html'
        (folder/filename).write_text('<!doctype html><meta charset="utf-8"><title>Draft topic label review</title>'
            '<style>body{font:17px/1.6 system-ui;max-width:1000px;margin:40px auto;padding:20px}section{border-top:2px solid #aaa;padding:20px 0}summary{cursor:pointer;font-weight:600}details p{white-space:pre-wrap}</style>'
            f'<h1>Label review batch {batch}</h1><p>Assistant drafts; actual team decisions required. '
            'Development evidence only, not the reserved evaluation packet.</p>'+''.join(cards))
        lines.append(f'| {batch} | {len(group)} | [{filename}]({filename}) |')
    (folder/'README.md').write_text('\n'.join(lines)+'\n')
    write_json(folder/'provenance.json',dict(sources=sources,topic_count=len(table),batch_count=int(table.batch.max()),
        evidence_unique_ids=len({i.strip() for v in table.evidence_ids for i in v.split('|')}),
        reserved_intersection=0,reservation_sha256=checksum(MODERN/'Results/modern/review_sample.json'),
        approved_labels=approved, pending_labels=110-approved,
        full_text='Local HTML cards ignored by Git; regenerate with prepare_label_review.py'))
    print(f'Prepared {len(table)} topics in {table.batch.max()} batches; {approved} approved.')


if __name__=='__main__':prepare()
