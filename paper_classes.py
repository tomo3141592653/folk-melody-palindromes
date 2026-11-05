# 論文の表2の型(retrograde / RI / inversion / translation / multiple)で、各コーパスの対称なフレーズを数える
import sys, collections
import numpy as np
sys.path.insert(0, '.')
from mtc_loader import phrases_mtc
from census_repro import perms
def kinds(x, H):
    L = len(x); Q = x[H]; D = (x[None, :] - Q) % 12; Sm = (x[None, :] + Q) % 12
    tr = (D == D[:, :1]).all(1); inv = (Sm == Sm[:, :1]).all(1)
    k = set()
    if tr[L:].any(): k.add('retrograde')
    if inv[L:].any(): k.add('RI')
    if inv[0]: k.add('inversion')
    if tr[1:L].any(): k.add('translation')
    if inv[1:L].any(): k.add('回転+反転(表に無い)')
    return k
if __name__ == "__main__":
    c = collections.Counter(); n = 0
    for sid, p in phrases_mtc(sys.argv[1]):
        if not 4 <= len(p) <= 16: continue
        n += 1; k = kinds(np.array(p) % 12, perms(len(p)))
        if k: c[next(iter(k)) if len(k) == 1 else 'multiple'] += 1
    tot = sum(c.values())
    print(f'フレーズ {n}、対称 {tot}（{tot/n:.1%}）')
    for t, v in c.most_common(): print(f'  {t}: {v}（対称のうち {v/tot:.0%}）')
    # 台帳: results/paper_classes_<コーパス名>.json(原稿 4.1 の型の割合はここから)
    import json, os
    name = os.path.basename(sys.argv[1]).split('_sequences')[0].split('.jsonl')[0].lower()
    json.dump({'command': 'paper_classes.py ' + sys.argv[1], 'n': n, 'symmetric': tot, 'classes': dict(c)},
              open(f'results/paper_classes_{name}.json', 'w'), ensure_ascii=False, indent=1)
