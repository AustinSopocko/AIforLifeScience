"""Live demo driver for the <=5 min video (WI-V). Sequence and timings: demo/STORYBOARD.md.

Contract
--------
`python scripts/demo.py --profile demo` runs, in order and with on-screen pacing:
index (both corpora; prep > culture/plate > recording) -> split (+ a deliberate recording-level split
raising InvariantViolation) -> seal -> ledger verify (+ tamper, verify fails, revert) -> shot 1 (NFA
trajectory reveal) -> shot 2 (Potter forecasting curve fed live by eval.claim_a_fewshot.run_fewshot for
one fold, or a labelled replay of the recorded run) -> shot 3 (Potter batch probe + canary panel) ->
verdict table from ledger rows. Never displays a number not produced by the pipeline or read from the ledger.
"""

if __name__ == "__main__":
    raise SystemExit("not implemented (WI-V)")
