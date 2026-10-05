"""Cluster bootstrap with the culture prep as the unit (WI-06).

Contract
--------
`cluster_bootstrap(df, statistic, *, cluster_col="prep_id", n_resamples=4000, ci=0.95, seed)`
resamples CLUSTERS with replacement (each resampled cluster contributes all its rows, with a
fresh cluster label so duplicates are distinct), recomputes `statistic(df_resampled)`, and
returns BootstrapResult(point, lower, upper, n_clusters, resamples). Percentile intervals.
`paired_cluster_bootstrap(df, stat_a, stat_b, ...)` resamples once and evaluates both on the
same resample (for differences such as ours-minus-baseline).
Validation (WI-06 acceptance): coverage 95% ± 3% over 500 synthetic simulations with known effect.
Refuses to run with fewer than 5 clusters (raises) — such results must be labelled qualitative
and use a different procedure.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class BootstrapResult:
    point: float
    lower: float
    upper: float
    n_clusters: int
    n_resamples: int


def cluster_bootstrap(df, statistic, *, cluster_col: str = "prep_id", n_resamples: int = 4000,
                      ci: float = 0.95, seed: int = 0) -> BootstrapResult:
    raise NotImplementedError("WI-06")


def paired_cluster_bootstrap(df, stat_a, stat_b, *, cluster_col: str = "prep_id",
                             n_resamples: int = 4000, ci: float = 0.95, seed: int = 0) -> BootstrapResult:
    raise NotImplementedError("WI-06")
