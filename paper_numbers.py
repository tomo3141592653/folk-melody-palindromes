"""原稿 paper_en.md の本文の数を台帳 results/*.json から埋める。
本文の数には印 <!--n:名前-->値<!--/n--> を付け、values() に名前を足す。印の付いていない数は [L] のまま残し、台帳ができたら印に替える。
変わった値と、印はあるが values() に無い名前を表示する。使い方: uv run python paper_numbers.py(scipy を使う)
"""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
PAPER = HERE / 'paper_en.md'
def load(name): return json.loads((HERE / 'results' / name).read_text())
def ci(b): return f"{b['oe']:.2f} [{b['lo']:.2f}, {b['hi']:.2f}]"
def beta(b): return f"{b['est']:.3f} [{b['lo']:.3f}, {b['hi']:.3f}]"
def power(E, alpha=0.05, beta=0.8):
    """期待本数 E のポアソンで、片側 alpha の検定が確率 beta で検出できる最小の倍率"""
    from scipy.stats import poisson
    c = int(poisson.isf(alpha, E)) + 1   # P(X >= c) <= alpha となる最小の c
    while poisson.sf(c - 1, E) > alpha: c += 1
    r = 1.0
    while poisson.sf(c - 1, r * E) < beta: r += 0.001
    return r
def values():
    v = {}
    r = load('ident.json')['4-9|retrograde']
    tot = r['q=0'] + r['q=1'] + r['0<q<1']
    obs = r['q=1 実際'] + r['0<q<1 実際']
    v['ident49_total'] = f'{tot:,}'
    ex = load('classes_essen_exact.json')['cells']
    v['cl_retro'] = f"{oe(ex, '4-9|retrograde'):.2f} and {oe(ex, '10-16|retrograde'):.2f}"
    v['cl_ri'] = f"{oe(ex, '4-9|RI'):.2f} and {oe(ex, '10-16|RI'):.2f}"
    v['cl_tr'] = f"{oe(ex, '4-9|translation'):.2f} and {oe(ex, '10-16|translation'):.2f}"
    v['cl_mu'] = f"{oe(ex, '4-9|multiple'):.2f} and {oe(ex, '10-16|multiple'):.2f}"
    v['cl_exact_n'] = f"{sum(load('classes_essen_exact.json')['n_exact'].values()):,}"
    v['ident49_q0'] = f"{r['q=0']:,}"
    v['ident49_q1'] = f"{r['q=1']:,}"
    v['ident49_mid'] = f"{r['0<q<1']:,}"
    v['ident49_q1_share'] = f"{100 * r['q=1'] / obs:.0f}%"
    v['ident49_retro_obs'] = f'{obs:,}'
    t = load('two_pal.json')
    e = t['essen']
    v['tp_essen_oe'] = ', '.join(f"{e['bands'][k]['oe']:.2f}" for k in ['4-6', '7-9', '10-12']) + f" and {e['bands']['13-16']['oe']:.2f}"
    v['tp_essen_beta'] = beta(e['beta1'])
    f = t['fsinst_prespecified']
    v['tp_fs_beta'] = beta(f['beta1']); v['tp_fs_1012'] = ci(f['bands']['10-12']); v['tp_fs_1316'] = ci(f['bands']['13-16'])
    d = t['fsinst_disjoint_conditioned']
    v['tp_dj_beta'] = beta(d['beta1']); v['tp_dj_1012'] = ci(d['bands']['10-12']); v['tp_dj_1316'] = ci(d['bands']['13-16'])
    rv = load('reversible_essen.json')['bands']
    sh = [f"{100 * rv[k]['条件'] / rv[k]['N']:.1f}%" for k in ['4-6', '7-9', '10-12', '13-16']]
    v['rev_essen_share'] = ', '.join(sh[:3]) + ' and ' + sh[3]
    assert all(rv[k]['q>0だが条件なし'] == 0 for k in rv)  # 本文「可逆でないフレーズで q>0 のものは無い」
    ta = load('two_arches_essen.json')
    v['ta_n'] = f"{ta['retrograde_10_16']:,}"; v['ta_two'] = f"{ta['2つの回文の並び']:,}"; v['ta_pal'] = f"{ta['ふつうの回文']:,}"
    cs = load('census_essen.json')['bands']
    v['census_oe1316'] = f"{cs['13-16']['oe']:.1f}"
    v['census_sym_share'] = f"{100 * sum(b['O'] for b in cs.values()) / sum(b['N'] for b in cs.values()):.1f}%"
    for nm, key in (('essen', 'pc_retro_essen'), ('mtc-ann-2.0.1', 'pc_retro_ann')):
        pc = load(f'paper_classes_{nm}.json')
        v[key] = f"{100 * pc['classes']['retrograde'] / pc['symmetric']:.0f}%"
    ri = load('retro_ident_essen_dedup-global.json')['bands']
    _ri = lambda k: f"{ri[k]['O_id'] / ri[k]['E_id']:.2f} [{ri[k]['oe_id_lo']:.2f}, {ri[k]['oe_id_hi']:.2f}]"
    v['ri_n46'] = f"{ri['4-6']['N_id']}"
    v['ri_dg_oe'] = ', '.join(_ri(k) for k in ['4-6', '7-9', '10-12']) + f" and {_ri('13-16')}"
    de = load('decompose_essen.json')['bands']; d7 = de['7-9']; c7 = d7['ci']
    v['dec_n7'] = str(d7['n_pal'])
    v['dec_e7'] = (f"O/E = {d7['oe_note']:.2f} [{c7['oe_note'][0]:.2f}, {c7['oe_note'][1]:.2f}] is the product of {d7['f1']:.2f} [{c7['f1'][0]:.2f}, {c7['f1'][1]:.2f}] for reversibility, "
                   f"{d7['f2']:.2f} [{c7['f2'][0]:.2f}, {c7['f2'][1]:.2f}] for the ease with which a reversible phrase's transitions form a palindrome, and {d7['f3']:.2f} [{c7['f3'][0]:.2f}, {c7['f3'][1]:.2f}] for the residual")
    da = load('decompose_mtc-ann-2.0.1.json')['bands']['7-9']
    v['dec_a7'] = f"{da['oe_note']:.2f} = {da['f1']:.2f} × {da['f2']:.2f} × {da['f3']:.2f}"; v['dec_a7_n'] = str(da['n_pal'])
    v['dec_e4_f3'] = f"{de['4-6']['f3']:.2f} [{de['4-6']['ci']['f3'][0]:.2f}, {de['4-6']['ci']['f3'][1]:.2f}]"
    v['dec_n_long'] = f"{de['10-12']['n_pal']} and {de['13-16']['n_pal']}"
    ce = load('two_pal_clean_essen.json')['bands']; cf = load('two_pal_clean_mtc-fs-inst-2.0.json')['bands']; cd = load('disjoint_clean.json')['bands']
    v['cl7'] = f"Essen {ci(ce['7-9'])}, MTC-FS-INST {ci(cf['7-9'])}"
    v['cl10'] = (f"Essen {ci(ce['10-12'])} and {ci(ce['13-16'])}; MTC-FS-INST {ci(cf['10-12'])} and {ci(cf['13-16'])}; "
                 f"disjoint MTC-FS-INST {cd['10-12']['oe']:.2f} and {cd['13-16']['oe']:.2f}")
    ti = load('types_essen_interval.json')['cells']['13-16|回文型']
    v['iv_mirror1316'] = f"{ti['O'] / ti['E']:.2f}"
    v['tp_vi_beta'] = f"β_1 = {beta(t['fsinst_vocal']['beta1'])} and {beta(t['fsinst_instrumental']['beta1'])}"
    v['dec_e7_f3'] = f"{d7['f3']:.2f} [{c7['f3'][0]:.2f}, {c7['f3'][1]:.2f}]"
    v['dec_a7_f3'] = f"{da['f3']:.2f} [{da['ci']['f3'][0]:.2f}, {da['ci']['f3'][1]:.2f}]"
    shv = [100 * rv[k]['条件'] / rv[k]['N'] for k in rv]
    v['rev_essen_range'] = f"{min(shv):.0f}–{max(shv):.1f}%"
    rg = load('region_essen.json')['groups']
    pct = lambda g, k, d: f"{100 * rg[g][k] / rg[g]['N']:.{d}f}%"
    v['rg_kindr'] = f"{pct('kindr', 'rev', 1)} of phrases of 7–16 notes are reversible and {pct('kindr', 'pal', 2)} are palindromes"
    v['rg_deut'] = f"{pct('deut', 'rev', 1)} and {pct('deut', 'pal', 2)}"
    v['rg_shanx'] = f"{pct('shanx', 'rev', 1)} and {pct('shanx', 'pal', 2)}"
    rat = [rg[g]['pal'] / rg[g]['rev'] for g in ('deut', 'kindr', 'oestr', 'suisse')]
    v['rg_ratio_de'] = f"{min(rat):.2f} and {max(rat):.2f}"
    h, x = (f"{rg[g]['pal'] / rg[g]['rev']:.2f}" for g in ('han', 'shanx'))
    v['rg_ratio_cn'] = f"{h} in both the Han and the Shanxi collections" if h == x else f"{h} and {x} in the Han and Shanxi collections"
    idd = load('ident.json')
    fixed = min((r['q=0'] + r['q=1']) / (r['q=0'] + r['q=1'] + r['0<q<1']) for r in (idd['4-9|retrograde'], idd['10-16|retrograde']))
    v['fixed_floor'] = f"{int(100 * fixed)}%"   # 「〜を超える」と書くので切り捨て
    v['dj_dropped'] = f"{100 * load('disjoint_orig.json')['dropped_null_share']:.2f}%"
    dc = load('data_counts.json'); n = lambda x: f'{x:,}'
    for k in ('essen', 'mtc-ann', 'fsinst', 'fsinst_disjoint'): v[f'dc_{k.replace("-", "_")}_ph'] = n(dc[k]['phrases_4_16'])
    v['dc_ann_tunes'] = n(dc['mtc-ann']['tunes']); v['dc_fs_tunes'] = n(dc['fsinst']['tunes'])
    v['dc_fs_voc'] = n(dc['fsinst_vocal']['tunes']); v['dc_fs_ins'] = n(dc['fsinst_instrumental']['tunes'])
    v['dc_ann_in_fs'] = n(dc['ann_in_fsinst']); v['dc_dj_tunes'] = n(dc['fsinst_disjoint']['tunes'])
    rm = dc['disjoint_removed_phrases']; rm_ann = dc['mtc-ann']['phrases_4_16']
    v['dc_removed'] = f"{n(rm)} phrases ({n(rm_ann)} with the MTC-ANN songs and {n(rm - rm_ann)} by the matching rule)"
    v['dc_sha'] = f"{dc['essen']['sha256_16']} (Essen), {dc['mtc-ann']['sha256_16']} (MTC-ANN) and {dc['fsinst']['sha256_16']} (MTC-FS-INST)"
    mj = load('middle_jump_essen.json')
    v['mj_n'] = str(mj['n']); v['mj_mid'] = str(mj['positions']['2']); v['mj_exp'] = f"{mj['n'] / 3:.1f}"
    au = load('audit_sampler.json'); from scipy.stats import kstest
    assert au['all_seen']   # 本文「総当たりの全ての音列が出た」
    v['au_desc'] = f"{au['n']} phrases of 13–16 notes with {au['min_paths']:,} to {au['max_paths']:,} distinct sequences"
    v['au_res'] = f"{au['p_below_005']} of {au['n']} below 0.05; Kolmogorov–Smirnov test against the uniform distribution p = {kstest([r['p'] for r in au['rows']], 'uniform').pvalue:.2f}"
    sp = load('split_position_mtc-fs-inst-2.0.json')['bins']; mid = ('0.4', '0.5', '0.6')
    so = sum(b['O'] for b in sp.values()); se = sum(b['E'] for b in sp.values())
    v['split_mid'] = (f"{100 * sum(sp[k]['O'] for k in mid) / so:.0f}% of observed cuts fall between 0.35 and 0.65 of the phrase length, "
                      f"against {100 * sum(sp[k]['E'] for k in mid) / se:.0f}% under the null")
    cb = [load(f)['beta1'] for f in ('two_pal_clean_essen.json', 'two_pal_clean_mtc-fs-inst-2.0.json', 'disjoint_clean.json')]
    v['cl_beta'] = f"β_1 = {beta(cb[0])}, {beta(cb[1])} and {beta(cb[2])}"
    words = {0: 'no', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five'}
    oc = lambda k: words.get(dc[k]['over_cap'], f"{dc[k]['over_cap']:,}")
    v['cap'] = f"{dc['cap']:,}"
    v['over_cap'] = f"all but {oc('essen')} Essen phrases and {oc('fsinst')} MTC-FS-INST phrases"
    v['ta_other'] = f"{ta['その他']:,}"
    fo = load('disjoint_orig_family.json'); fcl = load('disjoint_clean_family.json'); fc = load('family_concentration.json')
    v['fam_n'] = f"{fo['n_clusters']:,}"; v['song_n'] = f"{load('disjoint_orig.json')['n_clusters']:,}"
    v['fam_beta'] = f"β_1 = {beta(fo['beta1'])}; with the stricter definition, {beta(fcl['beta1'])}"
    v['fam_conc'] = f"the {fc['n']} observed phrases of 13–16 notes under the stricter definition come from {fc['n_families']} family clusters, at most {fc['max_per_family']} from any one"
    daf = load('decompose_mtc-ann-2.0.1_family.json')['bands']['7-9']['ci']['f3']
    v['dec_a7_f3_fam'] = f"[{daf[0]:.2f}, {daf[1]:.2f}]"
    v['ann_families'] = f"{dc['mtc-ann']['families']:,}"
    de, cn = t['essen_de'], t['essen_cn']
    cde, ccn = load('two_pal_clean_essen_de.json')['beta1'], load('two_pal_clean_essen_cn.json')['beta1']
    v['region'] = (f"with the registered definition β_1 = {beta(de['beta1'])} in the German-language and {beta(cn['beta1'])} in the Chinese collections; "
                   f"with the stricter definition {beta(cde)} and {beta(ccn)}")
    me, mf = load('two_pal_clean_essen_min3.json')['bands'], load('two_pal_clean_fsinst_disjoint_min3.json')['bands']
    v['min3'] = (f"Essen {ci(me['10-12'])} and {ci(me['13-16'])}; disjoint MTC-FS-INST {ci(mf['10-12'])} and {ci(mf['13-16'])} "
                 f"for 10–12 and 13–16 notes, from {mf['10-12']['O']} and {mf['13-16']['O']} observed phrases")
    v['min3_fs1316'] = f"{mf['13-16']['oe']:.1f}"
    mv, mi = load('two_pal_clean_fsinst_vocal_min3.json')['bands'], load('two_pal_clean_fsinst_instrumental_min3.json')['bands']
    v['min3_vi'] = f"vocal {ci(mv['10-12'])} and {ci(mv['13-16'])}, instrumental {ci(mi['10-12'])} and {ci(mi['13-16'])}"
    L3 = lambda bd: f"{ci(bd['7-9'])}, {ci(bd['10-12'])} and {ci(bd['13-16'])}"
    neo, nfo = load('two_pal_clean_essen_onlynest.json'), load('two_pal_clean_fsinst_disjoint_onlynest.json')
    nen, nfn = load('two_pal_clean_essen_nonest.json'), load('two_pal_clean_fsinst_disjoint_nonest.json')
    v['nest_only'] = f"Essen {L3(neo['bands'])}; disjoint MTC-FS-INST {L3(nfo['bands'])} for 7–9, 10–12 and 13–16 notes"
    v['nest_no'] = (f"Essen {ci(nen['bands']['10-12'])} and {ci(nen['bands']['13-16'])}, β_1 = {beta(nen['beta1'])}; "
                    f"disjoint MTC-FS-INST {ci(nfn['bands']['10-12'])} and {ci(nfn['bands']['13-16'])}, β_1 = {beta(nfn['beta1'])}")
    m3n, m3o = load('two_pal_clean_fsinst_disjoint_min3_nonest.json')['bands'], load('two_pal_clean_fsinst_disjoint_min3_onlynest.json')['bands']
    v['nest_min3'] = f"{ci(m3n['10-12'])} and {ci(m3n['13-16'])} without nesting, {ci(m3o['10-12'])} and {ci(m3o['13-16'])} with it"
    on = load('disjoint_orig_nonest.json')
    v['nest_orig'] = f"13–16 notes O/E = {ci(on['bands']['13-16'])}, β_1 = {beta(on['beta1'])}"
    o2 = load('two_pal_clean_fsinst_disjoint_onlynest_order2.json')
    v['order2'] = f"nested phrases {ci(o2['bands']['10-12'])} and {ci(o2['bands']['13-16'])} for 10–12 and 13–16 notes, β_1 = {beta(o2['beta1'])}"
    o3 = load('two_pal_clean_fsinst_disjoint_onlynest_order3.json')['bands']
    v['order3'] = f"{ci(o3['10-12'])} and {ci(o3['13-16'])} from only {o3['10-12']['n_id']} and {o3['13-16']['n_id']} identifiable phrases"
    lo_, ln_ = load('two_pal_clean_fsinst_disjoint_lrcond_onlynest.json')['bands'], load('two_pal_clean_fsinst_disjoint_lrcond_nonest.json')['bands']
    v['lrcond'] = (f"nested {ci(lo_['10-12'])} and {ci(lo_['13-16'])} for 10–12 and 13–16 notes, against {nfo['bands']['10-12']['oe']:.2f} and {nfo['bands']['13-16']['oe']:.2f} without the condition; "
                   f"not nested {ln_['10-12']['oe']:.2f} and {ln_['13-16']['oe']:.2f}")
    po_, pn_ = load('two_pal_clean_fsinst_disjoint_onlynest_posrep.json')['bands'], load('two_pal_clean_fsinst_disjoint_nonest_posrep.json')['bands']
    pa_n, pa_o = load('paired_posrep_lrcond_fsinst_disjoint_nonest.json')['bands'], load('paired_posrep_lrcond_fsinst_disjoint_onlynest.json')['bands']
    def pci(c): return f"{c['oe']:.2f} [{c['lo']:.2f}, {c['hi']:.2f}]"
    v['paired'] = (f"nested, {pa_o['10-12']['n_id']} and {pa_o['13-16']['n_id']} phrases: {pci(pa_o['10-12']['lrcond'])} and {pci(pa_o['13-16']['lrcond'])} with the length condition, "
                   f"{pci(pa_o['10-12']['posrep'])} and {pci(pa_o['13-16']['posrep'])} with the position condition; not nested, {pa_n['10-12']['n_id']} and {pa_n['13-16']['n_id']} phrases: "
                   f"{pci(pa_n['10-12']['lrcond'])} and {pci(pa_n['13-16']['lrcond'])}, against {pci(pa_n['10-12']['posrep'])} and {pci(pa_n['13-16']['posrep'])}")
    bo, bn = load('two_pal_clean_fsinst_disjoint_beat_onlynest.json')['bands'], load('two_pal_clean_fsinst_disjoint_beat_nonest.json')['bands']
    eo = load('two_pal_clean_essen_beat_onlynest.json')['bands']
    v['beat'] = (f"disjoint MTC-FS-INST, nested {ci(bo['10-12'])} and {ci(bo['13-16'])} for 10–12 and 13–16 notes, not nested {bn['10-12']['oe']:.2f} and {bn['13-16']['oe']:.2f}; "
                 f"Essen, nested {ci(eo['10-12'])} and {ci(eo['13-16'])} from {eo['10-12']['n_id']} and {eo['13-16']['n_id']} identifiable phrases")
    fp, fn = load('two_pal_clean_fsinst_disjoint_per.json'), load('two_pal_clean_fsinst_disjoint_noper.json')
    ep, en = load('two_pal_clean_essen_per.json'), load('two_pal_clean_essen_noper.json')
    v['per'] = (f"disjoint MTC-FS-INST {ci(fp['bands']['10-12'])} and {ci(fp['bands']['13-16'])}, Essen {ci(ep['bands']['10-12'])} and {ci(ep['bands']['13-16'])} for 10–12 and 13–16 notes")
    v['noper'] = (f"disjoint MTC-FS-INST {ci(fn['bands']['10-12'])} and {ci(fn['bands']['13-16'])}, β_1 = {beta(fn['beta1'])}; "
                  f"Essen {ci(en['bands']['10-12'])} and {ci(en['bands']['13-16'])}, β_1 = {beta(en['beta1'])}")
    v['per_1316'] = f"{fp['bands']['13-16']['oe']:.0f}"
    aa = load('aa_share_fsinst_disjoint.json')['bands']
    v['aa_share'] = f"{aa['10-12']['aa']} of {aa['10-12']['observed']} and {aa['13-16']['aa']} of {aa['13-16']['observed']}"
    mn, mp = load('two_pal_clean_fsinst_disjoint_min3_noper.json')['bands'], load('two_pal_clean_fsinst_disjoint_min3_per.json')['bands']
    v['min3_per'] = f"periodic {ci(mp['10-12'])} and {ci(mp['13-16'])}, not periodic {ci(mn['10-12'])} and {ci(mn['13-16'])}"
    uf, ue = load('unit_cyclic_fsinst_disjoint.json')['bands'], load('unit_cyclic_essen.json')['bands']
    v['unit_short'] = f"{uf['3-5']['units']} and {ue['3-5']['units']}"
    v['unit_long'] = (f"disjoint MTC-FS-INST {ci(uf['6-8']['transitions'])} from {uf['6-8']['transitions']['n']} figures, "
                      f"Essen {ue['6-8']['transitions']['oe']:.2f} from {ue['6-8']['transitions']['n']}")
    pf, pe = load('periodic_oe_fsinst_disjoint.json')['bands'], load('periodic_oe_essen.json')['bands']
    v['per_all'] = f"periodic phrases as such: disjoint MTC-FS-INST {ci(pf['10-12'])} and {ci(pf['13-16'])}, Essen {ci(pe['10-12'])} and {ci(pe['13-16'])}"
    v['posrep'] = (f"nested {ci(po_['10-12'])} and {ci(po_['13-16'])} from {po_['10-12']['n_id']} and {po_['13-16']['n_id']} identifiable phrases; "
                   f"not nested {ci(pn_['13-16'])} at 13–16 notes")
    def rep(name):
        c = load(f'repetition_{name}.json')['cells']
        return '; '.join(f"k = {k}: {c[f'7-9|k{k}']['oe']:.2f}, {c[f'10-12|k{k}']['oe']:.2f} and {c[f'13-16|k{k}']['oe']:.2f}" for k in (3, 4, 5))
    v['rep_essen'] = rep('essen'); v['rep_fs'] = rep('fsinst_disjoint')
    # 新しい値はこの行の上に足す
    # 査読(11/5 MAJOR)への対応: 同じ句の集合で周期的/非周期的に分けた O−E（decomp_periodic.py）
    dc = {k: load(f'decomp_periodic_{k}.json')['bands'] for k in ('fsinst_disjoint_reg', 'essen_reg', 'fsinst_disjoint', 'essen', 'fsinst_disjoint_min3', 'essen_min3')}
    pct = lambda x: f"{100 * x:.0f}%"
    dif = lambda d: f"{d['O_minus_E']:+.1f} [{d['diff_lo']:+.1f}, {d['diff_hi']:+.1f}]".replace('-', '−')
    v['dp_share_strict'] = f"{pct(dc['fsinst_disjoint']['10-12']['share_of_excess_periodic'])} and {pct(dc['fsinst_disjoint']['13-16']['share_of_excess_periodic'])}"
    v['dp_np_strict_1316'] = dif(dc['fsinst_disjoint']['13-16']['noper'])
    v['dp_np_reg'] = f"{dif(dc['fsinst_disjoint_reg']['10-12']['noper'])} and {dif(dc['fsinst_disjoint_reg']['13-16']['noper'])}"
    v['dp_share_reg1316'] = pct(dc['fsinst_disjoint_reg']['13-16']['share_of_excess_periodic'])
    v['dp_np_essen_strict'] = f"{dif(dc['essen']['10-12']['noper'])} and {dif(dc['essen']['13-16']['noper'])}"
    v['dp_share_essen_strict1316'] = pct(dc['essen']['13-16']['share_of_excess_periodic'])
    v['dp_np_clean_fs'] = f"{dif(dc['fsinst_disjoint']['7-9']['noper'])} and {dif(dc['fsinst_disjoint']['10-12']['noper'])}"
    return v
def oe(c, k): return c[k]['O'] / c[k]['E']
def tables():
    nt = load('classes_essen_note.json')['cells']; ex = load('classes_essen_exact.json')['cells']
    f = lambda x: f'{x:.1f}' if x >= 100 else f'{x:.2f}'
    rows = ['| Class | 4–9, notes null | 4–9, transitions null | 10–16, notes null | 10–16, transitions null |', '|---|---|---|---|---|']
    for k in ['retrograde', 'RI', 'translation', 'multiple']:
        rows.append(f'| {k} | ' + ' | '.join(f(oe(c, f'{b}|{k}')) for b in ('4-9', '10-16') for c in (nt, ex)) + ' |')
    dc_rows = ['| Corpus, definition | Notes | Phrases | Excess O−E, all | O−E, periodic | O−E, not periodic | Periodic share |', '|---|---|---|---|---|---|---|']
    lab = {'fsinst_disjoint_reg': 'MTC-FS-INST (disjoint), registered', 'essen_reg': 'Essen, registered', 'fsinst_disjoint': 'MTC-FS-INST (disjoint), stricter', 'essen': 'Essen, stricter', 'fsinst_disjoint_min3': 'MTC-FS-INST (disjoint), three pitch classes per part', 'essen_min3': 'Essen, three pitch classes per part'}
    for k in lab:
        bands = load(f'decomp_periodic_{k}.json')['bands']
        for b in ('7-9', '10-12', '13-16'):
            if b not in bands: continue
            d = bands[b]; g = lambda x: f"{x['O_minus_E']:+.1f} [{x['diff_lo']:+.1f}, {x['diff_hi']:+.1f}]"
            sh = f"{100 * d['share_of_excess_periodic']:.0f}%" if d['all']['diff_lo'] > 0 else '—'   # 全体の超過が0をまたぐ行では割合を出さない
            dc_rows.append((f"| {lab[k]} | {b.replace('-', '–')} | {d['n_phr']} | {g(d['all'])} | {g(d['per'])} | {g(d['noper'])} | {sh} |").replace('-', '−').replace('MTC−FS−INST', 'MTC-FS-INST'))
    return {'t1': '\n'.join(rows), 'dp': '\n'.join(dc_rows)}
if __name__ == '__main__':
    s = PAPER.read_text(); v = values(); missing = set()
    for name, body in tables().items():
        pat = re.compile(rf'(<!--table:{name}-->\n)(.*?)(\n<!--/table-->)', re.S)
        m = pat.search(s)
        if not m: missing.add('table:' + name); continue
        if m.group(2) != body: print(f'table:{name} を作り直した')
        s = s[:m.start(2)] + body + s[m.end(2):]
    def sub(m):
        name, old = m.group(1), m.group(2)
        if name not in v: missing.add(name); return m.group(0)
        if old != v[name]: print(f'{name}: {old!r} -> {v[name]!r}')
        return f'<!--n:{name}-->{v[name]}<!--/n-->'
    s2 = re.sub(r'<!--n:(\w+)-->(.*?)<!--/n-->', sub, s)
    PAPER.write_text(s2)
    used = set(re.findall(r'<!--n:(\w+)-->', s2))
    print('印', len(used), '個 / 未定義', sorted(missing), '/ 未使用', sorted(set(v) - used), '/ 残りの [L]', s2.count('[L]'))
