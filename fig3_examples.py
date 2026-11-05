# 図3: 回文2つの連結になっている実例。重複を除いた MTC-FS-INST(fsinst_disjoint)から、13〜16音で、
# two_pal_clean.py と同じ条件(片方が1種類の音だけの分割と、等長で全音階に移したくり返しの分割を除く)を満たし、
# 見やすさのため両方の部分が4音以上のものを、ファイルの先頭から4本。切れ目に縦線
import gzip, json, itertools, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def pal(y): return y == y[::-1]
def clean_cut(x, dp):  # two_pal_clean.py の two_pal_clean と同じ条件で、通る切れ目を返す
    L = len(x)
    if pal(x): return None
    for k in range(2, L - 1):
        if not (pal(x[:k]) and pal(x[k:])): continue
        if len(set(x[:k])) == 1 or len(set(x[k:])) == 1: continue
        if 2 * k == L and len({b - a for a, b in zip(dp[:k], dp[k:])}) == 1: continue
        return k
    return None
ex = []
with gzip.open('data/mtcfeatures/fsinst_disjoint.jsonl.gz', 'rt') as fh:
    for line in fh:
        d = json.loads(line); f = d['features']
        for _, grp in itertools.groupby(zip(f['phrase_ix'], f['midipitch'], f['diatonicpitch']), key=lambda t: t[0]):
            g = list(grp); p = [m for _, m, _ in g]; L = len(p)
            if not 13 <= L <= 16: continue
            k = clean_cut(tuple(v % 12 for v in p), [dd for _, _, dd in g])
            if k and k >= 4 and L - k >= 4: ex.append((d['id'], p, k))
        if len(ex) >= 4: break
ex = ex[:4]
fig, axes = plt.subplots(1, 4, figsize=(9, 2.2), dpi=200)
for ax, (sid, p, k) in zip(axes, ex):
    ax.plot(range(len(p)), p, '-o', color='#0072B2', ms=3.5, lw=1.2)
    ax.axvline(k - 0.5, color='#E69F00', lw=1.5, ls='--')
    ax.set_title(f'{sid} ({len(p)} notes, cut {k}|{len(p) - k})', fontsize=7); ax.set_xticks([]); ax.tick_params(labelsize=6)
    ax.spines[['top', 'right']].set_visible(False)
axes[0].set_ylabel('MIDI pitch', fontsize=7)
fig.suptitle('Phrases that factor into two palindromes (dashed line: cut)', fontsize=8)
fig.tight_layout(); fig.savefig('figures/fig3_examples.png')
print([(s, k, len(p)) for s, p, k in ex])
