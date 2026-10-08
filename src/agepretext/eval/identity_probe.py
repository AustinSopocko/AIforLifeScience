"""Shared identity-probe + canary engine for Claim C (WI-04). Used by C1 (NFA) and C2 (Wagenaar).

Contract
--------
- `probe(reprs, labels, groups, split_spec, cfg) -> ProbeResult`: multinomial logistic probe (inner-CV
  regularisation) predicting identity `labels` (plate or batch) within each stratum in `groups`
  (prep for C1, DIV bin for C2), under `split_spec` — the only callers allowed to request
  SplitPurpose.IDENTITY_PROBE:
      "leave_one_well_out_within_plate"  (C1, exception 2)
      "culture_within_batch"             (C2, exception 1)
  Statistic = excess balanced accuracy (observed - permutation-null mean) pooled over strata;
  p from cfg.permutations grouped permutations (eval.nulls.grouped_label_permutation at the declared
  level: well-within-prep for C1, culture for C2). Returns confusion matrices per stratum.
- `canary_power(run_pipeline_with_canary, seeds, cfg) -> CanaryResult`: for each seed, calls the
  caller-supplied closure that injects the canary, re-runs the FULL upstream pipeline (C1: transform +
  ridge refit + Δ; C2: encoder retrain + re-embed) and probes; power = share of seeds with p < alpha.
- Verdict is NOT computed here: eval.verdicts applies the identity rule from prereg.yaml.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ProbeResult:
    excess_balanced_accuracy: float
    p_value: float
    n_strata: int
    confusion: dict


@dataclass(frozen=True)
class CanaryResult:
    power: float
    detected_per_seed: tuple


def probe(reprs, labels, groups, split_spec: str, cfg) -> ProbeResult:
    raise NotImplementedError("WI-04")


def canary_power(run_pipeline_with_canary, seeds, cfg) -> CanaryResult:
    raise NotImplementedError("WI-04")


def group_probe(Z, labels, groups, *, k: int = 4, seed: int = 20261007, n_perm: int = 1000, perm_seed: int = 20261006,
                strata=None, cs=(0.01, 0.1, 1.0, 10.0), n_jobs: int = 1) -> ProbeResult:
    """Phase 2/3 H-LAB probe (and its pseudo-lab canary). Recordings are rows; `groups` = cluster_id (no cluster crosses
    folds: ordinary grouped CV, not an IDENTITY_PROBE exception). Multinomial logistic on fold-standardised Z, C chosen by
    inner 3-fold grouped CV; outer StratifiedGroupKFold(k) on `labels` (or on `strata`+label when given). Sample weights
    make every cluster equal; balanced accuracy uses the same weights. Statistic = observed BA - mean permutation BA;
    permutations reassign labels across clusters (within each stratum when `strata` is given), re-running the whole probe;
    p = (1 + #{perm >= observed}) / (1 + n_perm)."""
    import warnings
    import numpy as np
    from joblib import Parallel, delayed
    warnings.filterwarnings("ignore", message="y_pred contains classes not in y_true")
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import balanced_accuracy_score
    from sklearn.model_selection import StratifiedGroupKFold
    from sklearn.preprocessing import StandardScaler

    Z, y, g = np.asarray(Z, float), np.asarray(labels), np.asarray(groups)
    st = np.asarray(strata) if strata is not None else None
    w = 1.0 / np.unique(g, return_inverse=True, return_counts=True)[2][np.unique(g, return_inverse=True)[1]]
    cl = np.unique(g)
    cl_strat = None if st is None else {c: st[g == c][0] for c in cl}

    def fit_predict(Xtr, ytr, gtr, wtr, Xte):
        sc = StandardScaler().fit(Xtr); Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)
        best, bc = -1.0, cs[0]
        inner = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=seed)
        for c in cs:
            acc = []
            for a, b in inner.split(Xtr, ytr, gtr):
                if len(np.unique(ytr[a])) < 2:
                    continue
                m = LogisticRegression(C=c, max_iter=500).fit(Xtr[a], ytr[a], sample_weight=wtr[a])
                acc.append(balanced_accuracy_score(ytr[b], m.predict(Xtr[b]), sample_weight=wtr[b]))
            if acc and np.mean(acc) > best:
                best, bc = float(np.mean(acc)), c
        return LogisticRegression(C=bc, max_iter=500).fit(Xtr, ytr, sample_weight=wtr).predict(Xte)

    def run(yy):
        warnings.filterwarnings("ignore", message="y_pred contains classes not in y_true")
        key = yy if st is None else np.char.add(st.astype(str), yy.astype(str))
        pred = np.empty_like(yy)
        for tr, te in StratifiedGroupKFold(n_splits=k, shuffle=True, random_state=seed).split(Z, key, g):
            pred[te] = fit_predict(Z[tr], yy[tr], g[tr], w[tr], Z[te])
        return balanced_accuracy_score(yy, pred, sample_weight=w), pred

    obs, pred = run(y)
    rng = np.random.default_rng(perm_seed)
    cl_label = {c: y[g == c][0] for c in cl}
    perms = []
    for _ in range(n_perm):
        if st is None:
            lab = dict(zip(cl, rng.permutation([cl_label[c] for c in cl])))
        else:
            lab = {}
            for s_ in sorted(set(cl_strat.values())):
                cs_ = [c for c in cl if cl_strat[c] == s_]
                lab.update(zip(cs_, rng.permutation([cl_label[c] for c in cs_])))
        perms.append(np.array([lab[c] for c in g]))
    null = Parallel(n_jobs=n_jobs)(delayed(lambda yy: run(yy)[0])(yy) for yy in perms)
    null = np.asarray(null)
    labs = np.unique(y)
    conf = {str(a): {str(b): float(w[(y == a) & (pred == b)].sum() / w[y == a].sum()) for b in labs} for a in labs}
    return ProbeResult(float(obs - null.mean()), float((1 + (null >= obs).sum()) / (1 + n_perm)), int(len(cl)),
                       {"observed_ba": float(obs), "null_mean_ba": float(null.mean()), "null_q95_ba": float(np.quantile(null, 0.95)),
                        "per_class_recall_weighted": conf})
