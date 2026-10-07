# Preregistration: Age-Pretext Encoder (v4, Phase 2 research protocol)

> **Status: DRAFT.** It becomes binding at **Seal 2**, when the architecture is frozen on dev.
> - The machine-readable twin is `protocol/prereg.yaml`. If this prose and the YAML disagree, the YAML wins and the
>   disagreement is a bug.
> - **Seal 2 is blocked** while `open_decisions` is non-empty (D21, §8) or any `TBD_SEAL2` remains (the Phase 4
>   battery).
> - v3 (sealed at Seal 1) is archived by content in `protocol/archive/seal-1/`. Every Seal 1 component still hashes to
>   `protocol/seals/seal-1.json`.

## 0. Provenance

**Seal 1's unpaired H-AGE-P result stands as reported and refuted** (UB 0.401 vs BL-1 point 0.360; ledger rows 16–18).
**Phase 2 adopts the paired comparison PROSPECTIVELY, on dev.** The paired rule is never re-applied to the Seal 1
result.

The other Seal 1 hypotheses (H-AGE-N, H-A, H-B, H-C1, H-C2) were never run. They are withdrawn and superseded by this
protocol; no data were touched for them.

The spine is unchanged:
- append-only hash-chained ledger;
- sealed protocols;
- canaries;
- cluster bootstrap with the culture prep as the unit;
- nulls and baselines declared before any fit.

## 1. Data roles

`splits/dev_confirmatory.json` fixes the roles. The unit is `cluster_id = <lab>:<prep>`, where a prep is an independent
dissection or plating date. EPAmeadev and EPA-MI share three culture dates (20140205, 20140212, 20140402). Each shared
date is one cluster, not two.

| Role | Lab | Sources | Species / region | Preps | DIV (after QC) |
|---|---|---|---|---|---|
| dev | potter_gatech | Wagenaar 2006 | rat cortex | 8 | 3–39 |
| dev | epa_shafer | EPAmeadev + EPA-MI (controls only) | rat cortex | 16 | 2–37 (mostly 2–12) |
| dev | eglen_grant | Charlesworth g2chvcdata (drug files excluded) | mouse hippocampus + cortex | 22 | 7–29 |
| dev | giugliano | Fragile-X (WT + Fmr1-KO) | mouse cortex | 10 | 7–35 |
| confirmatory | epa_shafer | NFA 2018 (TC + NTP) | rat cortex | 17 | 5–12 |
| confirmatory | kapucu_tuni | Kapucu 2022 rat | rat cortex | 3 | 2–35 |

- **Dev:** tuning is unlimited, and every run is ledgered (`phase: exploratory`). Dev results carry no claim.
- **Confirmatory:** one run, under Seal 2, on a clean tree (INVARIANT-4).
- **NFA is not an unseen lab.** It comes from the same lab (EPA, Shafer) as two dev corpora, so for NFA the
  confirmatory run tests unseen preps, not an unseen lab. NFA dissection dates (2016–2017) are disjoint from the dev EPA
  dates (2013–2014).
- **NFA has no spike trains.** It is a feature table (17 endpoints + MI), so the spike encoder cannot be evaluated on
  it (D21).
- **Kapucu** is the only unseen-lab confirmatory corpus.
- **KCL organoids** are deferred until the architecture is frozen (D20).

**Treatment filters.** These recordings never enter the index; the rules live in `configs/data/<source>.yaml`:
- g2chvc files carrying KN62 (cortical arrays, from DIV 17), APV (DIV 19+) or UO126 (the whole series): 69 files.
- EPA-MI dosed wells (columns 2–7).
- EPA-MI post-bicuculline `_01` recordings.

Fmr1-KO is a genotype, not a treatment. It stays in the index as a covariate.

## 2. Invariants

1. Splits are by cluster. Transforms and parameters are fit on training clusters only.
2. Treated recordings never enter age training.
3. Confirmatory clusters are read only by the single Seal 2 run on a clean tree, and every opening is ledgered.
4. A leave-one-lab-out test fold holds exactly one lab, and that lab is absent from its training fold
   (`assert_group_disjoint`).
5. The only sanctioned identity-probe exception is `SplitPurpose.IDENTITY_PROBE`, built only in
   `eval/identity_probe.py`.

**QC.** A recording must be at least 600 s long; this is the Seal 1 Potter rule.
- Length is the stored recording length where one exists (g2chvc). Otherwise it is the time of the last spike.
- **Known bias:** the last-spike proxy drops 3 EPAmeadev DIV-2 plate recordings (144 well rows) because they are
  silent. That is an age-correlated exclusion. It may be revised on dev before Seal 2, and every change is ledgered.

## 3. Decision rule (paired)

For each gating baseline b, let Δ_b = stat(claim) − stat(b), computed on the **same** cluster resample (percentile
bootstrap, B = 4,000, 95%, seed 20261005).
- For an error metric, the claim survives iff **UB(Δ_b) < 0 for every gating b**.
- Otherwise the verdict is REFUTES.
- If the bound cannot be computed (fewer than 5 clusters), the verdict is INCONCLUSIVE.
- There is no minimum effect size (D5 carried over).

**Error weighting.** MAE is the mean over clusters of the within-cluster mean |error|, in log-DIV. EPA contributes
5,040 well recordings against roughly 500 for each other lab, so a per-row MAE would mostly measure EPA.

**Identity rule** (unchanged from v3):
- SUPPORTS iff canary power ≥ 0.8 **and** real-identity permutation p ≥ 0.05.
- REFUTES iff power ≥ 0.8 and p < 0.05.
- INCONCLUSIVE iff power < 0.8.

## 4. Dev evaluation (how dev is scored; no claims)

**Primary: leave-one-lab-out (LOLO)** over the four dev labs (`splits/dev_lolo.json`).
- **Folds:** eglen_grant 22, epa_shafer 16, giugliano 10, potter_gatech 8 clusters.
- **Fitting:** each fold refits everything (encoder, head, BL-0, BL-1, standardisation) on the other three labs.
- **Statistic:** the mean over the four held-out labs of the cluster-weighted MAE, so each lab counts equally.
- **Intervals:** bootstrap resamples clusters within each lab.
- **Gating:** paired against BL-0 and BL-1.
- **Also reported:** each fold's Δ with its cluster CI (every fold has ≥ 8 clusters), the worst fold, and error by DIV.

**Required secondary: the DIV 7–12 overlap stratum.** This is the same LOLO analysis with the same models, restricted to
held-out recordings with DIV in [7, 12]. Every dev lab has recordings there (eglen 7/9/10/11, epa 7/9/12,
giugliano 7/9/11, potter 7–12). It is always reported. If the primary passes but the stratum fails, the advantage is
not shown where the labs overlap in age, and it is reported as possibly lab-age confounded.

**Reported: pooled cluster cross-validation.** This uses 4 group folds by cluster, stratified by lab. It adds BL-LAB
(the training mean log-DIV of the recording's own lab). Its only purpose is to show the size of the lab shortcut, which
LOLO removes.

**Why LOLO is primary.** DIV windows differ by lab (EPA mostly 2–12, Charlesworth 7–29, Wagenaar 3–39, Fragile-X 7–35).
A pooled age regressor can therefore lower its error by recognising the lab, which is the shortcut Claim C forbids.

**Known harmonisation issue.** BL-1's network-burst detector was tuned on 59-electrode arrays, while EPA wells have 16
electrodes. Its parameters may be adapted on dev before Seal 2, and every change is ledgered.

## 5. Confirmatory hypotheses (one run under Seal 2)

### H-AGE-K: cross-lab age transfer (Kapucu rat)

- **Model:** the final pooled encoder plus its age head, trained on all 56 dev clusters. BL-0 and BL-1 are trained on
  the same clusters.
- **Metric:** MAE of log-DIV, paired against BL-0 and BL-1.
- **Inference:** worst-fold. In **each** of the three preps (190617, 250417, 31017), the paired, well-level bootstrap
  UB(Δ_b) must be < 0 for both baselines.
- **Scope:** three clusters are below the 5-cluster minimum. The result is within-prep only, with no inference over
  preps or labs. Two of the three preps record only DIV 21–31.

### H-LAB: lab-identity probe on the pooled model (credibility; sets wording)

- **Representation:** final pooled-encoder z, for dev recordings with DIV in [7, 12].
- **Probe:** multinomial logistic (inner CV); labels = lab; 4 group folds by cluster, stratified by lab.
  - Statistic: excess balanced accuracy.
  - p-value: 1,000 cluster-level permutations.
- **Canary:** in each lab, a seeded random 10% of electrodes get extra Poisson spikes at the stratum median
  per-electrode rate.
  - The canary is injected into training data, and the encoder is retrained (1 member).
  - 20 seeds; required power 0.8 at α = 0.05.
- **Reported, not gating:**
  - rat cortex only (Potter vs EPA);
  - mouse cortex only (Giugliano vs Charlesworth cortex);
  - a hand-crafted-feature probe.
- **Wording:**

  | Verdict | Wording |
  |---|---|
  | SUPPORTS | "lab identity is not decodable from the representation within DIV 7–12" |
  | REFUTES | "lab identity is decodable; species, region, platform and lab are confounded and cannot be separated; LOLO is the only cross-lab age evidence" |
  | INCONCLUSIVE | "underpowered" |

- **Expected outcome:** REFUTES is likely, because platform and species differ by lab. It is pre-declared as
  wording-only, not as a kill.

### Phase 4 battery: TBD_SEAL2

Downstream transfer and readout hypotheses, including any NFA feature-level hypothesis, are specified here before
Seal 2.

## 6. Baselines (all ledgered)

| ID | Definition | Gating |
|---|---|---|
| BL-0 | training-mean log-DIV | yes |
| BL-1 | ridge on [log1p mean firing rate, log1p network-burst rate], α = 1, standardised on the training fold | yes |
| BL-LAB | training mean log-DIV of the recording's lab | no (pooled cluster CV only) |

## 7. Disclosures (ledgered)

- **Kapucu and NFA were inspected before the confirmatory split existed.** This covered counts, layout and medians
  (ledger rows 1–4) and the Kapucu wells-with-spikes count (K3 gate). No model has ever seen either corpus.
- **Wagenaar was used at Seal 1** to train and evaluate the H-AGE-P encoder, and its dev results informed the Phase 1
  power projection. It is dev data.
- **Phase 2 inspection of the four new dev corpora** was limited to:
  - file structure, filenames and metadata fields;
  - recording lengths (for QC);
  - spike-list headers and well IDs.

  No activity statistic was inspected. Each inspection went through a script printing ≤ 40 lines.

## 8. Open decision blocking Seal 2

**D21: the confirmatory spike-level evidence is 3 Kapucu preps.** NFA cannot host an encoder evaluation, because it has
no spikes. Options:
- **(a)** Accept H-AGE-K as is (within-prep, 3 preps).
- **(b)** Before any Phase 3 fit, move one dev lab to confirmatory, e.g. Fragile-X (10 preps) or Charlesworth (22).
  This would give a second unseen-lab, spike-level corpus with ≥ 5 clusters. LOLO would then have 3 folds.
- **(c)** Evaluate an NFA-feature-level age model trained on dev spikes through harmonised features. This tests the
  feature pipeline, not the encoder.

Option (b) must be decided before Phase 3 begins, because dev data used for tuning can never become confirmatory.

## Amendments

_None._
