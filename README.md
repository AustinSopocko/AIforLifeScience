# Age-pretext encoder for organ-on-chip neural electrophysiology

An encoder trained to predict culture age (days in vitro) from spontaneous MEA spike trains, used as a
general representation of neural culture state, and evaluated under a pre-registered, falsification-first protocol.

**Claims**
- **A (representation):** the frozen encoder, trained on Wagenaar/Potter rat cultures, transfers few-shot to another lab's rat cultures (Kapucu 2022): full curve k = 1–16 labelled wells, 4 vs all is primary.
- **B (readout):** predicted-minus-true age detects chronic chemical exposure in the EPA network formation assay better than a firing-rate + burst-rate readout.
- **C (credibility):** plate identity within a culture prep is not decodable from the readout (C1, primary), and dissection batch is not decodable from the encoder (C2), each with a canary that must be detected.

**Run** (CPU-only, Python 3.11; tested on 4 cores / 15 GB):
```bash
python3.11 -m venv .venv && . .venv/bin/activate
pip install -r requirements.lock && pip install -e . --no-deps
bash reproduce.sh            # entry point; currently prints the artefact manifest (all TODO)
```

**Status:** S0, a skeleton. Modules are docstring-contract stubs, and `reproduce.sh` lists every artefact as TODO.
Plan: [`PLAN.md`](PLAN.md) · Preregistration: [`PREREGISTRATION.md`](PREREGISTRATION.md) ([`protocol/prereg.yaml`](protocol/prereg.yaml)).
