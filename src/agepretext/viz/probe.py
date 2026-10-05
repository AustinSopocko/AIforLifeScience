"""Demo shot 3 / report F5: Claim C panel — C1 (NFA plate within prep) and C2 (Wagenaar batch), each
beside its canary (WI-O1, consumes WI-N4 and WI-P4 output).

Contract
--------
`render_probe_panel(c1, c2, overlay=None) -> Frame`: left half = C1: plate confusion on Δ for the
pre-declared prep (the prep with most plates; tie -> lowest id) beside its canary (seed 0), null histogram
with observed excess balanced accuracy, canary power k/20 vs 0.8. Right half = C2: 8 x 8 batch confusion on
z for the DIV bin with most recordings beside its canary, null, power k/10 vs 0.8. Verdict badges from
eval.verdicts; C1 labelled PRIMARY.
Overlay text (seal hash, `ledger verify` output) is passed in, never computed here.
"""


def render_probe_panel(probe_results: dict, canary_results: dict, overlay: str | None = None):
    raise NotImplementedError("WI-O1")
