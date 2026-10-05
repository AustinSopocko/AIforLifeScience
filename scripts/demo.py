"""Live demo driver for the <=5 min video (WI-15). Sequence and timings: demo/STORYBOARD.md.

Contract
--------
`python scripts/demo.py --profile demo` runs, in order and with on-screen pacing:
index -> split (+ deliberate well-level split raising InvariantViolation) -> seal -> ledger verify
(+ tamper/verify-fail/revert) -> shot 1 (trajectory reveal) -> shot 2 (few-shot curve fed live by
eval.claim_a_fewshot.run_fewshot, or replay of a recorded run labelled as such) -> shot 3 (probe
panel) -> verdict table from confirmatory ledger rows. Never displays a number not produced by
the pipeline or read from the ledger.
"""

if __name__ == "__main__":
    raise SystemExit("not implemented (WI-15)")
