# Technical report outline (15–20 pages), v2

Budget: 5 h of the fixed 10 h block (WI-R).
- Build: `agepretext report` (LaTeX).
- Generated inputs: `report/generated/numbers.tex` (macros tied to ledger `row_id`s) and
  figures from `viz/figures.py`.
- CI fails if the prose contains a literal result number.
- Terminology: "age-pretext encoder" only.

| § | Section | Pages | Figures / tables |
|---|---|---|---|
| 1 | Abstract and contributions: one age pretext, three claims, relative decision rule, falsifiable credibility | 1 | — |
| 2 | Problem and impact: maturity readouts for neural organ-on-chip; DNT screening; sponsor digital-twin precondition | 2 | F0 concept (static) |
| 3 | Data and roles: Potter (encoder; A, C), NFA (B, cross-corpus replication), Kapucu (why it cannot be inferential: one prep carries the hPSC series) | 2 | F1 corpora/roles/hierarchy, T1 data and licences |
| 4 | Method: binned spikes, set encoder, log-DIV, cluster-bagged ensemble, cross-fitting; NFA ridge path; shared evaluation core | 2.5 | F2a architecture |
| 5 | Validation protocol: preregistration, relative rule, seals, ledger (incl. A13 genesis row), canary, invariants | 2 | F7 workflow, T2 hypotheses/baselines (rendered from prereg.yaml) |
| 6 | Age prerequisite (both corpora) | 1 | F2b calibration by DIV bin |
| 7 | Claim C (first among claims) | 2 | F3 probe + canary |
| 8 | Claim A | 1.5 | F6 forecasting curve |
| 9 | Claim B | 2 | F4 trajectories, F5 detection vs BL-B1/B2 (B3 reported), sensitivity table incl. plate-clustered |
| 10 | Limitations: biology-vs-artefact in batch identity; feature-only NFA; rat-only core; column-2 confound; human data cannot support inference; no hyperparameter tuning in P (deliberate) | 1.5 | — |
| 11 | Reproducibility | 0.5 | F8 ledger timeline |
| — | References, appendix (ledger summary, cut-order decisions, amendments) | 1–2 | T3 |
