"""Demo shot 2 (REQUIRED) / report F6: Claim A full few-shot curve, built progressively (WI-O1, WI-P5 events).

Contract
--------
`LiveCurve(methods, k_values)`; `.update(event: FewShotEvent)` adds a point and redraws; `.frame()`
returns the current Frame. One panel per held-out Kapucu rat prep; x = labelled wells (log scale:
1, 2, 4, 8, 16, all), y = forecasting MAE (lower is better); ours, BL-A0..A3 with well-level bootstrap
ribbons; a horizontal guide at "best baseline @ k=all (point)" and ours' upper-bound marker at k=4 in each
panel — the worst-fold rule made visible — plus the H-A verdict badge when complete. `replay(events, pacing)`
replays a recorded run with an on-screen "replay of run <row_id>" label.
"""


class LiveCurve:
    def __init__(self, methods: list, k_values: list):
        raise NotImplementedError("WI-O1")
