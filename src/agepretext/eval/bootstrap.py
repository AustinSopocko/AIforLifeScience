"""Cluster bootstrap with the culture prep as unit (WI-04). Shared.

Contract
--------
`cluster_bootstrap(df, statistic, *, cluster_col, n_resamples=4000, ci=0.95, seed)` resamples CLUSTERS
with replacement (resampled duplicates get fresh cluster labels), recomputes `statistic`, and returns
BootstrapResult(point, lower, upper, n_clusters, n_resamples). Percentile intervals.
`paired_cluster_bootstrap(df, stat_a, stat_b, ...)` evaluates both statistics on the same resample.
Headline cluster_col = prep (Potter batch, NFA culture date); sensitivity = culture / plate.
Raises TooFewClusters when n_clusters < prereg.statistics.bootstrap.min_clusters (5); callers map
that to INCONCLUSIVE (this is why Kapucu cannot be inferential: PLAN §2.2).
Acceptance: 95% +/- 3% coverage over 500 synthetic simulations with a known effect and ICC > 0.
"""
from dataclasses import dataclass


class TooFewClusters(RuntimeError):
    pass


@dataclass(frozen=True)
class BootstrapResult:
    point: float
    lower: float
    upper: float
    n_clusters: int
    n_resamples: int


def cluster_bootstrap(df, statistic, *, cluster_col: str, n_resamples: int = 4000,
                      ci: float = 0.95, seed: int = 0, min_clusters: int = 5) -> BootstrapResult:
    import numpy as np
    import pandas as pd
    groups = {k: g for k, g in df.groupby(cluster_col)}
    keys = sorted(groups)
    if len(keys) < min_clusters:
        raise TooFewClusters(f"{len(keys)} clusters < {min_clusters}")
    rng = np.random.default_rng(seed)
    stats = []
    for _ in range(n_resamples):
        pick = rng.integers(0, len(keys), len(keys))
        stats.append(statistic(pd.concat([groups[keys[i]] for i in pick], ignore_index=True)))
    a = (1 - ci) / 2
    return BootstrapResult(float(statistic(df)), float(np.quantile(stats, a)), float(np.quantile(stats, 1 - a)),
                           len(keys), n_resamples)


def paired_cluster_bootstrap(df, stat_a, stat_b, *, cluster_col: str, n_resamples: int = 4000,
                             ci: float = 0.95, seed: int = 0) -> BootstrapResult:
    raise NotImplementedError("WI-04")
