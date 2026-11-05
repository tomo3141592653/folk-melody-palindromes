# 遷移が可逆(遷移の表が対称かつ最初=最後の音)なフレーズの割合を、実際と「音の並べ替え」(論文の比較相手)とで比べる。曲内重複除去
import sys, collections
import numpy as np
sys.path.insert(0, '.')
from mtc_loader import phrases_mtc
def rev(p):
    c = collections.Counter(zip(p, p[1:]))
    return p[0] == p[-1] and all(c[(a, b)] == c[(b, a)] for a, b in c)
if __name__ == "__main__":
    BANDS = [(4, 6), (7, 9), (10, 12), (13, 16)]
    rng = np.random.default_rng(0); S = 200
    st = collections.defaultdict(collections.Counter); seen = set()
    for sid, p in phrases_mtc(sys.argv[1]):
        L = len(p); b = next((k for k in BANDS if k[0] <= L <= k[1]), None)
        if b is None or (sid, tuple(p)) in seen: continue
        seen.add((sid, tuple(p)))
        s = st[b]; s['N'] += 1; s['O'] += rev(p)
        sh = rng.permuted(np.tile(np.array(p), (S, 1)), axis=1)
        s['E'] += sum(rev(list(x)) for x in sh) / S
    for b in BANDS:
        s = st[b]; print(f"{b[0]}-{b[1]}音 N={s['N']} 可逆 実際{s['O']}({s['O']/s['N']:.1%}) 音の並べ替えの期待{s['E']:.1f} O/E {s['O']/s['E']:.2f}")
