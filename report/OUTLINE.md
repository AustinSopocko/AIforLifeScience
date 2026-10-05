# Technical report outline (15–20 pages), draft

Built by `agepretext report`. LaTeX lives in `report/main.tex` and `report/sections/`.
Generated inputs: `report/generated/numbers.tex` (macros tied to ledger `row_id`s) and
`report/generated/fig_*.pdf` from the `viz/figures.py` registry. CI fails if a section file
contains a literal result number that is not a macro.

| § | Section | Pages | Figures / tables | Source |
|---|---|---|---|---|
| 1 | Abstract and contributions (three claims, one run, falsifiable credibility) | 1 | — | numbers.tex |
| 2 | Problem and impact: maturity readouts for neural organ-on-chip; DNT screening; the sponsor digital-twin precondition (PLAN §13) | 2 | F0 concept diagram (static, versioned SVG) | — |
| 3 | Data: sources, hierarchy, licences, what is *not* available (no NFA spike lists, no human age×perturbation) | 2 | F1 hierarchy and DIV×prep overview, T1 data table | recon/inventory.json |
| 4 | Method: features, age target, model, ensemble, cross-fitting, invariants | 2.5 | F2 pipeline diagram | configs |
| 5 | Validation protocol: preregistration, seals, ledger, verdict engine, cluster bootstrap, canary | 2 | F7 workflow, T2 baselines + kill conditions (rendered from prereg.yaml) | prereg.yaml |
| 6 | Results — age model | 1 | F2b calibration (pred vs true, held-out preps) | ledger |
| 7 | Results — Claim C (placed first among claims on purpose) | 2 | F3 probe panel + canary power curve | ledger |
| 8 | Results — Claim B | 2.5 | F4 trajectories, F5 detection vs BL-5/BL-6, sensitivity table | ledger |
| 9 | Results — Claim A | 1.5 | F6 few-shot curve | ledger |
| 10 | Limitations and threats to validity: feature-level input, rat-only, position confound, compound-dose labels, small lockbox | 1.5 | — | — |
| 11 | Reproducibility: one command, runtime, hardware, ledger audit trail | 0.5 | F8 ledger timeline | ledger |
| — | References, appendix (full ledger summary, amendments) | 1–2 | T3 ledger summary | ledger |

The page total is about 19, so §10 can absorb slack.
