# Analysis plan for the confirmation (Section 4.5)

This is the plan for the confirmation on MTC-FS-INST, as committed before the file was downloaded. It was committed to the author's private working repository (commit `953bc790fab6cf817c64e0e7814dc7dc39290a33`, 2026-11-02 23:26:34 +0900); the local copy of `MTC-FS-INST-2.0_sequences-1.1.jsonl.gz` has the modification time 2026-11-02 23:27:59 +0900. Because that repository is private, this is not a public, independently time-stamped registration.

`two_pal_oe.py` has not been changed since the plan (its last change is 23:25:48 the same evening). `identifiability.py`, from which it imports `all_paths` and `CAP`, was later extended with an interval computation for Section 4.3 that does not touch those two names.

## English translation

Pre-registration: confirmation of result 9 (products of two palindromes) (2026-11-02 23:26, written and committed before opening the data)

- Data: MTC-FS-INST-2.0_sequences-1.1.jsonl.gz from MTCFeatures 1.1 (Zenodo 3551003), not yet opened.
- Analysis: run `two_pal_oe.py`, with the code as of this moment, with arguments `<file> global` (pitch-class judgement without transposition, deduplication within and then across songs, exhaustive transition-preserving null, identifiable subset 0 < q < 1, song-level resampling, the same regression).
- Main hypothesis H1: the regression slope β1 > 0 (lower limit of the song-level 95% interval > 0).
- Secondary hypothesis H2: on the identifiable subset, O/E > 1 for 10–12 and 13–16 notes (judged from the per-band output: point estimates > 1 in both bands and the interval lower limit > 1 in at least one).
- Falsification: if the β1 interval contains zero or the point estimate is zero or below, result 9 is treated as a finding in Essen only, and we write that it was not confirmed.

## Original (Japanese)

```
## 事前登録: 結果9（回文2つの連結）の確認（2026-11-02 23:26、データを開く前に書いてコミットする）
- データ: MTCFeatures 1.1 の MTC-FS-INST-2.0_sequences-1.1.jsonl.gz（Zenodo 3551003、まだ一度も開いていない）
- 解析: two_pal_oe.py をこの時点のコードのまま、引数 `<file> global` で実行（音名・移調なしの判定、曲内→曲間の重複除去、遷移を保つ帰無の総当たり、識別できる部分 0<q<1、曲単位の再標本化、同じ回帰）
- 主仮説 H1: 回帰の β1 > 0（曲単位95%区間の下限 > 0）
- 副仮説 H2: 10–12音と13–16音をまとめた識別できる部分の O/E > 1（その区間は帯ごとの出力で判断し、両帯とも点推定 > 1 かつ少なくとも一方の区間下限 > 1）
- 反証: β1 の区間が0を含む、または点推定が0以下なら、結果9は Essen だけの所見として扱い、確認できなかったと書く
```
