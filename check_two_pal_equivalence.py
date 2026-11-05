# 付録A の確認: 3文字・長さ1〜10のすべての列で、「巡回の反転(移調なし)で不変」と「回文2つ(空・1文字を含む)の連結」が一致するか
import itertools
def pal(w): return w == w[::-1]
def refl_inv(x):
    L = len(x)
    return any(all(x[i] == x[(s - i) % L] for i in range(L)) for s in range(L))
def two_pal(x):
    return any(pal(x[:a]) and pal(x[a:]) for a in range(len(x) + 1))
if __name__ == '__main__':
    n = bad = 0
    for L in range(1, 11):
        for x in itertools.product(range(3), repeat=L):
            n += 1; bad += refl_inv(x) != two_pal(x)
    print(n, 'words, disagreements:', bad)
