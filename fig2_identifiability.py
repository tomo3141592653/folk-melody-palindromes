# 図2: 遷移を保つ帰無の下で retrograde 型になれるかが決まってしまうフレーズの割合(Essen、重複除去なし)。台帳 results/ident.json から
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
L = json.load(open('results/ident.json'))
bands = ['4-9', '10-16']; parts = [('q=0', 'cannot be retrograde (q = 0)', '#CCCCCC'), ('q=1', 'always retrograde (q = 1)', '#0072B2'), ('0<q<1', 'identifiable (0 < q < 1)', '#E69F00')]
fig, ax = plt.subplots(figsize=(6.4, 2.6), dpi=200)
for y, b in enumerate(bands):
    d = L[f'{b}|retrograde']; tot = sum(d[k] for k, _, _ in parts); left = 0
    for k, lab, c in parts:
        w = d[k] / tot
        ax.barh(y, w, left=left, color=c, edgecolor='white', height=0.55, label=lab if y == 0 else None)
        if w > 0.15: ax.text(left + w / 2, y, f'{d[k]:,}', ha='center', va='center', fontsize=8, color='white' if k == 'q=1' else 'black')
        left += w
    obs = d['q=1 実際'] + d['0<q<1 実際']
    ax.text(1.01, y, f'q = 1: {d["q=1"]:,}   0 < q < 1: {d["0<q<1"]:,}\nobserved retrograde: {obs:,} (q = 1: {d["q=1 実際"]:,})', va='center', fontsize=7.5)
ax.set_yticks(range(len(bands))); ax.set_yticklabels([b.replace('-', '–') + ' notes' for b in bands]); ax.invert_yaxis()
ax.set_xlim(0, 1); ax.set_xlabel('Share of Essen phrases'); ax.spines[['top', 'right']].set_visible(False)
ax.legend(frameon=False, fontsize=7.5, ncol=3, loc='lower center', bbox_to_anchor=(0.5, 1.0))
fig.tight_layout(); fig.savefig('figures/fig2_identifiability.png', bbox_inches='tight')
