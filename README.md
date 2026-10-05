# Age-pretext encoder for neural organ-on-chip electrophysiology

> **Status: planning skeleton (v2). Nothing is implemented yet.** Read [`PLAN.md`](PLAN.md).

Culture age (days in vitro) is a free, noise-free label on nearly every MEA recording. We train an
**age-pretext encoder** on spike trains to regress age, then test three pre-registered claims.

| Claim | Corpus | Test |
|---|---|---|
| **A** representation | Wagenaar/Potter 2006 (8 batches, 30 cultures) | Frozen embedding + a 4-culture head forecasts held-out-batch network-burst rate 7 days ahead, better than every baseline trained on all cultures |
| **B** readout | EPA NFA 2018 (18 preps; ToxCast dev, NTP sealed lockbox) | Age residual of chronically exposed wells beats firing-rate + burst-rate readouts. This is a cross-corpus replication on summary features. |
| **C** credibility | Wagenaar/Potter | A linear probe does not detect dissection-batch identity, while a synthetic batch artefact (canary) is detected at the pre-declared power |

Decision rule: a claim survives only if its cluster-bootstrap bound (culture prep as the unit)
beats the **point estimate** of the best pre-declared baseline. There are no absolute thresholds.

Validation infrastructure is a first-class deliverable:
- [`PREREGISTRATION.md`](PREREGISTRATION.md) and [`protocol/prereg.yaml`](protocol/prereg.yaml).
- A hash-chained append-only ledger ([`ledger/`](ledger/SCHEMA.md)). Row 1 is a pre-split
  disclosure.
- Sealed protocol hashes are required for every evaluation run.

## Quickstart (target behaviour)

```bash
conda env create -f environment.yml && conda activate agepretext
pip install -e .
bash reproduce.sh --profile mvr      # ≈2 h on 4 CPU cores
agepretext ledger verify
```

## Data (downloaded from origin at runtime; never committed)

| Source | Role | Licence |
|---|---|---|
| Wagenaar, Pine & Potter 2006 | Encoder corpus (A, C) | cite-only |
| US EPA NFA 2018 (Shafer et al. 2019) | Claim B | EPA ScienceHub |
| Kapucu et al. 2022 | Stretch: human transfer demo (non-inferential) | CC BY 4.0 |

Hardware: one CPU machine (≥ 4 cores, 16 GB RAM, 10 GB disk). No GPU.
