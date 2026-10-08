"""Cluster bootstrap with the culture prep as unit (WI-04). Shared.

Contract
--------
`cluster_bootstrap(df, statistic, *, cluster_col, n_resamples=4000, ci=0.95, seed)` resamples CLUSTERS
with replacement (resampled duplicates get fresh cluster labels), recomputes `statistic`, and returns
BootstrapResult(point, lower, upper, n_clusters, n_resamples). Percentile intervals.
`paired_cluster_bootstrap(df, stat_a, stat_b, *, cluster_col, strata_col=None, ...)` returns the interval of
stat_a - stat_b, both evaluated on the SAME resample (Phase 2 paired rule). With `strata_col` (LOLO: lab) clusters are
resampled within each stratum, so every resample keeps every stratum; min_clusters then applies per stratum.
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


def paired_cluster_bootstrap(df, stat_a, stat_b, *, cluster_col: str, strata_col: str | None = None,
                             n_resamples: int = 4000, ci: float = 0.95, seed: int = 0,
                             min_clusters: int = 5) -> BootstrapResult:
    import numpy as np
    import pandas as pd
    groups = {k: g for k, g in df.groupby(cluster_col)}
    if strata_col is None:
        strata = {None: sorted(groups)}
    else:
        strata = {}
        for k, g in groups.items():
            s = g[strata_col].unique()
            if len(s) != 1:
                raise ValueError(f"cluster {k} spans strata {list(s)}")
            strata.setdefault(s[0], []).append(k)
        strata = {s: sorted(v) for s, v in sorted(strata.items())}
    if min(len(v) for v in strata.values()) < min_clusters:
        raise TooFewClusters(f"{ {s: len(v) for s, v in strata.items()} } clusters < {min_clusters} in some stratum")
    rng = np.random.default_rng(seed)
    diff = lambda d: stat_a(d) - stat_b(d)
    stats = []
    for _ in range(n_resamples):
        parts = []
        for keys in strata.values():
            for j, i in enumerate(rng.integers(0, len(keys), len(keys))):
                parts.append(groups[keys[i]].assign(**{cluster_col: f"{keys[i]}#{len(parts)}"}))
        stats.append(diff(pd.concat(parts, ignore_index=True)))
    a = (1 - ci) / 2
    return BootstrapResult(float(diff(df)), float(np.quantile(stats, a)), float(np.quantile(stats, 1 - a)),
                           len(groups), n_resamples)


def cluster_weighted_mae(df, pred_col: str, *, true_col: str = "y_true_log_div", cluster_col: str = "cluster_id",
                         strata_col: str | None = None) -> float:
    """Phase 2 error weighting: mean over clusters of within-cluster mean |error|; with strata_col (LOLO: lab), the
    mean over strata of that quantity (each lab equal)."""
    e = (df[pred_col] - df[true_col]).abs()
    per_cluster = e.groupby(df[cluster_col]).mean()
    if strata_col is None:
        return float(per_cluster.mean())
    lab = df.groupby(cluster_col)[strata_col].first()
    return float(per_cluster.groupby(lab).mean().mean())


def paired_cluster_mae_bootstrap(df, pred_a: str, pred_b: str, *, true_col: str = "y_true_log_div",
                                 cluster_col: str = "cluster_id", strata_col: str | None = None, n_resamples: int = 4000,
                                 ci: float = 0.95, seed: int = 0, min_clusters: int = 5) -> BootstrapResult:
    """Exact fast path of paired_cluster_bootstrap for stat = cluster_weighted_mae (lab-equal with strata_col): the
    statistic is linear in per-cluster mean |error|, so each resample is a mean over drawn clusters. Draw order is
    identical to paired_cluster_bootstrap (strata sorted, clusters sorted within stratum), so results match exactly."""
    import numpy as np
    e = df.assign(_a=(df[pred_a] - df[true_col]).abs(), _b=(df[pred_b] - df[true_col]).abs())
    per = e.groupby(cluster_col).agg(a=("_a", "mean"), b=("_b", "mean"),
                                     s=(strata_col, "first") if strata_col else ("_a", lambda x: 0))
    per["d"] = per.a - per.b
    strata = {s_: sorted(g.index) for s_, g in per.groupby("s")} if strata_col else {None: sorted(per.index)}
    if min(len(v) for v in strata.values()) < min_clusters:
        raise TooFewClusters(f"{ {s_: len(v) for s_, v in strata.items()} } clusters < {min_clusters} in some stratum")
    dv = {s_: per.loc[k, "d"].to_numpy() for s_, k in strata.items()}
    rng = np.random.default_rng(seed)
    stats = np.empty(n_resamples)
    for r in range(n_resamples):
        stats[r] = np.mean([dv[s_][rng.integers(0, len(dv[s_]), len(dv[s_]))].mean() for s_ in strata])
    point = float(np.mean([v.mean() for v in dv.values()]))
    a = (1 - ci) / 2
    return BootstrapResult(point, float(np.quantile(stats, a)), float(np.quantile(stats, 1 - a)), len(per), n_resamples)