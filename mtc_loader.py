# MTCFeatures の jsonl.gz からフレーズ(midipitch の並び)を (曲ID, 音高リスト) で返す。論文に合わせ 4≤L≤16 は使う側で絞る
import gzip, json, itertools
def phrases_mtc(path):
    with gzip.open(path, 'rt') as fh:
        for line in fh:
            d = json.loads(line); f = d['features']
            for ix, grp in itertools.groupby(zip(f['phrase_ix'], f['midipitch']), key=lambda t: t[0]):
                yield d['id'], [p for _, p in grp]
