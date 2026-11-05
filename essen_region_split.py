# Essen を曲IDの頭の文字で地域に分けたファイルを作る(data/mtcfeatures/ に置く。配布しない)。
# 中国: han・shanx・natmn・xinhua 等の中国の集、ドイツ語圏: deut・kindr・oestr・suisse、それ以外は作らない
import gzip, json, re, collections
CN = {'han', 'shanx', 'natmn', 'xinhua', 'china'}; DE = {'deut', 'kindr', 'oestr', 'suisse', 'altdeu', 'ballad', 'dva', 'erk', 'boehme', 'zuccal', 'allerkbd', 'fink', 'lothr'}
D = 'data/mtcfeatures/'
if __name__ == '__main__':
    out = {k: gzip.open(D + f'essen_{k}.jsonl.gz', 'wt') for k in ('cn', 'de')}; n = collections.Counter(); other = collections.Counter()
    with gzip.open(D + 'essen_sequences-1.1.jsonl.gz', 'rt') as fh:
        for line in fh:
            g = re.match(r'[a-z]+', json.loads(line)['id']).group(0)
            k = 'cn' if g in CN else 'de' if g in DE else None
            if k: out[k].write(line); n[k] += 1
            else: other[g] += 1
    for f in out.values(): f.close()
    print(dict(n), 'その他', other.most_common())
