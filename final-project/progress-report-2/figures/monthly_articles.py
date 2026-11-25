"""Monthly AV article counts, stacked by publication, for the PR2 Data section."""
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'code'))
from shared.corpus import load_corpus

TOP = ['TechCrunch', 'CNBC', 'Reuters', 'The Verge']
COLORS = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#b4b2a9']  # categorical slots 1-4, gray for Other
OUT = Path(__file__).resolve().parent/'monthly_articles.pdf'

df = load_corpus()
df['month'] = pd.to_datetime(df.date).dt.to_period('M').dt.to_timestamp()
df['group'] = df.publication.where(df.publication.isin(TOP), 'Other')
counts = df.groupby(['month', 'group']).size().unstack(fill_value=0)[TOP + ['Other']]
counts = counts.reindex(pd.date_range(counts.index.min(), counts.index.max(), freq='MS'), fill_value=0)
print(f'{len(df)} articles, {len(counts)} months, peak {counts.sum(axis=1).max()} in {counts.sum(axis=1).idxmax():%Y-%m}')

plt.rcParams.update({'font.family': 'serif', 'font.size': 7, 'axes.linewidth': 0.5})
fig, ax = plt.subplots(figsize=(3.5, 1.8))
ax.stackplot(counts.index, counts.T.values, labels=counts.columns, colors=COLORS,
             edgecolor='white', linewidth=0.4)
ax.set_ylabel('Articles per month')
ax.set_xlim(counts.index.min(), counts.index.max())
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.grid(axis='y', linewidth=0.3, color='#d0cfc8')
ax.set_axisbelow(True)
for side in ('top', 'right'):
    ax.spines[side].set_visible(False)
ax.tick_params(width=0.5, length=2)
ax.legend(loc='lower left', bbox_to_anchor=(0, 1.0), ncol=5, frameon=False, fontsize=6, handlelength=1, columnspacing=0.8)
fig.tight_layout(pad=0.2)
fig.savefig(OUT)
print(f'Wrote {OUT}')
