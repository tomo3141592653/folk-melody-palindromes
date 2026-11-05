# 確認用データから既使用データとの重複を除いた版を作る: MTC-ANN と同じ曲IDの曲を丸ごと除き、
# 残りの曲から Essen か MTC-ANN と音程列(移調不変)が一致するフレーズ(4≤L≤16)の音を取り除く。特徴の列はすべて同じ位置で切る
import gzip, json, itertools
D = 'data/mtcfeatures/'
def phrase_keys(path):
    ks = set(); ids = set()
    with gzip.open(path, 'rt') as fh:
        for line in fh:
            d = json.loads(line); f = d['features']; ids.add(d['id'])
            for _, grp in itertools.groupby(zip(f['phrase_ix'], f['midipitch']), key=lambda t: t[0]):
                p = [m for _, m in grp]
                if 4 <= len(p) <= 16: ks.add(tuple(b - a for a, b in zip(p, p[1:])))
    return ks, ids
if __name__ == "__main__":
    ann_k, ann_ids = phrase_keys(D + 'MTC-ANN-2.0.1_sequences-1.1.jsonl.gz')
    es_k, _ = phrase_keys(D + 'essen_sequences-1.1.jsonl.gz')
    used = ann_k | es_k; n_song = n_drop = n_keep = 0
    with gzip.open(D + 'MTC-FS-INST-2.0_sequences-1.1.jsonl.gz', 'rt') as fh, gzip.open(D + 'fsinst_disjoint.jsonl.gz', 'wt') as out:
        for line in fh:
            d = json.loads(line)
            if d['id'] in ann_ids: continue
            f = d['features']; n = len(f['midipitch']); keep = [True] * n; i = 0
            for _, grp in itertools.groupby(range(n), key=lambda j: f['phrase_ix'][j]):
                idx = list(grp); p = [f['midipitch'][j] for j in idx]
                if 4 <= len(p) <= 16 and tuple(b - a for a, b in zip(p, p[1:])) in used:
                    for j in idx: keep[j] = False
                    n_drop += 1
                else: n_keep += 1
            d['features'] = {k: [v[j] for j in range(n) if keep[j]] if isinstance(v, list) and len(v) == n else v for k, v in f.items()}
            out.write(json.dumps(d) + '\n'); n_song += 1
    print('残した曲', n_song, '取り除いたフレーズ', n_drop, '残したフレーズ', n_keep)
