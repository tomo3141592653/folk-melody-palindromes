# 図1・本文の「回文2つの連結」の数字の台帳を作る: 3つの解析を走らせ、出力の行から O/E・区間・β1 を読み取って results/two_pal.json へ
import subprocess, re, json, sys
RUNS = {
    'essen': ['two_pal_oe.py', 'data/mtcfeatures/essen_sequences-1.1.jsonl.gz', 'global'],
    'fsinst_prespecified': ['two_pal_oe.py', 'data/mtcfeatures/MTC-FS-INST-2.0_sequences-1.1.jsonl.gz', 'global'],
    'fsinst_disjoint_conditioned': ['disjoint_conditioned.py', 'data/mtcfeatures/fsinst_disjoint.jsonl.gz', 'orig'],
    'fsinst_vocal': ['two_pal_oe.py', 'data/mtcfeatures/fsinst_vocal.jsonl.gz', 'global'],
    'fsinst_instrumental': ['two_pal_oe.py', 'data/mtcfeatures/fsinst_instrumental.jsonl.gz', 'global'],
    'essen_de': ['two_pal_oe.py', 'data/mtcfeatures/essen_de.jsonl.gz', 'global'],   # essen_region_split.py で作る
    'essen_cn': ['two_pal_oe.py', 'data/mtcfeatures/essen_cn.jsonl.gz', 'global'],
}
band_re = re.compile(r'^(\d+)-(\d+)音 .*?O/E (?:\d+/[\d.]+=)?([\d.]+) 曲単位95%区間 \[([\d.]+), ([\d.]+)\]')
beta_re = re.compile(r'β1=(-?[\d.]+).*?\[(-?[\d.]+), (-?[\d.]+)\]')
ledger = {}
for name, args in RUNS.items():
    out = subprocess.run([sys.executable, '-I'] + args,
                         capture_output=True, text=True, check=True).stdout
    bands = {}
    for line in out.splitlines():
        m = band_re.match(line)
        if m and ('識別できる部分 O/E' in line or name == 'fsinst_disjoint_conditioned'):
            bands[f'{m.group(1)}-{m.group(2)}'] = {'oe': float(m.group(3)), 'lo': float(m.group(4)), 'hi': float(m.group(5))}
    b = beta_re.search(out)
    ledger[name] = {'command': ' '.join(args), 'bands': bands, 'beta1': {'est': float(b.group(1)), 'lo': float(b.group(2)), 'hi': float(b.group(3))}}
    assert len(bands) == 4, (name, bands)
with open('results/two_pal.json', 'w') as fh: json.dump(ledger, fh, ensure_ascii=False, indent=1)
print(json.dumps({k: (v['bands']['13-16'], v['beta1']) for k, v in ledger.items()}, ensure_ascii=False))
