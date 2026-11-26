"""Focused report figures from existing exports; no fitting or input changes."""
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, MultipleLocator

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'pyproject.toml').exists())
OUT = Path(__file__).resolve().parent
RESULTS = ROOT / 'final-project/code/modern-methods/Results'
COMP = RESULTS / 'comparison/n30_c25_s42'

def read(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))

def save(fig, name):
    fig.savefig(OUT / f'{name}.png', dpi=220, facecolor='white')
    fig.savefig(OUT / f'{name}.pdf', facecolor='white')
    plt.close(fig)

plt.rcParams.update({'font.size': 9, 'axes.titlesize': 10, 'axes.labelsize': 9,
                     'pdf.fonttype': 42, 'ps.fonttype': 42,
                     'axes.spines.top': False, 'axes.spines.right': False})
colors = {'LDA': '#0072B2', 'BERTopic': '#D55E00'}
tables = {model: {r['publication']: r for r in read(COMP / sub / 'publication_counts.csv')}
          for model, sub in [('LDA', 'classical'), ('BERTopic', 'modern')]}
specs = [
    ('A  Waymo', 35, 1, ['The Verge', 'TechCrunch']),
    ('B  Uber–Waymo litigation', 7, 2, ['Vox', 'Reuters']),
    ('C  Congressional legislation', 4, 20, ['The Hill']),
    ('D  Urban mobility', 28, 16, ['Wired']),
]
data = []
fig, axes = plt.subplots(2, 2, figsize=(7.2, 4.5), sharex=True)
for ax, (title, lt, bt, pubs) in zip(axes.flat, specs):
    for i, pub in enumerate(pubs):
        ns = []
        for model, topic, offset in [('LDA', lt, -.16), ('BERTopic', bt, .16)]:
            row = tables[model][pub]
            n = sum(int(v) for k, v in row.items() if k != 'publication')
            count = int(row[str(topic)])
            share = count / n * 100
            ns.append(n)
            data.append(dict(panel=title, model=model, topic_id=topic, publication=pub,
                             count=count, denominator=n, percent=share))
            ax.barh(i + offset, share, height=.27, color=colors[model], label=model if i == 0 else None)
            ax.text(share + .5, i + offset, f'{share:.2f}%', va='center', fontsize=8)
        assert len(set(ns)) == 1
    ax.set_yticks(range(len(pubs)), [f'{p}\n(n={sum(int(v) for k,v in tables["LDA"][p].items() if k != "publication"):,})' for p in pubs])
    ax.set_ylim(len(pubs) - .45, -.55)
    ax.set_title(f'{title}\nLDA {lt} / BERTopic {bt}', loc='left')
    ax.set_xlim(0, 40)
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_major_formatter(PercentFormatter(100, decimals=0))
    ax.grid(axis='x', alpha=.18)
    ax.set_axisbelow(True)
for ax in axes[1]: ax.set_xlabel('Share of all corpus articles from outlet')
handles, labels = axes[0, 0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', ncol=2, frameon=False, bbox_to_anchor=(.52, 1.0))
fig.subplots_adjust(left=.15, right=.97, bottom=.13, top=.85, hspace=.65, wspace=.52)
save(fig, 'publication_examples')

cont = {int(r['topic_id_lda']): {int(k): int(v) for k, v in r.items() if k != 'topic_id_lda'}
        for r in read(COMP / 'assignment_contingency.csv')}
assert sum(cont[3].values()) == 356
assert sum(r[0] for r in cont.values()) == 538
uber_topics = [27, 26, 32, 45, -1]
uber = [cont[3][t] for t in uber_topics]
uber.insert(4, 356 - sum(uber))
uber_names = ['Tempe crash (B27)', 'CA permit dispute (B26)', 'Testing restart (B32)',
              'NTSB investigation (B45)', 'Other assigned topics', 'Unassigned (B−1)']
tesla = [cont[9][0], cont[17][0], 538 - cont[9][0] - cont[17][0]]
tesla_names = ['Products/upgrades (L9)', 'Crash investigations (L17)', 'Other LDA topics']
assert uber == [68, 66, 57, 30, 74, 61]
assert tesla == [227, 152, 159]
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.5))
for ax, names, values, total, title, palette in [
    (axes[0], uber_names, uber, 356, 'A  LDA 3: Uber testing/crash\nBERTopic destinations (n=356)', [colors['BERTopic']]*4 + ['#B8C0C7', '#6B6B6B']),
    (axes[1], tesla_names, tesla, 538, 'B  BERTopic 0: Tesla\nLDA sources (n=538)', [colors['LDA']]*2 + ['#B8C0C7']),
]:
    ax.barh(range(len(names)), values, color=palette, height=.6)
    ax.set_yticks(range(len(names)), names, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, max(values) * 1.28)
    for i, value in enumerate(values): ax.text(value + max(values)*.025, i, str(value), va='center', fontsize=9)
    ax.set_title(title, loc='left', pad=12)
    ax.set_xlabel('Articles')
    ax.grid(axis='x', alpha=.18); ax.set_axisbelow(True)
fig.subplots_adjust(left=.24, right=.98, bottom=.17, top=.80, wspace=1.25)
save(fig, 'topic_split_merge')

sources = [COMP / 'classical/publication_counts.csv', COMP / 'modern/publication_counts.csv',
           COMP / 'assignment_contingency.csv', COMP / 'comparison_identity.json']
(OUT / 'figure_data_and_provenance.json').write_text(json.dumps({
    'prepared_date': '2026-11-26', 'purpose': 'Main-report figure selection; illustrative, not exhaustive outlet rankings',
    'publication_examples': data,
    'split_example': dict(source_model='LDA', source_topic=3, denominator=356,
                         destinations=dict(zip(uber_names, uber))),
    'merge_example': dict(destination_model='BERTopic', destination_topic=0, denominator=538,
                         sources=dict(zip(tesla_names, tesla))),
    'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
    'qualifications': ['Publication denominators include BERTopic outliers.', 'Topic matches do not establish semantic equivalence.',
                       'Figure 2 panels use different denominators and axis ranges; each accounts for its full selected topic.',
                       'No uncertainty intervals or independent fit ratings are implied.'],
}, indent=2) + '\n')
print('Saved two focused figures in PNG/PDF with source counts and provenance.')
