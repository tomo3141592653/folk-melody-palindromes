# 隣接2音の組の数と最初・最後の音を保つ並べ替え(オイラー路)を一様に引く(Kandel ほか 1996 の方法)。
# 終点 t へ向かう「各頂点の最後の出辺」の全域木を Wilson のアルゴリズムで一様に選び、残りの出辺を混ぜて並べる
import random, collections
def sample(p, rng=random):
    out = collections.defaultdict(list)
    for a, b in zip(p, p[1:]): out[a].append(b)
    t = p[-1]
    last = {}; in_tree = {t}
    for v in list(out):
        u = v
        while u not in in_tree:          # 出辺をたどる乱歩、ループ消去は last の上書きで行う
            last[u] = rng.randrange(len(out[u])); u = out[u][last[u]]
        u = v
        while u not in in_tree:
            in_tree.add(u); u = out[u][last[u]]
    order = {}
    for v, nb in out.items():
        rest = [b for i, b in enumerate(nb) if i != last.get(v, -1)]
        rng.shuffle(rest)
        order[v] = rest + ([nb[last[v]]] if v in last else [])
    seq, u, ptr = [p[0]], p[0], collections.Counter()
    while ptr[u] < len(order.get(u, [])):
        nxt = order[u][ptr[u]]; ptr[u] += 1; seq.append(nxt); u = nxt
    assert len(seq) == len(p), '路が途中で切れた'
    return seq
def q_hat(p, n=4000, rng=random):
    return sum(s == s[::-1] for s in (sample(p, rng) for _ in range(n))) / n
if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    from doublet_probe import phrases_of, euler_paths
    rng = random.Random(1); k = 0
    for f, p in phrases_of(sys.argv[1]):
        if 8 <= len(p) <= 12 and len(set(p)) > 2:
            tot, pal = euler_paths(p)
            if tot < 2: continue
            print(len(p), f'総当たり q={pal/tot:.3f} (路{tot}本)  サンプリング q={q_hat(p, 4000, rng):.3f}')
            k += 1
            if k >= 8: break
