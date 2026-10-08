# Technical report outline (15–20 pages), v3: protocol-first and outcome-invariant

**Budget:** 5 h of the fixed 10 h block. 1 h on Wed 7 Oct (§1–4 drafted before results exist)
and 4 h on Fri 9 Oct.

**Title (fixed for every outcome):** *Falsifiable by construction: a pre-registered evaluation
protocol for neural MEA representations, applied to an age-pretext encoder.*

**Framing (fixed):** the protocol is the contribution, and Claims A, B and C are its
applications. This matches every row of the `PLAN.md` §6b contingency table, so when claims
fall, nothing is rewritten.

## R-mechanics: how the text follows the verdicts without hand editing

- `report_numbers.py` writes `report/generated/numbers.tex` containing:
  - every number, as a macro tied to a ledger `row_id`;
  - verdict macros `\VerdictAGEP`, `\VerdictAGEN`, `\VerdictA`, `\VerdictB`, `\VerdictCone`,
    `\VerdictCtwo`, each one of `SUPPORTS`, `REFUTES` or `INCONCLUSIVE`;
  - `\CaseNumber` (1–8) per §6b, including the collapse rule.
- Each application subsection includes `sections/interp_<claim>_{supports,refutes,inconclusive}.tex`
  through `\verdictswitch{<macro>}{…}{…}{…}`. **All three variants are written in WI-R before
  Seal #2 opens the lockbox**, so wording cannot follow the results.
- The abstract is assembled from `abstract_protocol.tex` (fixed) + `headline_case<N>.tex`
  (8 pre-written, from §6b) + `result_<claim>_<verdict>.tex` (3 claims × 3 verdicts).
- Figure placement follows the §6b case row: main text vs appendix and order are driven by
  `\CaseNumber`, via `figures_case<N>.tex`. Captions also have per-verdict variants.
- CI fails if any section file contains a literal result number, or if any of the
  3 × 3 + 8 variant files is missing.

## Sections

| § | Section | Pages | Outcome-dependent? | Figures |
|---|---|---|---|---|
| 1 | Introduction: unfalsifiable representations in neural organ-on-chip ML; the protocol as contribution; the three applications; the sponsor digital-twin precondition | 1.5 | Abstract headline only (case macro) | — |
| 2 | **The protocol**: preregistration, relative decision rule, culture-prep clustering, invariants, canary-calibrated identity probes, seals, append-only ledger (incl. disclosure rows) | 3 | No | F2 workflow |
| 3 | Data and roles: Wagenaar (encoder), Kapucu rat (cross-lab target), NFA (readout); why Kapucu hPSC cannot carry inference | 2 | No | F1 corpora/roles |
| 4 | Methods: binned spikes, set encoder, log-DIV, cluster-bagged ensemble, cross-fitting, frozen transfer; NFA ridge readout; shared evaluation core | 2.5 | No | — |
| 5.0 | Age prerequisite (both corpora) | 1 | Verdict-switched paragraph | F4 |
| 5.1 | Application C: credibility. C1 NFA plate-within-prep (primary), C2 Wagenaar batch; canary power for each; aggregation rule | 2 | Verdict-switched (C1, C2) | F5 |
| 5.2 | Application A: cross-lab few-shot transfer; full curve; worst-fold rule (or the D17 choice) | 1.5 | Verdict-switched | F6 |
| 5.3 | Application B: age-residual readout; calibration; detection vs BL-B1/B2; sensitivity; C1 dependency | 2 | Verdict-switched | F7, F8 |
| 6 | **What the protocol caught**: ledger summary (all runs, all verdicts), canary results, any lockbox reopening, cut-order decisions. Grows in prominence as claims fall; never empty. **Includes §6.1 (F2) and §6.2 (data integrity), below.** | 1.5 | Content from the ledger; text fixed | F3 ledger timeline |
| 7 | Limitations and the sponsor precondition: **temporal resolution (400 ms bins, ~34 s receptive field: burst-scale dynamics only, sub-200 ms timing discarded; compute-driven, fixed by the pre-declared G-time ladder before any fit — one paragraph, main text)**; biology vs artefact in batch identity; 3-prep inference for A; feature-only NFA; rat-only core; column-2 confound; NTP compound overlap (deviation 3); zero tuning by design | 1.5 | No | — |
| 8 | Reproducibility: one command, runtime, hardware, verifying the ledger | 0.5 | No | — |
| — | References; appendix (full ledger table, amendments, demoted figures per case) | 1–2 | Figure list by case | per §6b |

The total is about 19 pages, and §6 or §7 absorb slack. The application order is fixed as
C → A → B, matching the video. Within §5 the order never changes. Only the emphasis wording and
figure placement change by case.

## Findings for §6 and §7 (Phase 2; numbers are tied to ledger rows)

### §6.1 The protocol changed a number in the baseline's favour (F2)

Recalibrating the gating baseline's burst detector **per platform**, on dev and before any encoder fit, cut BL-1's age
error on the Axion 16-electrode platform by **13%**: out-of-fold MAE 0.4272 → 0.3709 log-DIV (ledger rows 28–30).
- **Scale:** that platform carries 84% of the dev recordings (5,328 of 6,373).
- **Other platform:** on MCS 8×8 the same procedure moved BL-1 only 0.3062 → 0.2991 (−2.3%).

This is a concrete instance of the protocol changing a result **in the baseline's favour**. With the Seal 1 detector,
which was tuned on 59-electrode arrays, any encoder advantage on EPA data would partly have been a handicapped
baseline. The calibration was declared before it ran (row 28). Its one extension round was declared after round 1
showed edge selections (row 29). Selection used BL-1's own cross-validation, deliberately favouring the baseline.

### §6.2 Data-integrity exclusion found by the protocol (Amendment A1)

Six Wagenaar files are truncated at recording or export (DIV 3–34, last spike at 13–369 s, while the same cultures'
neighbouring recordings run 1,808–2,714 s at comparable rates). They are excluded as data integrity, separately from
the F1 length rule. The same scan found the silent EPA DIV-2 plates to be genuinely silent, so they are kept (ledger
row 33).

### §7 Limitation: the Axion baseline may still be understated (P1)

From the round-1 winner to the round-2 winner, BL-1's Axion error moved **6.45%** (0.3965 → 0.3709; ledger row 32).
That exceeds the pre-stated 2% materiality line, so **the Axion BL-1 may be materially understated**. The search was
not reopened.

By axis:
- **Active fraction (0.1 → 0.05), −2.8%:** this edge is structurally closed. On wells with ≤ 19 active electrodes,
  0.05 is identical to 0, verified on 438 of 438 wells.
- **Bin (200 → 400 ms), −1.6%:** this is the one open edge. Its last step was below 2%.

Any encoder advantage on EPA held-out data is read with this caveat.
