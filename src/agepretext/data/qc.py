"""Recording-length QC (Phase 2, F1). configs/data/qc.yaml.

Contract
--------
`length_qc(duration_s, duration_source, *, min_duration_s=600, window_s=120) -> (keep, n_windows)`:
- stored length: keep iff duration_s >= min_duration_s; n_windows = floor(duration_s / window_s).
- last_spike (no recorded length): ALWAYS kept, because a short last-spike time cannot separate a silent recording
  from a short one and silence is age information (young plates). n_windows = max(1, floor(duration_s / window_s));
  a recording whose last spike precedes the first window end gets one window, zero after the last spike.
- none / deferred: not spike-level here (NFA) or decided in the confirmatory run (Kapucu) -> (True, None).
`integrity_excluded() -> dict` (Amendment A1): recording_id -> evidence for truncated files, from
configs/data/integrity_exclusions.yaml. A DATA INTEGRITY exclusion, applied before and independently of length_qc.
`old_rule_drop(duration_s, duration_source)` marks the Seal-1 rule (last spike < 600 s) for the reported sensitivity
analysis only.
"""
import math

import yaml


def length_qc(duration_s: float, duration_source: str, *, min_duration_s: float = 600, window_s: float = 120):
    if duration_source == "stored":
        return duration_s >= min_duration_s, int(duration_s // window_s)
    if duration_source == "last_spike":
        return True, max(1, int(duration_s // window_s)) if not math.isnan(duration_s) else 1
    if duration_source in ("none", "deferred"):
        return True, None
    raise ValueError(duration_source)


def old_rule_drop(duration_s: float, duration_source: str, *, min_duration_s: float = 600) -> bool:
    return duration_source == "last_spike" and duration_s < min_duration_s


def integrity_excluded(path: str = "configs/data/integrity_exclusions.yaml") -> dict:
    return dict(yaml.safe_load(open(path))["excluded"])
