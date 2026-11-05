# 起点論文(2610.40303)の census の再現: 音名の並びを長さLの巡回列とみて、D12(移調・反転)×DL(巡回シフト・逆行)の
# 恒等でない元で自分に重なるか(=対称)。帰無モデルは各フレーズの音の並べ替え(p_i はモンテカルロ)。長さ帯ごとに O/E
import sys, collections
import numpy as np
sys.path.insert(0, '.')
from doublet_probe import phrases_of
from mtc_loader import phrases_mtc
def perms(L):
    i = np.arange(L)
    hs = [((i + s) % L) for s in range(L)] + [((s - i) % L) for s in range(L)]
    return np.array(hs)          # 0番目が恒等
def symmetric(X, H):
    """X: (S, L) の音名。各行が恒等でない (g, h) で不変なら True"""
    Q = X[:, H]                  # (S, 2L, L) : 位置を h で並べ替えた列
    D = (X[:, None, :] - Q) % 12 # 移調: p - q が一定
    Sm = (X[:, None, :] + Q) % 12  # 反転: p + q が一定
    tr = (D == D[:, :, :1]).all(2); inv = (Sm == Sm[:, :, :1]).all(2)
    tr[:, 0] = False             # h=恒等 で移調が一定なのは移調量0の恒等変換だけなので除く(反転は残す)
    return (tr | inv).any(1)
BANDS = [(4, 6), (7, 9), (10, 12), (13, 16)]
def main():
  S = int(sys.argv[2]) if len(sys.argv) > 2 else 400
  rng = np.random.default_rng(0)
  O = collections.Counter(); E = collections.Counter(); N = collections.Counter()
  src = phrases_mtc(sys.argv[1]) if sys.argv[1].endswith('.jsonl.gz') else phrases_of(sys.argv[1])  # MTCFeatures か CCARH の krn
  for f, p in src:
      L = len(p)
      if not 4 <= L <= 16: continue
      b = next(k for k in BANDS if k[0] <= L <= k[1])
      x = np.array(p) % 12; H = perms(L)
      O[b] += bool(symmetric(x[None, :], H)[0]); N[b] += 1
      sh = rng.permuted(np.tile(x, (S, 1)), axis=1)
      E[b] += symmetric(sh, H).mean()
  for b in BANDS:
      print(f'{b[0]}-{b[1]}音 フレーズ{N[b]:6d} 対称{O[b]:5d}({O[b]/N[b]:.1%}) 期待{E[b]:8.1f} O/E {O[b]/E[b]:.2f}')
  # 台帳: results/census_<コーパス名>.json(原稿 4.1 の数はここから)
  import json, os
  name = os.path.basename(sys.argv[1]).split('_sequences')[0].split('.jsonl')[0].lower()
  json.dump({'command': 'census_repro.py ' + ' '.join(sys.argv[1:]), 'S': S,
             'bands': {f'{b[0]}-{b[1]}': {'N': N[b], 'O': O[b], 'E': E[b], 'oe': O[b] / E[b]} for b in BANDS}},
            open(f'results/census_{name}.json', 'w'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
