# 図4: 回文2つ(clean の定義)を句全体が周期的かどうかで分けた O/E。台帳 results/two_pal_clean_*_per.json / *_noper.json から
import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
B = ['7-9', '10-12', '13-16']
S = [('essen', 'Essen'), ('fsinst_disjoint', 'MTC-FS-INST, overlap removed')]
fig, axes = plt.subplots(1, 2, figsize=(8, 3.2), dpi=200, sharey=True)
for ax, (k, title) in zip(axes, S):
    for j, (opt, lab, col, mk) in enumerate([('per', 'periodic (a figure repeated in full)', '#D55E00', 'o'), ('noper', 'not periodic', '#0072B2', 's')]):
        d = json.load(open(f'results/two_pal_clean_{k}_{opt}.json'))['bands']
        x = [i + (j - 0.5) * 0.18 for i in range(len(B))]
        y = [d[b]['oe'] for b in B]; lo = [d[b]['oe'] - d[b]['lo'] for b in B]; hi = [d[b]['hi'] - d[b]['oe'] for b in B]
        ax.errorbar(x, y, yerr=[lo, hi], fmt=mk, color=col, capsize=3, lw=1.3, ms=5, label=lab)
    ax.axhline(1, color='grey', ls='--', lw=1); ax.set_yscale('log'); ax.set_ylim(0.4, 45); ax.set_yticks([0.5, 1, 2, 5, 10, 20, 40]); ax.set_yticklabels(['0.5', '1', '2', '5', '10', '20', '40'])
    ax.set_xticks(range(len(B))); ax.set_xticklabels([b.replace('-', '–') for b in B]); ax.set_xlabel('Phrase length (notes)')
    ax.set_title(title, fontsize=9); ax.spines[['top', 'right']].set_visible(False)
axes[0].set_ylabel('Observed / expected\n(transition-preserving null)'); axes[0].legend(fontsize=7, frameon=False, loc='upper left')
fig.tight_layout(); fig.savefig('figures/fig4_periodic.png')
