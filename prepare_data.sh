#!/usr/bin/env bash
# Download MTCFeatures 1.1 into data/mtcfeatures/ and build the derived files read by run_all.sh.
# The corpora are not redistributed in this repository (CC BY-NC-SA 3.0, see data/mtcfeatures/LICENCE_Data).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p data/mtcfeatures
Z=https://zenodo.org/api/records/3551003/files   # MTCFeatures 1.1, doi:10.5281/zenodo.3551003
for f in essen_sequences-1.1.jsonl.gz MTC-ANN-2.0.1_sequences-1.1.jsonl.gz MTC-FS-INST-2.0_sequences-1.1.jsonl.gz; do
  [ -f data/mtcfeatures/$f ] || curl -L -o data/mtcfeatures/$f "$Z/$f/content"
done
curl -sL -o data/mtcfeatures/LICENCE_Data "$Z/LICENCE_Data/content"
md5sum -c - <<'MD5'
c9290572aefb97af60b206775d050876  data/mtcfeatures/essen_sequences-1.1.jsonl.gz
1a15615a4f7222702276565a0253e329  data/mtcfeatures/MTC-ANN-2.0.1_sequences-1.1.jsonl.gz
2c5ef01870e9e202df392fed5b34b061  data/mtcfeatures/MTC-FS-INST-2.0_sequences-1.1.jsonl.gz
MD5
# derived files
python3 essen_region_split.py        # -> essen_de, essen_cn
python3 make_disjoint_fsinst.py      # -> fsinst_disjoint (MTC-FS-INST minus MTC-ANN songs and phrases shared with Essen/MTC-ANN)
python3 make_vocal_instrumental.py   # -> fsinst_vocal, fsinst_instrumental (full MTC-FS-INST split by type)
# check the uncompressed content of the derived files (gzip headers carry a timestamp, so compare after zcat)
while read -r h f; do
  got=$(zcat data/mtcfeatures/$f.jsonl.gz | sha256sum | cut -c1-64)
  [ "$got" = "$h" ] && echo "$f OK" || { echo "$f MISMATCH"; exit 1; }
done <<'SHA'
6ffaa079648f85dfed949d4567b12deacd9b687da631db5e17937524bedab94a essen_de
5e0930f37d5ef23f843dbc934d6d225f791d5221733ed082d693a6c832fcbb10 essen_cn
1e73f1e418a2e64b9df7032fcd47c64f9e5814272e2fb6ecaa26fd03974b5d97 fsinst_disjoint
ecb792136cd998b9970de6260620973445ba669bee6a846e35c624827d7938cd fsinst_vocal
5f9f0e6825d006bcda99c0095ff84505a866a3bcc213398a78de5e78d0a3cd4a fsinst_instrumental
SHA
