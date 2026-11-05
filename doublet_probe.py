# 試し: 回文フレーズごとに、隣接2音の組の出現数と最初の音を保った並べ替え(オイラー路)を全部数え、
# そのうち回文になるものの割合を出す。大きすぎる場合は上限で打ち切る。検定ではなく見当をつけるため
import sys, glob, collections
sys.path.insert(0, '.')
from count_phrases import midi
def phrases_of(root):
    for f in sorted(glob.glob(root + '/**/*.krn', recursive=True)):
        cur = None
        for line in open(f, encoding='latin-1'):
            if line.startswith(('!', '*', '=')): continue
            tok = line.split('\t')[0].strip()
            if not tok or tok == '.': continue
            if '{' in tok: cur = []
            if 'r' not in tok and cur is not None:
                p = midi(tok)
                if p is not None and '_' not in tok and ']' not in tok: cur.append(p)
            if '}' in tok and cur is not None:
                yield f, cur; cur = None
CAP = 20000
def euler_paths(p):
    edges = collections.Counter(zip(p, p[1:]))
    out, n = [0, 0], len(p)
    seq = [p[0]]
    def dfs(u):
        if out[0] >= CAP: return
        if len(seq) == n:
            out[0] += 1; out[1] += seq == seq[::-1]; return
        for (a, b), c in list(edges.items()):
            if a == u and c > 0:
                edges[(a, b)] -= 1; seq.append(b); dfs(b); seq.pop(); edges[(a, b)] += 1
    dfs(p[0]); return out
if __name__ == "__main__":
    rows = []
    for f, p in phrases_of(sys.argv[1]):
        if len(p) >= 5 and p == p[::-1] and len(set(p)) > 1:
            tot, pal = euler_paths(p)
            rows.append((len(p), tot, pal, f.split('essen/')[1]))
    rows.sort()
    byL = collections.defaultdict(list)
    for L, tot, pal, f in rows: byL[L].append(pal / tot)
    print('回文(同音反復だけのものを除く):', len(rows), '本')
    for L in sorted(byL):
        v = byL[L]; print(f'{L:2d}音 {len(v):3d}本  並べ替えの中の回文の割合 平均 {sum(v)/len(v):.2f}  1.0(=強制)の本数 {sum(x == 1 for x in v)}')
    print('打ち切り(上限到達):', sum(t >= CAP for _, t, _, _ in rows))
