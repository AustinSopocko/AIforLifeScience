# Preregistration: Age-Pretext Encoder (v5, Phase 2 research protocol, SEALED at Seal 2)

> **Status: binding from the Seal 2 record onward.** After that, changes are dated amendments with a new seal and a
> ledger row.
> - The machine-readable twin is `protocol/prereg.yaml`. If this prose and the YAML disagree, the YAML wins and the
>   disagreement is a bug.
> - **Seal 2 freezes the evaluation protocol:** data roles, splits, QC, detector calibration, hypotheses, rules and
>   baselines.
> - **Seal 3 freezes the architecture** after Phase 3 on dev. It may change or add only `configs/model/set_encoder.yaml`
>   and `configs/train/*.yaml`. `seal()` refuses anything else.
> - The single confirmatory run requires Seal 3 and a clean tree.
> - v3 (Seal 1) is archived by content in `protocol/archive/seal-1/`. The `configs/eval/claim_*.yaml` files are Seal 1
>   records, and no Phase 2 hypothesis reads them.

## 0. Provenance

**Seal 1's unpaired H-AGE-P result stands as reported and refuted** (UB 0.401 vs BL-1 point 0.360; ledger rows 16–18).
**Phase 2 adopts the paired comparison PROSPECTIVELY, on dev.** The paired rule is never re-applied to the Seal 1
result.

The other Seal 1 hypotheses were never run and are withdrawn. H-B-NFA and H-C1 below are re-specified, not resumed.

The spine is unchanged:
- append-only hash-chained ledger;
- sealed protocols;
- canaries;
- cluster bootstrap with the culture prep as the unit;
- nulls and baselines declared before any fit.

## 1. Data roles

`splits/dev_confirmatory.json` fixes the roles. The unit is `cluster_id = <lab>:<prep>`, where a prep is an independent
dissection or plating date. Where EPAmeadev and EPA-MI share a culture date, that date is one cluster.

| Role | Lab | Sources | Species / region | Preps | Use |
|---|---|---|---|---|---|
| dev | potter_gatech | Wagenaar 2006 | rat cortex | 8 | tuning, LOLO |
| dev | epa_shafer | EPAmeadev + EPA-MI (controls) | rat cortex | 16 | tuning, LOLO |
| dev | eglen_grant | Charlesworth g2chvcdata (drug files excluded) | mouse hippocampus + cortex | 22 | tuning, LOLO |
| confirmatory | giugliano | Fragile-X **WT** | mouse cortex | 5 | H-AGE-FX (primary A) |
| confirmatory | giugliano | Fragile-X **Fmr1-KO** vs WT | mouse cortex | 5 + 5 | H-B2 (primary B) |
| confirmatory | kapucu_tuni | Kapucu 2022 rat | rat cortex | 3 | H-AGE-K (within-prep only) |
| confirmatory | epa_shafer | NFA 2018 (feature table) | rat cortex | 17 | H-B-NFA, H-C1 |

- **Dev:** tuning is unlimited, and every run is ledgered (`phase: exploratory`). Dev results carry no claim.
- **Confirmatory:** one run (INVARIANT-4).

**D21 (operator decision, option b).** Fragile-X moved from dev to confirmatory before any Phase 3 fit. The recorded
reasoning:
- 10 preps clear the 5-cluster bootstrap minimum.
- DIV 7–35 overlaps the training range.
- Mouse cortex from a fourth lab is a genuine cross-lab, cross-species generalisation test.
- Moving Charlesworth instead would remove the only hippocampal tissue and nearly half the non-EPA preps from dev.

**NFA** is the same lab as dev EPA, so for NFA the confirmatory run tests unseen preps, not an unseen lab. It has no
spikes, so the encoder cannot enter it. **KCL organoids** are deferred until the architecture is frozen (D20).

## 2. Invariants

1. Splits are by cluster. Transforms and parameters are fit on training clusters only.
2. Treated recordings never enter age training.
3. Confirmatory clusters are read only by the single run under Seal 3 on a clean tree, and every opening is ledgered.
   No Fragile-X recording, WT or KO, is ever used to fit or tune anything.
4. A leave-one-lab-out (LOLO) test fold holds exactly one lab, and that lab is absent from its training fold.
5. The only sanctioned identity-probe exception is `SplitPurpose.IDENTITY_PROBE`, built only in
   `eval/identity_probe.py`.

## 3. Length QC (F1)

Exclusion is on recorded **duration**, never on last-spike time (`configs/data/qc.yaml`, `data/qc.py`).
- **Stored length** (g2chvc `recordingtime`; EPA-MI "Analysis Duration (s)", 902–1316 s): a recording is excluded iff
  it is shorter than 600 s. On dev this excludes nothing.
- **No recorded length** (Potter, EPAmeadev, EPA-MI plate 20140423, Fragile-X): the recording is never excluded for
  length, because a short last-spike time cannot separate a silent recording from a short one, and silence is age
  information. It gets max(1, ⌊last spike / 120 s⌋) windows, with zeros after the last spike.
- **Effect on dev versus the Seal 1 rule:** 294 rows restored.
  - 3 silent EPAmeadev DIV-2 plates (144 rows, 1–3 windows each).
  - 3 short mature EPAmeadev plate recordings (144 rows).
  - 6 Potter recordings. The mature ones (DIV 13–34, last spike 12–127 s) look truncated, not silent; they are kept
    with one window each.
- **Sensitivity:** the Seal 1 rule is reported next to every result. It is not gating.

## 4. BL-1 detector calibration (F2)

A handicapped gating baseline would make the encoder look better for the wrong reason. So BL-1's feature detector was
recalibrated **per platform on dev** before any claim runs (`configs/features/burst_calibration.yaml`;
results in `research/f2_burst_calibration.json`).
- **Search:** 108 settings, declared before the run (ledger row 28).
- **Selection criterion:** BL-1's own 4-fold group-by-cluster out-of-fold age MAE. This is deliberately
  baseline-favouring: it includes the lab that a LOLO fold later holds out.

| Platform | Dev data | Applies to | Bin (ms) | Median × | Active fraction | Min rate (Hz) | BL-1 dev error (log-DIV) |
|---|---|---|---|---|---|---|---|
| mcs_8x8 (59/60 electrodes) | Potter + Charlesworth (1,045 recordings, 30 clusters) | Potter, Charlesworth, **Fragile-X** | 100 | 1.5 | 0.25 | 0 | 0.2991 |
| axion_48w_16 (16 per well) | EPAmeadev + EPA-MI (5,328 well recordings, 16 clusters) | EPA | 400 | 6 | 0.05 | 0 | 0.3709 |
| multiwell_64 | none | Kapucu | = mcs_8x8 (nearest electrode count) | | | | |
| Seal 1 default | — | — | 100 | 4 | 0.25 | 0.1 | mcs 0.3062 / axion 0.4272 |

**How the search ran.**
- **Round 1:** 108 settings per platform. Both winners sat on grid edges (ledger row 29).
- **Round 2:** one extension round, declared before it ran: 12 MCS settings and 48 Axion settings. The final selection is
  the best over both rounds.

**What remains at a grid edge.**
- A minimum rate of 0 Hz is the floor: every electrode with at least one spike counts as active.
- On Axion, the 400 ms bin and the 0.05 active fraction are still at the edge of the extended grid. The declared
  one-round rule ends the search, so BL-1 on Axion may still be slightly below its best.
- The Axion choice works as a population-rate burst detector on 16-electrode wells.

**Effect.** The selected errors are optimistic, because each was chosen on the same cross-validation that scores it.
That optimism favours the baseline, which is the intended direction.

## 5. Decision rule (paired)

For each gating baseline b, let Δ_b = stat(claim) − stat(b), computed on the **same** cluster resample (percentile
bootstrap, B = 4,000, 95%, seed 20261005).
- For an error metric, the claim survives iff UB(Δ_b) < 0 for **every** gating b.
- For a higher-is-better metric, it survives iff LB(Δ_b) > 0 for every gating b.
- Otherwise the verdict is REFUTES. If the bound cannot be computed (fewer than 5 clusters), it is INCONCLUSIVE.
- There is no minimum effect size.

**Error weighting.** MAE is the mean over clusters of the within-cluster mean |error|, in log-DIV.

**Identity rule:**
- SUPPORTS iff canary power ≥ 0.8 **and** real-identity permutation p ≥ 0.05.
- REFUTES iff power ≥ 0.8 and p < 0.05.
- INCONCLUSIVE iff power < 0.8.

## 6. Dev evaluation (no claims)

**Primary: LOLO** over three folds (eglen_grant 22, epa_shafer 16, potter_gatech 8 clusters).
- **Fitting:** each fold refits everything on the other two labs.
- **Statistic:** the mean over held-out labs of the cluster-weighted MAE.
- **Intervals:** clusters are resampled within each lab.
- **Gating:** paired against BL-0 and BL-1.
- **Also reported:** each fold's Δ, the worst fold, error by DIV, and the Seal 1 QC sensitivity.

**Required secondary: the DIV 7–12 overlap stratum.** This is the same analysis restricted to held-out recordings with
DIV in [7, 12]. It is always reported. If the primary passes but the stratum fails, the result is reported as possibly
lab-age confounded.

**Reported: pooled cluster cross-validation** with BL-LAB (the lab-mean baseline). Its purpose is to show the size of
the lab shortcut that LOLO removes.

**Phase 3 requirement (training imbalance).** EPA has about 10 times the recordings of any other dev lab. Per-cluster
scoring handles evaluation, but Phase 3 training must address the imbalance explicitly. The sampling scheme is
proposed and ledgered before the first Phase 3 fit and frozen at Seal 3. One final model, trained on all 46 dev
clusters, serves H-AGE-FX, H-AGE-K, H-B2 and H-LAB.

## 7. Confirmatory hypotheses (one run under Seal 3)

### H-AGE-FX: cross-lab, cross-species age transfer (PRIMARY, Claim A)

- **Data:** Fragile-X **wild-type only**, 5 preps (CS152, CS156, CS192, CS193, CS195).
- **Comparison:** the final pooled encoder's age head against BL-0 and BL-1, both trained on all dev clusters. BL-1 uses
  the mcs_8x8 parameters.
- **Rule:** paired, with cluster-weighted MAE of log-DIV. Clusters are resampled (5 = the minimum).
- **Required secondary:** WT recordings with DIV in [7, 12] (DIV 7, 9, 11).
- **Reported:** error by DIV, the knock-out (KO) zero-shot age MAE, and the Seal 1 QC sensitivity.

### H-AGE-K: unseen-lab age transfer, rat (secondary, Claim A)

- **Data:** Kapucu preps 190617, 250417 and 31017.
- **Comparison:** paired against BL-0 and BL-1. BL-1 uses the mcs_8x8 parameters.
- **Inference:** worst-fold. In **each** prep, the well-level bootstrap UB(Δ_b) must be < 0.
- **Scope:** within these 3 preps only. Two of them record only DIV 21–31.

### H-B2: age residual detects a genetic perturbation, Fmr1-KO vs WT (PRIMARY, Claim B)

This is perturbation detection on a genetic rather than a chemical perturbation, and it was written before anything
was fitted.

- **Residual:** Δ = predicted log-DIV − log DIV per recording, from the same final encoder. It is zero-shot: no Fragile-X
  recording is ever used for fitting or tuning.
- **Shared DIVs:** WT and KO share DIV 7, 9, 14, 21, 28 and 35.
- **Statistic:**
  - m_p(v) = the mean Δ of prep p's recordings at DIV v.
  - E = the mean over shared v of [mean over KO preps of m_p(v) − mean over WT preps of m_p(v)].
  - s = the pooled within-genotype SD of the DIV-centred prep means.
  - The effect is |d| = |E/s|, two-sided.
- **Detection null:** an exact permutation test over all 252 assignments of genotype labels to the 10 preps (5 vs 5).
  Prep is the unit, so differences between culture sessions are part of the null.
- **Gating baselines** (the same statistic):
  - BL-B1g: BL-1's age residual.
  - BL-B2g: the larger effect of the two raw BL-1 features. Taking the post-hoc maximum deliberately favours the
    baseline.
- **Rule:** SUPPORTS iff the permutation p < 0.05 **and** LB(|d_enc| − |d_b|) > 0 for both baselines. Preps are
  resampled within genotype (5 + 5). Otherwise the verdict is REFUTES, or INCONCLUSIVE if the bound cannot be computed.
- **Dependency:** if H-AGE-FX REFUTES, the verdict stands, but the wording becomes "separation by the residual of an age
  model that did not beat its baselines on WT".

### H-B-NFA: chemical perturbation readout on NFA (secondary, Claim B; feature-level)

This is v3 H-B re-specified. All 17 preps are confirmatory, so there is no NFA dev data to fit on. Instead, the age
model is cross-fit inside NFA with every setting fixed here.
- **Age model:** ridge (α = 1) on the 17 endpoints plus MI (`configs/features/nfa17.yaml`), bagged over preps (M = 5),
  fit on control wells, leave-one-prep-out across the 17 preps.
- **Age check (H-AGE-N):** paired against BL-0 and BL-1-NFA. If it REFUTES, H-B-NFA uses the BL-1-NFA age model,
  labelled as such.
- **Definitions:**
  - Δ = ŷ − log DIV, out-of-fold.
  - The effect is mean Δ(treated) − mean Δ(same-plate controls), summarised as the AUC over DIV 5–12.
  - Non-cytotoxic: AB ≥ the 5th percentile of control AB.
- **Detection:** at the 5% false-positive rate of a within-plate control-vs-control null, at the highest
  non-cytotoxic dose.
- **Rule:**
  - The calibration gate passes: the held-out control mean Δ CI contains 0.
  - **And** LB(det_claim − det_b) > 0 against BL-B1 and BL-B2. BL-B2 is selected on the training preps of each fold.
- **Reported, not gating:** BL-B3 and the sensitivity analyses.
- **Dependency:** H-B-NFA falls if H-C1 REFUTES.

### H-C1: plate identity in the NFA readout (PRIMARY, Claim C)

- **Representation:** the out-of-fold Δ trajectory of control wells over DIV 5/7/9/12.
- **Probe:** within each prep, labels = plate; leave-one-well-out within plate; 1,000 within-prep well permutations.
- **Canary:** a per-plate offset of 0.5 × the within-plate control SD (estimated on each fold's training preps). The
  pipeline is refit; 20 seeds; required power 0.8.
- **Rule:** identity rule.
- **Scope statement:** it certifies the NFA readout pipeline, not the encoder.

### H-LAB: lab identity in the pooled encoder (Claim C wording)

- **Representation:** final-encoder z for dev recordings with DIV in [7, 12].
- **Probe:** multinomial logistic, labels = lab, 4 group folds by cluster stratified by lab; cluster-level
  permutations.
- **Canary:** lab-specific noisy electrodes (10% of electrodes, at the stratum median rate), injected into training
  data, encoder retrained; 20 seeds; required power 0.8.
- **Wording:**

  | Verdict | Wording |
  |---|---|
  | SUPPORTS | "lab identity is not decodable from the representation within DIV 7–12" |
  | REFUTES | "lab identity is decodable; species, region, platform and lab are confounded and cannot be separated; LOLO is the only cross-lab age evidence" |
  | INCONCLUSIVE | "underpowered" |

### Claim status

- A holds iff H-AGE-FX SUPPORTS.
- B holds iff H-B2 SUPPORTS.
- C holds iff H-C1 SUPPORTS.
- C's wording comes from H-LAB.
- H-AGE-K and H-B-NFA verdicts are always reported beside the claims, but they never change them.
- The case number (1–8) follows the table in `prereg.yaml`.

## 8. Baselines

| ID | Definition | Gating for |
|---|---|---|
| BL-0 | training-mean log-DIV | ages, LOLO |
| BL-1 | ridge on log1p [mean firing rate, network-burst rate], per-platform detector (§4) | ages, LOLO |
| BL-LAB | lab-mean log-DIV | none (pooled cross-validation only) |
| BL-B1g / BL-B2g | BL-1 residual / max raw feature, H-B2 statistic | H-B2 |
| BL-1-NFA, BL-B1, BL-B2, BL-B3 | as in v3, with selection inside the cross-fit | H-AGE-N, H-B-NFA (B3 reported) |

## 9. Disclosures (ledgered)

- **Kapucu and NFA were inspected before the confirmatory split existed.** This covered counts, layout and medians
  (ledger rows 1–4) and the Kapucu wells-with-spikes count (K3). No model has ever seen either corpus.
- **Fragile-X was dev during Phase 2.1.** Its files were opened for:
  - structure and filenames;
  - per-file last-spike times (length QC);
  - one file's spike-array shape, time range and electrode range.

  No feature or model was ever computed on it (ledger row 25).
- **Wagenaar was used at Seal 1** (H-AGE-P) and in the Phase 1 projection. It is dev data.
- **Phase 2 inspection of the dev corpora** was limited to structure, metadata, recording lengths and headers. One
  EPA-MI statistics-file printout included one burst-duration value (dev data).
- **F2 is the only dev fitting before Seal 2:** BL-1 ridge models over the declared grid.

## Amendments

### A1 (2026-10-08): data-integrity exclusion of 6 truncated Potter files

This is operator item P2. It is a **data-integrity** exclusion, separate from the F1 length rule. It is recorded in
`configs/data/integrity_exclusions.yaml` and in the ledger (`amendment_a1_integrity_exclusion`), and it is sealed at
Seal 3.

**Rule.** A file with no recorded length is truncated iff both:
- its last spike falls before 0.25 × the median last-spike time of the same culture or plate's recordings within ±5 DIV;
- its spike rate up to that point is ≥ 0.25 × those recordings' median rate, so it is active, not silent.

**Recordings flagged.** Scanning all 633 dev units with no recorded length flags exactly 6 Potter recordings.

| Recording | DIV | Last spike (s) | Rate (Hz) | Neighbours: median length (s) / median rate (Hz) |
|---|---|---|---|---|
| 2-1-3 | 3 | 369 | 10.2 | 2,713 / 8.2 |
| 2-3-18 | 18 | 95 | 498.3 | 2,714 / 253.4 |
| 2-4-34 | 34 | 13 | 514.4 | 2,700 / 325.4 |
| 2-5-9 | 9 | 22 | 212.5 | 2,700 / 117.2 |
| 3-5-13 | 13 | 127 | 242.6 | 1,809 / 74.5 |
| 6-2-13 | 13 | 25 | 107.4 | 1,808 / 121.8 |

All 6 are intact bz2 streams ending on a complete line, so they were truncated at recording or export, not in
transfer. Neither the files nor the dataset index state a length.

**Checked and not flagged:**
- The 3 EPAmeadev DIV-2 plates are silent (0.0–0.1 Hz across the plate), so F1 keeps them.
- The 3 short mature 20131113 plates match their own plates' 522–727 s recordings at neighbouring DIVs. That is a
  shorter protocol, not truncation.

**Effect on F2.** The sealed F2 calibration included the 6 files. Re-scoring without them leaves the mcs_8x8 selection
unchanged (0.2991 → 0.2992).

**Confirmatory corpora.** The same rule is applied to Fragile-X and Kapucu inside the confirmatory run only.


### A2 (2026-10-09): H-LAB canary = pseudo-lab canary

Approved by the operator; it is sealed at Seal 3. The sealed electrode-based canary carries no lab signal for a
permutation-invariant encoder: every lab gets the same artefact, and electrode identity is invisible by design.

**Design** (`configs/eval/hlab_canary.yaml`):
- In each seed, a seeded random half of each lab's clusters is canary-positive.
- In every recording of those clusters, 10% of electrodes get extra Poisson spikes at rate_multiplier × the stratum
  median electrode rate.
- The artefact is injected into the raw counts before any input transform, and the encoder is retrained.
- The probe target is the canary flag, stratified by lab, with permutations within lab.
- 20 seeds; required power 0.8.

**Strength.** The rate multiplier was 1 in dev 3.1, where power was 0.75 (ledger row 38). It is calibrated **once**, on
the 3.1 encoder: the smallest of 2/3/4 with 20-seed power ≥ 0.90. It is then **frozen for every probe**, so before and
after comparisons share one scale.