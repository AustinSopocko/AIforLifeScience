# Age-pretext encoder for neural organ-on-chip electrophysiology

> **Status: planning skeleton. Nothing is implemented yet.** Read [`PLAN.md`](PLAN.md) first.

Culture age (days in vitro) is a free, noise-free label on nearly every public MEA recording.
We train a small model to regress age from spontaneous network activity and test three
pre-registered claims from that single training run:

- **A (representation):** the frozen embedding transfers few-shot to an unseen task.
- **B (readout):** predicted-minus-true age is a perturbation readout ("functionally younger").
- **C (credibility):** the representation does not encode plate or batch identity. A
  power-calibrated probe plus canary tests this.

Validation infrastructure is a first-class deliverable:
- [`PREREGISTRATION.md`](PREREGISTRATION.md) and [`protocol/prereg.yaml`](protocol/prereg.yaml):
  hypotheses, baselines, nulls and kill conditions, sealed before results exist.
- [`ledger/`](ledger/SCHEMA.md): append-only, hash-chained results ledger. Every run is
  recorded.
- Sealed protocol hashes are required for every evaluation run.

## Quickstart (target behaviour, WI-14)

```bash
conda env create -f environment.yml && conda activate agepretext
pip install -e .
bash reproduce.sh --profile mvr      # fetch -> index -> split -> verify seals -> train -> eval -> figures -> report
agepretext ledger verify             # audit the results ledger
```

## Data (downloaded from origin at runtime; never committed)

| Source | Use | Licence |
|---|---|---|
| US EPA Network Formation Assay 2018 (Shafer et al. 2019) | MVR: all three claims | EPA ScienceHub |
| Wagenaar, Pine & Potter 2006 | stretch: multi-source pretext | cite-only |
| Kapucu et al. 2022 (G-Node) | stretch: hPSC transfer | CC BY 4.0 |
| Cotterill et al. 2016 (EPAmeadev) | stretch: extractor validation | cite-only |

## Hardware

Single CPU machine: 4 cores, 16 GB RAM, about 5 GB disk for the MVR. No GPU required.

## Repository map

See `PLAN.md` §14.
