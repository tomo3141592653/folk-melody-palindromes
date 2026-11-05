# Essen 民謡集のフレーズ長と、音高の完全な回文（逆から読んでも同じ）の数を数える。規模の確認用で検定ではない
import re, sys, glob, collections
PC = {'c':0,'d':2,'e':4,'f':5,'g':7,'a':9,'b':11}
def midi(tok):
    m = re.search(r'([a-gA-G]+)(#*|-*)', tok)
    if not m or 'r' in tok.split()[0][:3] and not m: return None
    letters, acc = m.group(1), m.group(2)
    base = PC[letters[0].lower()]
    octv = 4 + (len(letters)-1) if letters[0].islower() else 3 - (len(letters)-1)
    return 12*(octv+1) + base + acc.count('#') - acc.count('-')
if __name__ == "__main__":
    phrases = []
    for f in glob.glob(sys.argv[1] + '/**/*.krn', recursive=True):
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
                phrases.append(cur); cur = None
    L = collections.Counter(len(p) for p in phrases)
    print('フレーズ数', len(phrases))
    print('長さ 13〜16 音:', sum(L[n] for n in range(13, 17)))
    pal = [p for p in phrases if len(p) >= 5 and p == p[::-1]]
    print('音高の完全回文（5音以上）:', len(pal), ' うち13〜16音:', sum(13 <= len(p) <= 16 for p in pal))
    print('長さ別の回文:', sorted(collections.Counter(len(p) for p in pal).items()))
