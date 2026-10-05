"""Demo shot 1 / report F4: age-deviation trajectories (WI-12, consumes WI-10 output).

Contract
--------
`select_compound(effects, rule="largest_noncytotoxic_delta_auc_lower_bound")` applies the
pre-declared selection rule (never manual).
`render_trajectory(trajectories, compound, *, reveal_steps=True) -> list[Frame]`: x = DIV
(5, 7, 9, 12); y = Δ in days; control band (median + 95% prep-bootstrap); one line per dose
(sequential colormap), ensemble ± bootstrap ribbons; cytotoxic doses hatched; inset with the BL-5
raw-feature trajectory; caption "no pre-exposure baseline: dosing from DIV 0". With reveal_steps
the frames reveal DIV by DIV, then dose by dose. Static mode returns one frame for the report.
"""


def select_compound(effects, rule: str = "largest_noncytotoxic_delta_auc_lower_bound") -> str:
    raise NotImplementedError("WI-12")


def render_trajectory(trajectories, compound: str, *, reveal_steps: bool = True) -> list:
    raise NotImplementedError("WI-12")
