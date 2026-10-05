# Preregistration — Age-Pretext Encoder (DRAFT, NOT SEALED)

> **Status: DRAFT.** This file becomes binding at **Seal #1** (work item WI-05), after the
> WI-00 kill-gate passes and decisions D2–D6 in `PLAN.md` §15 are answered. After sealing,
> changes are allowed only as dated **amendments** appended at the bottom. Each amendment
> needs a new seal, and the ledger records every amendment. Values in ⟨angle brackets⟩ are
> placeholders that WI-00 must fill. The machine-readable twin is `protocol/prereg.yaml`.
> Evaluators read thresholds from that file only, never from prose. If prose and YAML
> disagree, the YAML wins and the disagreement is a bug.

## 0. Scope

- **Primary dataset:** US EPA Network Formation Assay 2018 release (rat cortex, Axion 48-well,
  DIV 5/7/9/12).
  - Development set: ToxCast subset (TC), 12 preps, 6-fold grouped cross-fitting by prep.
  - Confirmatory lockbox: NTP subset, 6 preps. Opened once, under Seal #2.
- **Unit of analysis:** recording = well × DIV.
- **Unit of independence:** culture prep (`date` column). All intervals are percentile cluster
  bootstraps over preps (B = 4,000, 95%). The **lower bound** is the headline.
- **Age target:** log(DIV). Δ = predicted − actual (log-days). Reported in days via
  DIV·(exp(Δ) − 1).

## 1. Invariants (enforced in code, see `src/agepretext/invariants.py`)

- **INVARIANT-1.** Splits are by prep. No prep appears in two partitions. Transforms and
  hyperparameters are fit on train preps only.
- **INVARIANT-2.** Treated wells (dose > 0) never enter pretext (age) training.
- **INVARIANT-3.** The lockbox is read only under a sealed protocol on a clean tree. Every
  opening is ledgered.
- **Sole exception:** Claim C identity probes split by DIV within plate
  (`SplitPurpose.IDENTITY_PROBE`), because identity probes need shared identities.

## 2. Hypotheses, metrics, nulls, kill conditions

### H-AGE (prerequisite)
- **Metric:** out-of-fold R² and MAE (log-days) on held-out preps, controls only.
- **Supports if:** R² lower bound > ⟨0.30⟩ **and** MAE ≤ BL-1 MAE (paired cluster bootstrap,
  upper bound of MAE difference ≤ ⟨10%⟩ of BL-1 MAE).
- **Kill:** otherwise. **Consequence:** Claim B is evaluated on the BL-1 age model, labelled
  "hand-crafted age model". Claim A is still run.

### H-A (representation)
- **Task:** ⟨T1: predict cytotoxicity (compound-dose mean AB < 0.7 at DIV 12) from DIV 5 and
  DIV 7 recordings⟩. Pre-declared alternative under the ceiling rule: ⟨T2⟩.
- **Protocol:**
  - k ∈ {2, 5, 10, 20, 50, 100, all} labelled wells, class-balanced, drawn from train-fold preps.
  - 50 draws per k.
  - Evaluated on held-out-fold preps.
- **Ours:** frozen 16-d embedding plus L2 logistic regression (C chosen by inner grouped CV
  when k ≥ 20, else fixed C = 1.0).
- **Competitors at every k:**
  - BL-2: logistic regression on the inputs.
  - BL-3: same architecture from random init, trained end-to-end for a fixed ⟨200⟩ epochs.
  - BL-4: frozen random-init encoder plus logistic regression.
- **Primary metric:** AUROC.
- **Supports if:** lower bound of [AUROC_ours(k = 10) − max(AUROC_BL2, AUROC_BL3)(k = 50)]
  > −⟨0.02⟩.
- **Kill:** lower bound ≤ −⟨0.02⟩.
- **Ceiling rule:** if BL-2 at k = 10 has AUROC ≥ 0.95 on dev, switch to the alternative task.
  This is declared now and is not a kill.

### H-B (readout)
- **Definitions:**
  - Δ is computed out-of-fold.
  - Within-plate effect E(c, d, t) = mean Δ(treated c at dose d, DIV t) − mean Δ(same-plate
    controls, DIV t).
  - Δ-AUC(c, d) is the trapezoidal AUC of E over DIV 5–12.
  - Non-cytotoxic means compound-dose mean AB ≥ ⟨0.8⟩.
- **B(i) Calibration:** held-out control mean Δ has a CI containing 0 **and** |mean Δ| <
  ⟨0.10⟩ log-days. Failure voids B.
- **B(ii) Detection:**
  - The null distribution of Δ-AUC comes from control-vs-control pseudo-treatments (each
    control well against the remaining same-plate controls).
  - The threshold is set at a 5% two-sided false-positive rate.
  - Detection rate = the fraction of compounds whose Δ-AUC at their highest non-cytotoxic
    dose exceeds the threshold.
  - The same procedure applied to BL-5 (best single raw feature, chosen on dev) and to BL-6
    (Mahalanobis).
  - **Supports if:** lower bound of (detection_Δ − detection_BL5) > −⟨0.10⟩ (non-inferiority).
  - **Secondary:** superiority to BL-5 (lower bound > 0).
- **B(iii) Dose-dependence:** among detected compounds, median Spearman ρ(dose, Δ-AUC) < 0 with
  a CI excluding 0. Failure removes "dose-dependent" from the claim wording only.
- **Mandatory sensitivity analyses** (reported, not gating):
  - Reference = lowest-dose wells instead of column-2 controls (position confound).
  - Cytotoxic doses reported separately.
  - Plate-level clustering.
- **Kill:** B(i) fails, or B(ii) non-inferiority fails.

### H-C (credibility)
- **C-primary:** plate identity within prep, controls only, on the 16-d embedding.
  - Probe: multinomial logistic, inner-CV regularisation.
  - Leave-one-DIV-out (train on 3 DIVs, test on the 4th).
  - Statistic: excess balanced accuracy (observed − mean of 1,000 within-prep label
    permutations), pooled over preps and held-out DIVs.
- **Supports (probe fails to find identity) if all hold:**
  1. one-sided permutation p > ⟨0.05⟩;
  2. excess balanced accuracy point estimate < ⟨0.10⟩;
  3. excess on embedding ≤ excess on input features (no amplification). This is a paired
     bootstrap, with the upper bound of the difference ≤ ⟨0.02⟩.
- **Validity gate (canary):**
  - Inject a per-plate offset of ⟨0.5⟩ SD into the inputs (random direction per plate,
    fixed seed).
  - Retrain the full pipeline and rerun C-primary.
  - Power is the fraction of 20 canary seeds in which the probe is significant. Power must be
    ≥ ⟨0.8⟩.
  - **If the gate fails, H-C is INCONCLUSIVE, never SUPPORTS.**
- **C-secondary** (reported, not gating): prep identity across preps, age-matched, with the
  amplification ratio vs inputs, PCA-16 and the random-init encoder.
- **Kill:** any of conditions 1–3 fails while the validity gate passes.

## 3. Baselines (all mandatory, all ledgered)

BL-0 predict-mean · BL-1 ridge(MFR, burst rate) · BL-2 linear on all inputs · BL-3 same-arch from scratch
· BL-4 frozen random-init encoder · BL-5 best single raw feature deviation · BL-6 Mahalanobis deviation
· BL-7 EPA published hit calls (external reference only).

## 4. Exploratory vs confirmatory

- Dev (TC) runs are tagged `phase=exploratory` and are always ledgered.
- Hyperparameters may be tuned on dev only, and only by grouped inner CV.
- Seal #2 freezes code, configs and hyperparameters. Lockbox (NTP) runs are tagged
  `phase=confirmatory`.
- The report's headline numbers come from confirmatory rows only. Dev results are reported
  alongside, labelled.

## 5. Things we will report regardless of outcome

- Every ledger row count by claim and verdict.
- Every lockbox opening.
- Every amendment.
- The canary power curve.
- Calibration failures.

## Amendments

_None. Amendments are appended here after Seal #1, each with date, rationale, and new seal hash._
