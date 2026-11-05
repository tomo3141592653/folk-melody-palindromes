# MTC-FS-INST 2.0 の全体（重複除去前）を type 欄で声楽と器楽に分ける。並び順は元のまま。
# 声楽の側には MTC-ANN の 360 曲がそのまま入る（重複除去版は make_disjoint_fsinst.py）
import gzip, json, sys
D = 'data/mtcfeatures/'
if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else D
    outs = {t: gzip.open(out_dir + f'fsinst_{t}.jsonl.gz', 'wt') for t in ('vocal', 'instrumental')}
    n = {t: 0 for t in outs}
    with gzip.open(D + 'MTC-FS-INST-2.0_sequences-1.1.jsonl.gz', 'rt') as fh:
        for line in fh:
            t = json.loads(line).get('type')
            if t in outs: outs[t].write(line); n[t] += 1
    for f in outs.values(): f.close()
    print(n)
