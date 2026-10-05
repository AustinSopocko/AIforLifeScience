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
| 6 | **What the protocol caught**: ledger summary (all runs, all verdicts), canary results, any lockbox reopening, cut-order decisions. Grows in prominence as claims fall; never empty. | 1 | Content from the ledger; text fixed | F3 ledger timeline |
| 7 | Limitations and the sponsor precondition: biology vs artefact in batch identity; 3-prep inference for A; feature-only NFA; rat-only core; column-2 confound; zero tuning by design | 1.5 | No | — |
| 8 | Reproducibility: one command, runtime, hardware, verifying the ledger | 0.5 | No | — |
| — | References; appendix (full ledger table, amendments, demoted figures per case) | 1–2 | Figure list by case | per §6b |

The total is about 19 pages, and §6 or §7 absorb slack. The application order is fixed as
C → A → B, matching the video. Within §5 the order never changes. Only the emphasis wording and
figure placement change by case.
