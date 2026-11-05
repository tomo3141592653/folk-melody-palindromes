# 図1: 回文2つの連結(元の事象)の識別できる部分の O/E を長さの帯ごとに。数値は台帳 results/two_pal.json(build_ledger_two_pal.py が作る)から読む
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
bands = ['4–6', '7–9', '10–12', '13–16']
import json
L = json.load(open('results/two_pal.json'))
names = {'essen': 'Essen (exploratory)', 'fsinst_prespecified': 'MTC-FS-INST, pre-specified',
         'fsinst_disjoint_conditioned': 'MTC-FS-INST, overlap removed\n(null conditioned)'}
data = {names[k]: [(L[k]['bands'][b]['oe'], L[k]['bands'][b]['lo'], L[k]['bands'][b]['hi']) for b in ('4-6', '7-9', '10-12', '13-16')] for k in names}
colors = ['#0072B2', '#E69F00', '#009E73']; markers = ['o', 's', '^']
fig, ax = plt.subplots(figsize=(6.4, 4.0), dpi=200)
for j, ((name, vals), c, m) in enumerate(zip(data.items(), colors, markers)):
    xs = [i + (j - 1) * 0.18 for i in range(len(bands))]
    ax.errorbar(xs, [v[0] for v in vals], yerr=[[v[0] - v[1] for v in vals], [v[2] - v[0] for v in vals]],
                fmt=m, color=c, ms=6, capsize=3, lw=1.5, label=name)
ax.axhline(1, color='#888888', lw=1, ls='--')
ax.set_xticks(range(len(bands))); ax.set_xticklabels(bands)
ax.set_xlabel('Phrase length (notes)'); ax.set_ylabel('Observed / expected\n(transition-preserving null)')
ax.set_ylim(0.6, 2.8); ax.spines[['top', 'right']].set_visible(False); ax.grid(axis='y', color='#eeeeee')
ax.legend(frameon=False, fontsize=8, loc='upper left')
ax.set_title('Phrases that factor into two palindromes (identifiable subset)', fontsize=9)
fig.tight_layout(); fig.savefig('figures/fig1_two_pal.png')
