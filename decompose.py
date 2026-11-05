# 真ん中の軸の回文(音高そのもの)の、音の並べ替えに対する O/E を3つの積に分ける(恒等式):
#   O/E_note = [N_rev / E_rev_note] × [(Σ_{可逆} q / N_rev) / (E_pal_note / E_rev_note)] × [O / Σ_{可逆} q]
#   第1項: 可逆なフレーズの多さ  第2項: 可逆なものの中での回文の作りやすさ(実際の遷移で並べ替え vs 音の並べ替えで可逆になった列)
#   第3項: 2音の組を保つ並べ替えに対する O/E。曲内重複除去
import sys, collections
import numpy as np
sys.path.insert(0, '.')
from mtc_loader import phrases_mtc
from identifiability import all_paths, CAP
from euler_sample import q_hat
from reversible_vs_shuffle import rev
BANDS = [(4, 6), (7, 9), (10, 12), (13, 16)]
rng = np.random.default_rng(0); S = 400
st = collections.defaultdict(collections.Counter); seen = set(); rows = []
for sid, p in phrases_mtc(sys.argv[1]):
    L = len(p); b = next((k for k in BANDS if k[0] <= L <= k[1]), None)
    if b is None or (sid, tuple(p)) in seen: continue
    seen.add((sid, tuple(p)))
    s = st[b]; s['O'] += p == p[::-1]; row = {'sid': sid, 'b': b, 'O': int(p == p[::-1]), 'N_rev': 0, 'Sq': 0.0}
    sh = rng.permuted(np.tile(np.array(p), (S, 1)), axis=1)
    s['E_rev'] += sum(rev(list(x)) for x in sh) / S
    s['E_pal'] += (sh == sh[:, ::-1]).all(1).mean()
    row['E_rev'] = sum(rev(list(x)) for x in sh) / S; row['E_pal'] = (sh == sh[:, ::-1]).all(1).mean()
    if rev(p):
        s['N_rev'] += 1
        paths = all_paths(p)
        q = (sum(x == x[::-1] for x in paths) / len(paths)) if len(paths) <= CAP else q_hat(p, 2000)
        s['Sq'] += q; row['N_rev'] = 1; row['Sq'] = q
    rows.append(row)
UNIT = sys.argv[2] if len(sys.argv) > 2 else 'song'   # 区間の再標本化の単位: song か family(tunefamily。無い曲は1曲で1つ)
if UNIT == 'family':
    import gzip, json as _j
    fam = {}
    with gzip.open(sys.argv[1], 'rt') as fh:
        for line in fh:
            d = _j.loads(line); fam[d['id']] = d.get('tunefamily') or 'song:' + d['id']
    for r in rows: r['sid'] = fam[r['sid']]
led = {}
for b in BANDS:
    s = st[b]
    if not (s['E_rev'] and s['N_rev'] and s['Sq'] and s['E_pal']):
        print(f"{b[0]}-{b[1]}音 回文 {s['O']} 可逆 {s['N_rev']} | 本数が足りず分解できない"); continue
    f1 = s['N_rev'] / s['E_rev']; f2 = (s['Sq'] / s['N_rev']) / (s['E_pal'] / s['E_rev']); f3 = s['O'] / s['Sq']
    led[f'{b[0]}-{b[1]}'] = {'n_pal': s['O'], 'oe_note': s['O'] / s['E_pal'], 'f1': f1, 'f2': f2, 'f3': f3}
    print(f"{b[0]}-{b[1]}音 回文 {s['O']} | O/E_note {s['O']/s['E_pal']:.2f} = 可逆の多さ {f1:.2f} × 可逆内の作りやすさ {f2:.2f} × 遷移保存の O/E {f3:.2f}  (積 {f1*f2*f3:.2f})")

# 曲単位の再標本化で3因子と O/E_note の95%区間(1000回)
import random
by = collections.defaultdict(list)
for r in rows: by[r['sid']].append(r)
songs = list(by); rr = random.Random(0)
def factors(sel, b):
    t = collections.Counter()
    for sg in sel:
        for r in by[sg]:
            if r['b'] == b:
                for k in ('O', 'N_rev', 'Sq', 'E_rev', 'E_pal'): t[k] += r[k]
    if not (t['E_rev'] and t['N_rev'] and t['Sq'] and t['E_pal']): return None
    return (t['O'] / t['E_pal'], t['N_rev'] / t['E_rev'], (t['Sq'] / t['N_rev']) / (t['E_pal'] / t['E_rev']), t['O'] / t['Sq'])
for b in BANDS:
    bs = [f for f in (factors([rr.choice(songs) for _ in songs], b) for _ in range(1000)) if f]
    if len(bs) < 900: print(f'{b[0]}-{b[1]}音 区間を出せない'); continue
    ci = [sorted(x)[int(.025 * len(x))] for x in zip(*bs)], [sorted(x)[int(.975 * len(x)) - 1] for x in zip(*bs)]
    led[f'{b[0]}-{b[1]}']['ci'] = {k: [ci[0][i], ci[1][i]] for i, k in enumerate(('oe_note', 'f1', 'f2', 'f3'))}
    print(f'{b[0]}-{b[1]}音 区間 O/E_note [{ci[0][0]:.2f},{ci[1][0]:.2f}] 可逆の多さ [{ci[0][1]:.2f},{ci[1][1]:.2f}] 作りやすさ [{ci[0][2]:.2f},{ci[1][2]:.2f}] 遷移保存 [{ci[0][3]:.2f},{ci[1][3]:.2f}]')
# 台帳: results/decompose_<コーパス名>.json(原稿 4.4 はここから)
import json, os
name = os.path.basename(sys.argv[1]).split('_sequences')[0].split('.jsonl')[0].lower()
json.dump({'command': 'decompose.py ' + ' '.join(sys.argv[1:]), 'unit': UNIT, 'S': S, 'bands': led}, open(f'results/decompose_{name}' + ('' if UNIT == 'song' else f'_{UNIT}') + '.json', 'w'), ensure_ascii=False, indent=1)
