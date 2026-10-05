"""Demo shot 2 / report F6: few-shot curve filling in live (WI-12, consumes WI-11 generator).

Contract
--------
`LiveCurve(methods, k_values)`; `.update(event: FewShotEvent)` adds a point and redraws;
`.frame()` returns the current Frame. x = labelled wells (log scale), y = AUROC; ours, BL-2,
BL-3, BL-4 with CI ribbons once >= 10 draws exist at a k; a horizontal guide at "best from-scratch
@ k=50" and a verdict badge from eval.verdicts once complete. `replay(events, pacing)` replays a
recorded run at the same timing with an on-screen "replay of run <row_id>" label.
"""


class LiveCurve:
    def __init__(self, methods: list, k_values: list):
        raise NotImplementedError("WI-12")
