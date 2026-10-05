"""Demo shot 3 / report F3: batch probe fails while the canary is caught (WI-O1, consumes WI-P4 output).

Contract
--------
`render_probe_panel(probe_results, canary_results, overlay=None) -> Frame`: left = real-batch confusion
matrix (8 x 8) on primary z for the pre-declared DIV bin (the bin with the most recordings); middle =
the same probe after canary retraining (seed 0); right = culture-level permutation null with the observed
excess balanced accuracy marked, and canary power (k/10 seeds detected) against the 0.8 requirement.
Overlay text (seal hash, `ledger verify` output) is passed in, never computed here.
"""


def render_probe_panel(probe_results: dict, canary_results: dict, overlay: str | None = None):
    raise NotImplementedError("WI-O1")
