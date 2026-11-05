# 型(retrograde・RI)と長さ帯ごとに、2音の組を保つ並べ替えの下での q(その型になる確率、総当たり)が 0・1・その間 のフレーズ数と、
# それぞれの中の実際のその型の本数を数える。重複除去なし(論文の census と同じ単位)
import sys, collections
import numpy as np
sys.path.insert(0, '.')
from mtc_loader import phrases_mtc
from census_repro import perms
from identifiability import all_paths, CAP
def classes(X, H):
    L = X.shape[1]; Q = X[:, H]; D = (X[:, None, :] - Q) % 12; Sm = (X[:, None, :] + Q) % 12
    tr = (D == D[:, :, :1]).all(2); inv = (Sm == Sm[:, :, :1]).all(2)
    K = np.stack([tr[:, L:].any(1), inv[:, L:].any(1), tr[:, 1:L].any(1), inv[:, 0] | inv[:, 1:L].any(1)], 1)
    n = K.sum(1); out = np.full(len(X), '', dtype=object)
    for j, name in enumerate(['retrograde', 'RI', 'translation', 'その他']): out[(n == 1) & K[:, j]] = name
    out[n >= 2] = 'multiple'
    return out
if __name__ == "__main__":
    T = collections.defaultdict(collections.Counter)
    for sid, p in phrases_mtc(sys.argv[1]):
        L = len(p)
        if not 4 <= L <= 16: continue
        paths = all_paths(p)
        if len(paths) > CAP: T['skip']['n'] += 1; continue
        b = '4-9' if L <= 9 else '10-16'; H = perms(L)
        o = classes((np.array(p) % 12)[None, :], H)[0]
        cl = classes(np.array(sorted(paths)) % 12, H)
        for t in ('retrograde', 'RI'):
            q = (cl == t).mean(); k = 'q=0' if q == 0 else 'q=1' if q == 1 else '0<q<1'
            T[b, t][k] += 1; T[b, t][k + ' 実際'] += o == t; T[b, t][k + ' 期待'] += q
    for (b, t), s in sorted((k, v) for k, v in T.items() if k != 'skip'):
        print(f"{b:5s} {t:10s} " + '  '.join(f"{k}: {s[k]}本 実際{s[k+' 実際']} 期待{s[k+' 期待']:.1f}" for k in ('q=0', 'q=1', '0<q<1')))
    print('総当たり上限超えで除外', T['skip']['n'])
    import json
    with open('results/ident.json', 'w') as fh:
        json.dump({f'{b}|{t}': dict(c) for (b, t), c in ((k, v) for k, v in T.items() if k != 'skip')}, fh, ensure_ascii=False, indent=1)
