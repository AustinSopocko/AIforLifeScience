# Phase 3.1 — Permutation-invariant electrode handling (DEV only)

Ledger rows 35 (declarations, before any fit) and 36–39 (results, compute). Raw output: `artifacts/phase3_1/report.json`.
Everything here is `phase: exploratory`. Dev results carry no claim.

## 1. Mechanism

**Encoder.**
1. A **shared per-electrode dilated 1-D CNN** processes each electrode on its own. Its inputs are two channels:
   `log1p(own counts)` and `log1p(mean-over-electrodes population counts)`. Its settings are unchanged: 400 ms bins,
   channels 8/16/16, kernel 5, dilations 1/4/16.
2. A time mean turns each electrode into one **token**.
3. Pooling is **concat(mean, attention PMA with one learned seed)**.
4. Then z (32 dimensions) and a linear age head.

**Properties.** Every operation after the CNN is a symmetric function of the electrode set, so the encoder is
permutation-invariant. It handles any number of electrodes (Axion 16 / Potter 59 / Charlesworth 60).
- The population channel is a *mean*, so it does not scale with the electrode count N. It gives each electrode its
  network context (bursts, synchrony) without coordinates.
- Max pooling is **dropped**; Seal 1 had it.
- Capacity is otherwise as at Seal 1.

**Electrode set.** Each platform's **nominal physical layout** is used, with silent electrodes as all-zero rows.
Silence is therefore input, and N is a platform constant. **No position features.** Layout differs by platform (4×4
wells vs 8×8 arrays), so positions would hand the model a platform-and-lab label.

**Why this pooling, against the alternatives:**

| Option | Verdict | Reason |
|---|---|---|
| Sum pooling | rejected | It scales with N, so it reads out platform directly |
| Max, or mean + max (Seal 1) | rejected | Extreme-value statistics grow with N. Measured on synthetic data at random init: 60 → 16 electrodes shifts max-pooled features by **7.6%** of their across-window SD, against **≤ 0.2%** for mean and PMA |
| Mean + PMA | **chosen** | Both are weighted averages, so unbiased in N. PMA adds learned, content-based weighting at negligible cost |
| Electrode self-attention (Set Transformer) | deferred | Models pairwise electrode interactions, but it is a capacity increase (not allowed before this report) and O(N²). The population channel already supplies network context |
| Grid or graph convolution with coordinates | rejected | Needs positions, and the layout itself identifies the platform |
| Population-only (sum electrodes, then 1-D CNN) | rejected | Throws away per-electrode heterogeneity. It is close to a learned BL-1 |

**Implementation note.** The CNN runs only on real electrode rows, never on padding. The maths is identical
(unit-tested), and it is about 4× faster on mixed 16/60-electrode batches.

## 2. Compute (re-timed before any fit, ledger row 35)

- **Timing gate:** 3.0 ms per training window (4 threads, option-A mix including electrode subsampling), 0.65 ms per
  predicted window, 0.11 s per probe permutation.
- **Plan:** m = 128 windows per cluster per epoch, about the Seal 1 per-prep exposure. The cycle (LOLO 3 folds + final
  model + 20 canary retrains) was projected at about **5.5 h**, within the 8 h dev budget.
- **Actual: about 9 h of compute over 10.3 h wall-clock. Over budget.** The cloud machine was reclaimed twice. Its
  replacement trained about 2× slower for canary seeds 0–15 (about 27 min per seed instead of about 15). All 20
  declared seeds were run, with no outcome-dependent stopping.

## 3. Age: leave-one-lab-out (paired rule; lab-equal cluster-weighted MAE, log-DIV)

**How to read this.**
- **BL-1** is ridge regression on [log1p mean firing rate, log1p network-burst rate], with the per-platform F2 detector.
- Each baseline was fit two ways: **w** = option-A sample weights, **u** = unweighted.
- The encoder must beat **both** implementations of each baseline.
- Δ = encoder − baseline, with a 95% cluster bootstrap CI (clusters resampled within lab, 4,000 resamples).

| Analysis | Encoder | BL-0 w / u | BL-1 w / u | Δ vs BL-1 w | Δ vs BL-1 u | Dev verdict |
|---|---|---|---|---|---|---|
| **Primary LOLO** (6,367 rec, 46 clusters) | **0.502** | 0.681 / 0.738 | **0.471 / 0.450** | +0.031 [+0.009, +0.051] | +0.052 [+0.010, +0.091] | **REFUTES** |
| **Overlap stratum, DIV 7–12** (2,690 rec) | **0.263** | 0.302 / 0.296 | 0.266 / 0.356 | −0.003 [−0.038, +0.033] | −0.093 [−0.152, −0.038] | **REFUTES** (tie with BL-1 w) |
| Seal 1 QC sensitivity | 0.492 | 0.668 / 0.725 | 0.461 / 0.441 | +0.032 [+0.009, +0.052] | +0.051 [+0.009, +0.090] | REFUTES |

Per held-out lab:

| Held-out lab | Encoder | BL-1 w / u | Δ vs BL-1 w | Δ vs BL-1 u |
|---|---|---|---|---|
| eglen_grant (22 clusters) | 0.325 | 0.339 / 0.346 | −0.014 [−0.046, +0.020] | −0.021 [−0.055, +0.013] |
| epa_shafer (16) | 0.545 | 0.660 / 0.535 | −0.116 [−0.135, −0.097] | +0.009 [−0.005, +0.024] |
| potter_gatech (8) | **0.638** | 0.415 / 0.469 | **+0.223** [+0.168, +0.271] | +0.169 [+0.045, +0.278] |

**Reading.**
- The encoder beats the trivial baseline (BL-0) by a wide margin.
- It **loses to the 2-feature ridge (BL-1) overall**, and the gap is significant against both implementations.
- The loss is **driven by the Potter fold.** Trained on EPA + Charlesworth, it transfers badly to Wagenaar's dense
  cultures: worse than BL-0 w, and failing most at DIV 13–39 (cluster-weighted MAE 0.65–0.90 vs BL-1 0.35–0.58).
- On Charlesworth it ties BL-1. On EPA it beats the weighted BL-1 and ties the unweighted one.
- In the **DIV 7–12 overlap stratum the encoder only ties BL-1 w.** Even where the labs overlap in age, no advantage is
  shown.

## 4. Lab identity (H-LAB) on the final pooled encoder, DIV 7–12

| Probe | Balanced accuracy | Permutation null mean (q95) | Excess | p |
|---|---|---|---|---|
| **Encoder z, 3 labs** | **0.854** | 0.307 (0.374) | **0.547** | 0.001 |
| Encoder z, rat cortex only (Potter vs EPA) | 0.955 | 0.474 (0.544) | 0.480 | 0.001 |
| Hand-crafted (BL-1's 2 features) | 0.393 | 0.310 (0.351) | 0.083 | 0.004 |

Weighted recall from the encoder probe: eglen 0.86, EPA 0.81, Potter 0.90. From the hand-crafted probe, EPA recall is
only 0.06.

**Canary.** In the pseudo-lab design (see §5), **power is 0.75**: 15 of 20 seeds have p < 0.05, per-seed excess BA
0.05–0.33, injected rate 0.617 Hz. That is below the required 0.8.

**Identity rule: INCONCLUSIVE (underpowered).** Formally the probe's power fell short. Descriptively, the lab signal in
z is far larger than the canary signal: excess 0.55 against 0.05–0.33. **Lab identity is strongly decodable from the
representation, and much more so than from the two hand-crafted features.** The encoder has learned lab, platform and
species structure that simple activity statistics barely carry.

## 5. Flag for the operator: the sealed H-LAB canary is inert as written

The sealed text reads: "in each lab, a seeded random 10% of electrodes get extra spikes". For a permutation-invariant
encoder this carries **no lab information**. Every lab receives the same artefact, and which electrodes are noisy is
invisible by design.

Dev therefore used a **pseudo-lab canary**, declared in ledger row 35 before any fit:
- In each seed, a random half of each lab's clusters receives the artefact (10% of electrodes, at the stratum median
  rate).
- The encoder is retrained.
- The probe target is the canary flag, stratified by lab, with permutations within lab.

The confirmatory H-LAB needs a dated amendment to pin this operationalisation. **I have not applied one.**

## 6. What this says (no action taken)

The permutation-invariant set mechanism works mechanically: it is invariant, handles any N, and fits the budget. It
does **not** yet give an age representation that transfers across labs better than two activity features, and z
carries strong lab identity.

Two observations for the next item (not acted on):
- The Potter failure sits where Potter is most different: dense, high-rate cultures, and the DIV range that only Potter
  covers densely (13–39). This is the case the option-B sensitivity run is meant to probe.
- BL-1 ties or beats the encoder at DIV 7–12. The encoder's information beyond firing and burst rates is not yet age
  information that survives a change of lab.
