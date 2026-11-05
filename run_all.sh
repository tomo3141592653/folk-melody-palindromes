#!/usr/bin/env bash
# 原稿の台帳 results/*.json を全部作り直してから、原稿の数を差し込む。各台帳の command 欄から作った
set -euo pipefail
# 本体を { … exit; } で囲む: 走っている最中に書き換えても、bash は全体を読んでから実行するので段がずれない（run_parallelism.sh で11/4に起きた）
{
cd "$(dirname "$0")"
uv run python audit_sampler_long.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz 200   # -> results/audit_sampler.json
uv run python census_repro.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz 400   # -> results/census_essen.json
uv run python paper_classes_oe.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz 200 exact   # -> results/classes_essen_exact.json
uv run python paper_classes_oe.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz 200 note   # -> results/classes_essen_note.json
uv run python decompose.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz   # -> results/decompose_essen.json
uv run python decompose.py data/mtcfeatures/MTC-ANN-2.0.1_sequences-1.1.jsonl.gz   # -> results/decompose_mtc-ann-2.0.1.json
uv run python disjoint_conditioned.py data/mtcfeatures/fsinst_disjoint.jsonl.gz clean   # -> results/disjoint_clean.json
uv run python disjoint_conditioned.py data/mtcfeatures/fsinst_disjoint.jsonl.gz orig   # -> results/disjoint_orig.json
uv run python disjoint_conditioned.py data/mtcfeatures/fsinst_disjoint.jsonl.gz orig family   # -> results/disjoint_orig_family.json
uv run python disjoint_conditioned.py data/mtcfeatures/fsinst_disjoint.jsonl.gz clean family   # -> results/disjoint_clean_family.json
uv run python decompose.py data/mtcfeatures/MTC-ANN-2.0.1_sequences-1.1.jsonl.gz family   # -> results/decompose_mtc-ann-2.0.1_family.json
uv run python family_concentration.py   # -> results/family_concentration.json
uv run python middle_jump.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz   # -> results/middle_jump_essen.json
uv run python paper_classes.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz   # -> results/paper_classes_essen.json
uv run python paper_classes.py data/mtcfeatures/MTC-ANN-2.0.1_sequences-1.1.jsonl.gz   # -> results/paper_classes_mtc-ann-2.0.1.json
uv run python reversible_by_region.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz   # -> results/region_essen.json
uv run python identifiability.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz 400 dedup-global   # -> results/retro_ident_essen_dedup-global.json
uv run python reversible_doublets.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz   # -> results/reversible_essen.json
uv run python split_position_null.py data/mtcfeatures/MTC-FS-INST-2.0_sequences-1.1.jsonl.gz   # -> results/split_position_mtc-fs-inst-2.0.json
uv run python two_arches.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz   # -> results/two_arches_essen.json
uv run python two_pal_clean.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz   # -> results/two_pal_clean_essen.json
uv run python two_pal_clean.py data/mtcfeatures/MTC-FS-INST-2.0_sequences-1.1.jsonl.gz   # -> results/two_pal_clean_mtc-fs-inst-2.0.json
uv run python mtc_types.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz 200 interval   # -> results/types_essen_interval.json
uv run python ident_by_type.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz   # -> results/ident.json(図2も)
uv run python fig2_identifiability.py
uv run python essen_region_split.py
uv run python two_pal_clean.py data/mtcfeatures/essen_de.jsonl.gz   # -> results/two_pal_clean_essen_de.json
uv run python two_pal_clean.py data/mtcfeatures/essen_cn.jsonl.gz   # -> results/two_pal_clean_essen_cn.json
uv run python two_pal_clean.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz min3   # -> results/two_pal_clean_essen_min3.json
uv run python two_pal_clean.py data/mtcfeatures/fsinst_disjoint.jsonl.gz min3   # -> results/two_pal_clean_fsinst_disjoint_min3.json
uv run python two_pal_clean.py data/mtcfeatures/fsinst_vocal.jsonl.gz min3
uv run python two_pal_clean.py data/mtcfeatures/fsinst_instrumental.jsonl.gz min3
uv run python two_pal_clean.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz nonest
uv run python two_pal_clean.py data/mtcfeatures/fsinst_disjoint.jsonl.gz nonest
uv run python two_pal_clean.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz onlynest
uv run python two_pal_clean.py data/mtcfeatures/fsinst_disjoint.jsonl.gz onlynest
uv run python two_pal_clean.py data/mtcfeatures/fsinst_disjoint.jsonl.gz min3+nonest
uv run python two_pal_clean.py data/mtcfeatures/fsinst_disjoint.jsonl.gz min3+onlynest
uv run python disjoint_conditioned.py data/mtcfeatures/fsinst_disjoint.jsonl.gz orig+nonest
uv run python disjoint_conditioned.py data/mtcfeatures/fsinst_disjoint.jsonl.gz orig+onlynest
uv run python two_pal_clean.py data/mtcfeatures/fsinst_disjoint.jsonl.gz order2+onlynest
uv run python two_pal_clean.py data/mtcfeatures/fsinst_disjoint.jsonl.gz order2+nonest
uv run python two_pal_clean.py data/mtcfeatures/fsinst_disjoint.jsonl.gz order3+onlynest
uv run python two_pal_clean.py data/mtcfeatures/fsinst_disjoint.jsonl.gz order3+nonest
uv run python two_pal_clean.py data/mtcfeatures/fsinst_disjoint.jsonl.gz lrcond+onlynest
uv run python two_pal_clean.py data/mtcfeatures/fsinst_disjoint.jsonl.gz lrcond+nonest
uv run python two_pal_clean.py data/mtcfeatures/fsinst_disjoint.jsonl.gz posrep+onlynest
uv run python two_pal_clean.py data/mtcfeatures/fsinst_disjoint.jsonl.gz posrep+nonest
uv run python two_pal_clean.py data/mtcfeatures/fsinst_disjoint.jsonl.gz per
uv run python two_pal_clean.py data/mtcfeatures/fsinst_disjoint.jsonl.gz min3+per
uv run python two_pal_clean.py data/mtcfeatures/fsinst_disjoint.jsonl.gz min3+noper
uv run python two_pal_clean.py data/mtcfeatures/fsinst_disjoint.jsonl.gz noper
uv run python two_pal_clean.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz per
uv run python two_pal_clean.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz noper
uv run python two_pal_clean.py data/mtcfeatures/fsinst_disjoint.jsonl.gz beat+onlynest
uv run python two_pal_clean.py data/mtcfeatures/fsinst_disjoint.jsonl.gz beat+nonest
uv run python two_pal_clean.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz beat+onlynest
uv run python two_pal_clean.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz beat+nonest
uv run python aa_share.py
uv run python periodic_oe.py data/mtcfeatures/fsinst_disjoint.jsonl.gz
uv run python periodic_oe.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz
uv run python unit_cyclic.py data/mtcfeatures/fsinst_disjoint.jsonl.gz
uv run python unit_cyclic.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz
uv run python paired_posrep_lrcond.py data/mtcfeatures/fsinst_disjoint.jsonl.gz nonest
uv run python paired_posrep_lrcond.py data/mtcfeatures/fsinst_disjoint.jsonl.gz onlynest
uv run python repetition_oe.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz
uv run python repetition_oe.py data/mtcfeatures/fsinst_disjoint.jsonl.gz
uv run python build_ledger_two_pal.py   # -> results/two_pal.json(声楽・器楽を含む)
uv run python data_counts.py
uv run python fig1_two_pal.py
uv run python fig3_examples.py
uv run python fig4_nested.py
uv run python fig4_periodic.py
uv run python decomp_periodic.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz   # -> results/decomp_periodic_essen.json（査読11/5: 同じ集合で周期的/非周期的に分けて O−E の和を確かめる）
uv run python decomp_periodic.py data/mtcfeatures/fsinst_disjoint.jsonl.gz
uv run python decomp_periodic.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz min3
uv run python decomp_periodic.py data/mtcfeatures/fsinst_disjoint.jsonl.gz min3
uv run python decomp_periodic.py data/mtcfeatures/essen_sequences-1.1.jsonl.gz reg   # 登録時の定義（除外なし）
uv run python decomp_periodic.py data/mtcfeatures/fsinst_disjoint.jsonl.gz reg
uv run python decomp_noper_source.py data/mtcfeatures/fsinst_disjoint.jsonl.gz > /dev/null   # 非周期的の不足の出どころ（本文には数を出していない）
uv run python paper_numbers.py
exit
}
