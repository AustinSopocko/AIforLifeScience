# Preregistration: Age-Pretext Encoder (DRAFT v2, NOT SEALED)

> **Status: DRAFT.** Binding at **Seal #1** (WI-05).
> - After sealing, changes are dated **amendments** at the bottom. Each amendment needs a new
>   seal and a ledger row.
> - The machine-readable twin is `protocol/prereg.yaml`. Verdicts are computed only from it.
>   If prose and YAML disagree, the YAML wins and the disagreement is a bug.
> - Open items are marked ⟨…⟩ and map to `PLAN.md` §15 (D2b, D3′, D13–D15).

## 0. Scope and units

| | Pipeline P (Claims A, C) | Pipeline N (Claim B) |
|---|---|---|
| Corpus | Wagenaar/Potter 2006, dense cultures | EPA NFA 2018 |
| Input | binned spike trains (200 ms, 120 s windows) | 17 well-level endpoints + MI |
| Age model | electrode-set age-pretext encoder, cluster-bagged M = 3 | ridge on 25 transformed inputs, cluster-bagged M = 5 |
| Prep (cluster unit) | dissection batch (8) | culture date (18) |
| Sensitivity unit | culture/dish (30) | plate (99) |
| Development | 4-fold cross-fit, 2 batches per fold; no tuning (D2b) | TC: 6-fold cross-fit, 2 preps per fold |
| Confirmation | n/a (all hyperparameters fixed at Seal #1) | NTP lockbox (6 preps), opened once at Seal #2 |

- **Age target:** log(DIV), species-specific heads. Both corpora are rat in the MVR.
- **Intervals:** prep-level percentile cluster bootstrap, B = 4,000, 95%. The favourable-direction
  bound is the headline. Plate- or dish-clustered intervals are reported alongside as
  sensitivity, never as headline.

## 1. Invariants (enforced in code)

1. **INVARIANT-1.** Splits are by prep. Transforms, imputers and model parameters are fit on
   train preps only. P has no tuned hyperparameters.
2. **INVARIANT-2.** NFA treated wells never enter age training.
3. **INVARIANT-3.** The NTP lockbox is read only under Seal #2 on a clean tree. Every opening is
   ledgered.
4. **Sanctioned exception.** The Claim C probe splits **by culture within batch**
   (`SplitPurpose.IDENTITY_PROBE`), because it needs shared batch labels on both sides.

## 2. Decision rule (applies to every claim except C)

> A claim **survives** only if its cluster-bootstrap bound in the favourable direction is better
> than the **point estimate** of the best pre-declared baseline:
> - **lower** bound for higher-is-better metrics;
> - **upper** bound for error metrics.
>
> There are no absolute thresholds. Anything else is **REFUTES**. A run that cannot compute
> the bound, for example because there are too few clusters, is **INCONCLUSIVE**.

## 3. Hypotheses

### H-AGE-P (prerequisite, Potter)
- **Metric:** out-of-fold MAE of log-DIV on held-out batches (all dense recordings). Also
  reported per DIV bin (3–9, 10–16, 17–23, 24–39) without gating.
- **Baselines:**
  - BL-0: train-fold mean.
  - BL-1: ridge on [log mean firing rate, log network-burst rate].
- **Survives iff:** UB(MAE_encoder) < min(MAE_BL0, MAE_BL1).
- **If refuted:** A and C still run and are reported with this failure attached.

### H-AGE-N (prerequisite, NFA)
- **Metric and baselines:** as H-AGE-P, on held-out TC preps (controls only).
- **Survives iff:** UB(MAE_ridge17) < min(MAE_BL0, MAE_BL1).
- **If refuted:** Claim B is computed on the BL-1 age model, labelled "hand-crafted age model".

### H-A: representation (Potter held-out-batch forecasting) ⟨D3′, D15⟩
- **Target:** log1p network-burst rate of the same culture at DIV t′, where t′ − t ∈ [6, 8]
  (nearest to 7), predicted from the recording at DIV t.
- **Labelled unit:** culture. k ∈ {1, 2, 4, 8, all}, 30 draws per k. Labelled cultures are drawn
  from the fold's training batches only. Test = the fold's held-out batches.
- **Methods** (all receive DIV t as input):
  - Ours: [frozen z, DIV] → ridge.
  - BL-A0: DIV only.
  - BL-A1: [log mean firing rate, log burst rate, DIV] → ridge.
  - BL-A2: same architecture from random init, trained end-to-end on k cultures, 40 epochs.
  - BL-A3: [frozen random-init z, DIV] → ridge.
- **Metric:** MAE, lower is better.
- **Survives iff:** UB(MAE_ours at k = 4) < min over {BL-A0, BL-A1, BL-A2, BL-A3} of point
  MAE at k = all.
- **Alternative target (K3):** if fewer than 3 pairs per culture exist for at least 20 cultures,
  the target becomes log mean firing rate at t′, with the same rule. Declared now.

### H-B: readout (NFA) ⟨D14⟩
- **Definitions:**
  - Δ = ŷ − log DIV, out-of-fold.
  - E(c, d, t) = mean Δ(treated) − mean Δ(same-plate controls).
  - Δ-AUC = trapezoidal area under E over DIV 5–12.
  - Non-cytotoxic: compound-dose mean AB ≥ the 5th percentile of control-well AB in the same
    subset.
- **Detection:**
  - Null: control-vs-control pseudo-treatment, each control against the remaining same-plate
    controls, through the identical pipeline.
  - Threshold at the 5% false-positive rate.
  - Detection rate: the fraction of compounds whose Δ-AUC at the highest non-cytotoxic dose
    exceeds the threshold.
- **Gating baselines** (1-D readouts, thresholded identically):
  - BL-B1: age residual from the BL-1 age model.
  - BL-B2: best single raw-feature within-plate deviation AUC, chosen on dev.
- **Reported baseline, non-gating:** BL-B3, Mahalanobis deviation (Ledoit-Wolf, 17-D).
- **Calibration gate:** the CI of held-out control mean Δ contains 0. If not, B is REFUTED.
- **Survives iff:** the calibration gate passes **and** LB(det_Δ) > max(det_BL-B1, det_BL-B2)
  (point estimates).
- **Confirmatory evaluation:** NTP, under Seal #2, with the model trained on all TC preps.
  Headline numbers come from NTP. TC cross-fit results are reported as development.
- **Mandatory sensitivity analyses** (non-gating):
  - lowest-dose wells as the reference (column-2 position confound);
  - plate-clustered intervals;
  - cytotoxic doses reported separately;
  - dose-response, as the median per-compound Spearman ρ(dose, Δ-AUC).

### H-C: credibility (Potter) ⟨D13⟩
- **Data:** dense recordings, stratified into the 4 DIV bins. The probe runs within each bin.
- **Representation:** primary = embeddings from the final encoder trained on all 8 batches.
  Secondary = out-of-fold embeddings.
- **Probe:** multinomial logistic regression (inner-CV regularisation), labels = batch, under
  the culture-within-batch split.
  - Statistic: excess balanced accuracy, pooled over bins.
  - Null: 1,000 permutations of batch labels at the **culture** level.
- **Canary:**
  - Per batch, a seeded random 10% of electrodes receive extra Poisson spikes at the corpus
    median per-electrode rate for that DIV bin.
  - Injected into **training** data. The encoder is retrained end-to-end and the probe rerun.
  - 10 seeds. Power = the fraction of seeds with permutation p < 0.05.
- **Verdict:**
  - **SUPPORTS** iff canary power ≥ 0.8 **and** the real-batch permutation p ≥ 0.05.
  - **REFUTES** iff canary power ≥ 0.8 and real-batch p < 0.05.
  - **INCONCLUSIVE** iff canary power < 0.8.
- **Reported (non-gating):** the same probe on hand-crafted features and on a random-init
  encoder, as amplification context. ⟨If D13 is accepted: the NFA plate-within-prep probe as a
  secondary artefact-only check.⟩

## 4. Baselines (all mandatory, all ledgered)

| Group | Baselines |
|---|---|
| Age | BL-0, BL-1 |
| A | BL-A0, BL-A1, BL-A2, BL-A3 |
| B | BL-B1, BL-B2 (gating); BL-B3 (reported) |
| C | canary (validity), hand-crafted and random-init probes (reported) |

## 5. Phases

- `exploratory`: any run before Seal #1, or TC development runs after it.
- `confirmatory`: P runs under Seal #1 (no tuning exists to separate dev from confirmation in P),
  and NTP runs under Seal #2.
- `reproduction`: `reproduce.sh` re-runs.
- `infrastructure`: disclosures, cut-order decisions, amendments.

## 6. Disclosures

- **A13 (ledger row 1).** Before any split existed, the operator and assistant computed the
  following. No model was fit, and no activity statistic was computed on Potter or Kapucu.
  - NFA row counts, preps, plates, compounds and control-well positions; NaN fractions;
    AB < 0.7 counts; control medians of mean firing rate and burst rate by DIV — on both TC
    and NTP.
  - Potter file counts, cultures per batch and DIV coverage, from index pages.
  - The Kapucu folder listing, and one hPSC file's size, header and line count.

## Amendments

_None._
