# Age-pretext encoder for neural organ-on-chip electrophysiology

> **Status: planning skeleton (v3). Nothing is implemented yet.** Read [`PLAN.md`](PLAN.md).

**Framing:** the evaluation protocol is the contribution, and Claims A, B and C are its applications.

Culture age (days in vitro) is a free, noise-free label on nearly every MEA recording. We train an
**age-pretext encoder** on spike trains to regress age, then test three pre-registered claims.

| Claim | Corpus | Test |
|---|---|---|
| **A** representation | Wagenaar/Potter 2006 → Kapucu 2022 rat (3 preps, different lab and platform) | Frozen Wagenaar encoder + a head on k labelled Kapucu wells forecasts 7-day-ahead burst rate in a held-out prep. Full curve k = 1–16; primary 4 vs all, against four baselines. |
| **B** readout | EPA NFA 2018 (18 preps; ToxCast dev, NTP sealed lockbox) | Age residual of chronically exposed wells beats firing-rate + burst-rate readouts. This is a cross-corpus replication on summary features. |
| **C** credibility | NFA (primary C1) + Wagenaar (C2) | C1: plate identity within a culture prep (same cells) is not decodable from the readout, while a canary is caught at the pre-declared power. C2: the same test for dissection batch on the encoder. |

Decision rule: a claim survives only if its cluster-bootstrap bound (culture prep as the unit)
beats the **point estimate** of the best pre-declared baseline. There are no absolute thresholds. The submission for every outcome is pre-declared (PLAN §6b).

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
| Wagenaar, Pine & Potter 2006 | Encoder corpus (age, C2) | cite-only |
| US EPA NFA 2018 (Shafer et al. 2019) | Claim B, C1 | EPA ScienceHub |
| Kapucu et al. 2022 | Rat: Claim A transfer target. hPSC: stretch demo (non-inferential). | CC BY 4.0 |

Hardware: one CPU machine (≥ 4 cores, 16 GB RAM, 10 GB disk). No GPU.
