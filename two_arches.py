# 10–16音で論文の retrograde 型になるフレーズを、ふつうの回文 / 2つに切るとそれぞれが回文(音名) / その他 に分ける。重複除去なし
import sys, collections
import numpy as np
sys.path.insert(0, '.')
from mtc_loader import phrases_mtc
from census_repro import perms
from ident_by_type import classes
def pal(x): return len(x) >= 2 and all(a == b for a, b in zip(x, x[::-1]))
c = collections.Counter(); ex = []
for sid, p in phrases_mtc(sys.argv[1]):
    L = len(p)
    if not 10 <= L <= 16: continue
    x = [v % 12 for v in p]
    if classes(np.array(x)[None, :], perms(L))[0] != 'retrograde': continue
    if pal(x): c['ふつうの回文'] += 1
    elif any(pal(x[:k]) and pal(x[k:]) for k in range(2, L - 1)): c['2つの回文の並び'] += 1
    else:
        c['その他'] += 1
        if len(ex) < 4: ex.append(sid + ' ' + ' '.join(map(str, x)))
print(dict(c)); print('\n'.join(ex))
# 台帳: results/two_arches_<コーパス名>.json(原稿 4.5 と付録A の 282・191・16 はここから)
import json, os
name = os.path.basename(sys.argv[1]).split('_sequences')[0].split('.jsonl')[0].lower()
json.dump({'command': 'two_arches.py ' + sys.argv[1], 'retrograde_10_16': sum(c.values()), **dict(c)},
          open(f'results/two_arches_{name}.json', 'w'), ensure_ascii=False, indent=1)
