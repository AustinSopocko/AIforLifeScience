"""Demo shot 1 / report F7: NFA age-deviation trajectories (WI-O1, consumes WI-N3 output).

Contract
--------
`select_compound(effects, rule="largest_noncytotoxic_delta_auc_lower_bound_ntp")` applies the
pre-declared rule on confirmatory NTP results (never manual).
`render_trajectory(trajectories, compound, *, reveal_steps=True) -> list[Frame]`: x = DIV (5,7,9,12);
y = Δ in days; control band (median + 95% prep-bootstrap); one line per dose (sequential colormap) with
ensemble +/- bootstrap ribbons; cytotoxic doses hatched; inset = BL-B1 (firing+burst age residual) for
the same compound; caption "dosing from DIV 0 — no pre-exposure recording". reveal_steps animates DIV by
DIV, then dose by dose; static mode returns one frame for the report.
"""


def select_compound(effects, rule: str = "largest_noncytotoxic_delta_auc_lower_bound_ntp") -> str:
    raise NotImplementedError("WI-O1")


def render_trajectory(trajectories, compound: str, *, reveal_steps: bool = True) -> list:
    raise NotImplementedError("WI-O1")
