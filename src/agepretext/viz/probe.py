"""Demo shot 3 / report F3: identity probe failing next to a canary that succeeds (WI-12).

Contract
--------
`render_probe_panel(probe_results, canary_results) -> Frame`: left = plate-identity confusion
matrix on z for one pre-declared prep (the prep with most plates; tie -> lowest id); middle =
same probe on canary-injected inputs (0.5 SD); right = permutation-null histogram with observed
excess balanced accuracy marked + canary power curve across magnitudes with the 0.8 power line.
Terminal overlay text (seal hash, `ledger verify` result) is passed in, not computed here.
"""


def render_probe_panel(probe_results: dict, canary_results: dict, overlay: str | None = None):
    raise NotImplementedError("WI-12")
