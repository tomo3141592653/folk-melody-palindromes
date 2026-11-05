# 重複のない FS-INST で、clean の定義の入れ子の回文2つの連結として観測された句のうち AA(前半と後半が音高ごと同じ)の数を数える。台帳 results/aa_share_fsinst_disjoint.json
# 回文2つの連結から、①片方が1種類の音だけの分割、②2つの部分が同じ長さで音階の段数(diatonicpitch)の差が一定=全音階で移したくり返し の分割を除いた判定で、
# 実際と「遷移を保つ並べ替え」(総当たり)を比べる。並べ替えた列の段数は、そのフレーズの中の 音高→段数 の対応から引く。曲内→曲間の重複除去、識別できる部分、曲単位の区間と長さの回帰
import sys, gzip, json, itertools, collections, random
import numpy as np
from scipy.optimize import minimize
sys.path.insert(0, '.')
from identifiability import all_paths, CAP
def pal(y): return y == y[::-1]
# 第2引数は '+' でつないだ選択肢(例 min3+nonest)。min3: さらに両方の部分が3種類以上の音(2音の行き来を除く)。回文に入る音の種類は高々⌈n/2⌉なので10音以上だけ
# order2 / order3: 帰無を「隣り合う3音(4音)の組の数と最初の2音(3音)を保つ並べ替え」にする
# posrep: さらに、そのくり返しの位置まで実際と同じ列に絞る
# lrcond: 帰無を「最長のくり返しの長さが実際と同じ列」に絞る(くり返しの量を条件にする)
# nonest / onlynest: 片方の部分がもう片方の連続した一部(音名そのまま、移調なし)になっている分割=入れ子(部分的なくり返し)を除く / それだけを数える
OPTS = {'onlynest'}
MIN3 = 'min3' in OPTS
MAXN = 2 if MIN3 else 1
def longest_repeat(y):
    for m in range(len(y) - 1, 0, -1):
        c = collections.Counter(y[i:i + m] for i in range(len(y) - m + 1))
        if max(c.values()) > 1: return m
    return 0
def nested(a, b):
    a, b = (a, b) if len(a) >= len(b) else (b, a)
    return any(tuple(a[i:i + len(b)]) == tuple(b) for i in range(len(a) - len(b) + 1))
def two_pal_clean(x, dp):
    L = len(x)
    if pal(x): return False
    for k in range(2, L - 1):
        if not (pal(x[:k]) and pal(x[k:])): continue
        if len(set(x[:k])) <= MAXN or len(set(x[k:])) <= MAXN: continue
        if 2 * k == L and len({b - a for a, b in zip(dp[:k], dp[k:])}) == 1: continue
        if 'nonest' in OPTS and nested(x[:k], x[k:]): continue
        if 'onlynest' in OPTS and not nested(x[:k], x[k:]): continue
        return True
    return False

import gzip, itertools, json, collections
cnt=collections.Counter(); seen=set()
with gzip.open('data/mtcfeatures/fsinst_disjoint.jsonl.gz','rt') as fh:
    for line in fh:
        d=json.loads(line); f=d['features']
        for _,grp in itertools.groupby(zip(f['phrase_ix'],f['midipitch'],f['diatonicpitch']),key=lambda t:t[0]):
            g=list(grp); p=[m for _,m,_ in g]; L=len(p)
            if not 10<=L<=16: continue
            key=tuple(y-x for x,y in zip(p,p[1:]))
            if key in seen: continue
            seen.add(key)
            m2d={m:dd for _,m,dd in g}
            if two_pal_clean(tuple(v%12 for v in p),[m2d[v] for v in p]):
                b='10-12' if L<=12 else '13-16'
                aa = L%2==0 and p[:L//2]==p[L//2:]
                cnt[(b,aa)]+=1
res={b:{'observed':cnt[(b,True)]+cnt[(b,False)],'aa':cnt[(b,True)]} for b in ('10-12','13-16')}
print(res)
json.dump({'command':'aa_share.py','note':'clean の入れ子の回文2つの連結として観測された句(重複除去後、識別の条件なし)のうち、前半と後半が音高ごと同じ(AA)句の数','bands':res},open('results/aa_share_fsinst_disjoint.json','w'),ensure_ascii=False,indent=1)
