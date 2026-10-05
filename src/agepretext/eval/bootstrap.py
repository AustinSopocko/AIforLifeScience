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
                      ci: float = 0.95, seed: int = 0) -> BootstrapResult:
    raise NotImplementedError("WI-04")


def paired_cluster_bootstrap(df, stat_a, stat_b, *, cluster_col: str, n_resamples: int = 4000,
                             ci: float = 0.95, seed: int = 0) -> BootstrapResult:
    raise NotImplementedError("WI-04")
