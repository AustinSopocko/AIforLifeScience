# Preregistration: Age-Pretext Encoder (DRAFT v3, NOT SEALED)

> **Status: DRAFT.** Binding at **Seal #1** (WI-05).
> - After sealing, changes are dated amendments with a new seal and a ledger row.
> - The machine-readable twin is `protocol/prereg.yaml`. If prose and YAML disagree, the YAML
>   wins and the disagreement is a bug.
> - **Open before sealing:** D17 (Claim A inference rule with 3 preps), marked ⟨D17⟩.

## 0. Scope and units

| | Wagenaar/Potter (encoder) | Kapucu rat (transfer target) | EPA NFA (readout) |
|---|---|---|---|
| Hypotheses | H-AGE-P, H-C2 | H-A | H-AGE-N, H-B, H-C1 |
| Input | binned spikes (200 ms, 120 s windows) | same bins, **frozen** encoder | 17 endpoints + MI |
| Model | electrode-set encoder, cluster-bagged M = 3 | ridge heads on frozen z | ridge, cluster-bagged M = 5 |
| Prep (cluster unit) | dissection batch (8) | culture-date token (3: `190617`, `250417`, `31017`) | culture date (18) |
| Sensitivity unit | culture (30) | well (36) | plate (99) |
| Splits | 4-fold cross-fit (H-AGE-P); final encoder on all 8 batches | leave-one-prep-out | TC 6-fold cross-fit; NTP lockbox (Seal #2) |

- **Age target:** log(DIV). All MVR data is rat.
- **Tuning:** none. Every hyperparameter is fixed at Seal #1, except the logged pre-seal
  G-time shrink ladder.
- **Intervals:** percentile cluster bootstrap over preps, B = 4,000, 95%. The
  favourable-direction bound is the headline. Lower-level clustering is sensitivity only.

## 1. Invariants

1. Splits are by prep. Transforms and parameters are fit on train preps only.
2. NFA treated wells never enter age training.
3. NTP is read only under Seal #2 on a clean tree, and every opening is ledgered.
4. The encoder never sees Kapucu data during training.
5. **Sanctioned identity-probe exceptions** (`SplitPurpose.IDENTITY_PROBE`, caller-restricted to
   `eval/identity_probe.py`):
   - C2: cultures split within batch.
   - C1: wells split within plate.

## 2. Decision rules

- **Relative rule (D5):** a hypothesis survives only if its favourable-direction
  cluster-bootstrap bound beats the **point estimate** of the best gating baseline. Otherwise it
  is REFUTES. If the bound cannot be computed, it is INCONCLUSIVE.
- **Identity rule (C1, C2):**
  - SUPPORTS iff canary power ≥ 0.8 **and** real-identity permutation p ≥ 0.05.
  - REFUTES iff power ≥ 0.8 and p < 0.05.
  - INCONCLUSIVE iff power < 0.8.
- **Claim status:**
  - A holds iff H-A SUPPORTS.
  - B holds iff H-B SUPPORTS **and** H-C1 is not REFUTES.
  - C holds iff H-C1 SUPPORTS.
  - Anything else "falls". C2 sets C's wording only.
- **Case number** (1–8, `PLAN.md` §6b) is computed from the claim statuses, including the
  collapse rule.

## 3. Hypotheses

### H-AGE-P (prerequisite, Wagenaar)
- **Metric:** out-of-fold MAE of log-DIV, held-out batches. Also reported per DIV bin (3–9,
  10–16, 17–23, 24–39), not gating.
- **Survives iff:** UB < min(point MAE of BL-0, BL-1).
- **If refuted:** the failure is attached to H-A and H-C2.

### H-AGE-N (prerequisite, NFA)
- **Metric:** same, held-out TC preps, controls only.
- **Survives iff:** UB < min(BL-0, BL-1).
- **If refuted:** H-B uses the BL-1 age model, labelled as such.

### H-A: cross-lab few-shot transfer (Wagenaar → Kapucu rat)
- **Encoder:** the final Wagenaar encoder, frozen.
- **Folds:** leave-one-prep-out over `190617`, `250417` and `31017`.
- **Target:** log1p network-burst rate of the same well at t′, where t′ − t ∈ [6, 8].
  - The detector is fixed (`configs/features/potter_handcrafted.yaml`).
  - Alternative target if K3 fires: log mean firing rate at t′.
- **Labelled unit:** well. The pool is the training preps' wells (24).
  - k ∈ {1, 2, 4, 8, 16, all}. 30 draws per k. BL-A2 gets 5 seeds per draw.
- **Pairs:** training uses all pairs of labelled wells. Evaluation uses the held-out prep's pairs
  with t ∈ {21, 24}.
- **Methods** (all receive DIV t):
  - Ours: [frozen z, DIV] → ridge.
  - BL-A0: DIV only.
  - BL-A1: [log mean firing rate, log burst rate, DIV].
  - BL-A2: same architecture from scratch, 40 epochs.
  - BL-A3: [frozen random-init z, DIV].
- **Metric:** MAE, lower is better.
- **Full curve reported.**
- **Survives iff:** ⟨D17; default (a), worst-fold⟩ for **each** held-out prep, the
  well-level bootstrap UB of MAE(ours, k = 4) < min over BL-A0…A3 of point MAE at k = all in
  that prep.
- **Reported, not gating:** zero-shot age MAE of the Wagenaar age head on Kapucu rat, per prep.

### H-B: readout (NFA)
- **Definitions:**
  - Δ = ŷ − log DIV, out-of-fold.
  - E = mean Δ(treated) − mean Δ(same-plate controls).
  - Δ-AUC is taken over DIV 5–12.
  - Non-cytotoxic: AB ≥ the 5th percentile of control AB.
- **Detection:** at the 5% false-positive rate of a control-vs-control null, at the highest
  non-cytotoxic dose.
- **Gating baselines:** BL-B1 (BL-1 age residual), BL-B2 (best single raw feature, chosen on
  dev).
- **Reported, not gating:** BL-B3 (Mahalanobis).
- **Calibration gate:** the held-out control mean Δ CI contains 0.
- **Survives iff:** the calibration gate passes and LB(det_Δ) > max point det(BL-B1, BL-B2).
- **Confirmatory:** NTP under Seal #2.
- **Sensitivity, not gating:** lowest-dose reference; plate-clustered intervals; cytotoxic
  doses separately.
- **Credibility dependency:** if H-C1 REFUTES, B falls regardless of this verdict.

### H-C1: artefact-only identity probe (NFA), PRIMARY for Claim C
- **Representation:** per control well, the Δ trajectory over DIV 5/7/9/12 (TC from cross-fit;
  NTP from the final TC model, under Seal #2). All 18 preps.
- **Probe:** within each prep, labels = plate; multinomial logistic (inner-CV);
  leave-one-well-out within plate.
  - Statistic: excess balanced accuracy pooled over preps.
  - p-value: 1,000 within-prep well-level permutations.
- **Canary:**
  - Per plate, an offset drawn from N(0, (0.5·σ_w)²) added to every transformed input feature
    of all wells of that plate.
  - σ_w is the within-plate between-control-well SD, estimated on TC train preps.
  - The ridge is refit, Δ recomputed, and the probe rerun. 20 seeds.
- **Reported, not gating:** the same probe on the 25 transformed inputs.
- **Scope statement (mandatory in the report):** C1 certifies the readout pipeline, not the
  Wagenaar encoder.

### H-C2: encoder batch probe (Wagenaar), PRIMARY, wording-only
- **Representation:** final-encoder z, within each of the 4 DIV bins.
- **Probe:** labels = batch; cultures split within batch; 1,000 culture-level permutations.
- **Canary:**
  - In each batch, a seeded random 10% of electrodes get extra Poisson spikes at the corpus
    median per-electrode rate for the DIV bin.
  - Injected into training data, and the encoder is retrained. 10 seeds.
- **Wording:**
  - SUPPORTS → "the encoder carries no decodable batch identity".
  - REFUTES → "batch identity is decodable; biology and artefact cannot be separated on this
    corpus".
  - INCONCLUSIVE → "underpowered".

## 4. Baselines (all mandatory, all ledgered)

| Group | Baselines |
|---|---|
| Age | BL-0, BL-1 |
| A | BL-A0, BL-A1, BL-A2, BL-A3 |
| B | BL-B1, BL-B2 (gating); BL-B3 (reported) |
| C1, C2 | canary (validity); input-feature and hand-crafted probes (reported) |

## 5. Phases

| Phase | Covers |
|---|---|
| `exploratory` | Pre-seal work; TC development |
| `confirmatory` | All Wagenaar and Kapucu evaluations (no tuning exists); NTP under Seal #2 |
| `reproduction` | `reproduce.sh` re-runs |
| `infrastructure` | Disclosures, G-time shrink steps, cut-order decisions, amendments |

## 6. Disclosures (ledgered)

- **Row 1, A13:**
  - NFA counts, layout and medians (TC and NTP).
  - Potter index counts.
  - Kapucu folder listing, and one hPSC file's size, header and line count.
  - No model fit.
- **Row 2, recon closure:** listing of every Kapucu rat folder, filenames only. It established
  the 4 rat preps and their DIVs. These preps are Claim A's test data. No spike file was opened.

## Amendments

_None._
