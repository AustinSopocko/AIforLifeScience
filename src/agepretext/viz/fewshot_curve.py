"""Demo shot 2 / report F6: Claim A forecasting curve filling in live (WI-O1, consumes WI-P5 events).

Contract
--------
`LiveCurve(methods, k_values)`; `.update(event: FewShotEvent)` adds a point and redraws; `.frame()`
returns the current Frame. x = labelled cultures (log scale, 1..all), y = forecasting MAE (lower is
better); ours, BL-A0..A3 with batch-clustered CI ribbons once >= 10 draws exist at a k; a horizontal
guide at "best baseline @ k=all (point)" and, at k=4, ours' upper bound marker — the visual form of the
relative rule — plus the verdict badge from eval.verdicts when complete. `replay(events, pacing)`
replays a recorded run with an on-screen "replay of run <row_id>" label.
"""


class LiveCurve:
    def __init__(self, methods: list, k_values: list):
        raise NotImplementedError("WI-O1")
