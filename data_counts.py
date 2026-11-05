# 原稿 2章(データ)の数の台帳: 各ファイルの曲数・4〜16音のフレーズ数・SHA-256 の先頭16桁、MTC-FS-INST に入っている MTC-ANN の曲数
import gzip, json, hashlib, sys
sys.path.insert(0, '.')
from mtc_loader import phrases_mtc
from identifiability import all_paths, CAP
D = 'data/mtcfeatures/'
FILES = {'essen': 'essen_sequences-1.1.jsonl.gz', 'mtc-ann': 'MTC-ANN-2.0.1_sequences-1.1.jsonl.gz', 'fsinst': 'MTC-FS-INST-2.0_sequences-1.1.jsonl.gz',
         'fsinst_vocal': 'fsinst_vocal.jsonl.gz', 'fsinst_instrumental': 'fsinst_instrumental.jsonl.gz', 'fsinst_disjoint': 'fsinst_disjoint.jsonl.gz'}
def families(f):
    with gzip.open(D + f, 'rt') as fh: return len({json.loads(l).get('tunefamily') for l in fh} - {None, ''})
def ids(f):
    with gzip.open(D + f, 'rt') as fh: return [json.loads(l)['id'] for l in fh]
if __name__ == '__main__':
    out = {}
    for k, f in FILES.items():
        # Zenodo から取った元ファイルはファイルそのもの、作り直す派生データは展開した中身で取る（gzip のヘッダーには作った時刻が入るため。11/5 まっさらな写しの再現で判明）
        h = {'sha256_16': hashlib.sha256(open(D + f, 'rb').read()).hexdigest()[:16]} if k in ('essen', 'mtc-ann', 'fsinst') else \
            {'content_sha256_16': hashlib.sha256(gzip.open(D + f, 'rb').read()).hexdigest()[:16]}
        out[k] = {'file': f, **h,
                  'tunes': len(ids(f)), 'families': families(f), 'phrases_4_16': sum(4 <= len(p) <= 16 for _, p in phrases_mtc(D + f))}
    for k in ('essen', 'mtc-ann', 'fsinst'):   # 総当たりできない(異なる音列が CAP を超える)フレーズの本数。重複除去前
        out[k]['over_cap'] = sum(len(all_paths(p)) > CAP for _, p in phrases_mtc(D + FILES[k]) if 4 <= len(p) <= 16)
    out['cap'] = CAP
    out['ann_in_fsinst'] = len(set(ids(FILES['mtc-ann'])) & set(ids(FILES['fsinst'])))
    out['disjoint_removed_phrases'] = out['fsinst']['phrases_4_16'] - out['fsinst_disjoint']['phrases_4_16']
    json.dump(out, open('results/data_counts.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))
