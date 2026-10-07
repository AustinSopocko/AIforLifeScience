"""Phase 2: paired cluster bootstrap, paired verdict rule, cluster-weighted MAE, Seal-1 archive integrity, prereg v4."""
import hashlib
import json

import numpy as np
import pandas as pd
import pytest
import yaml

from agepretext.eval.bootstrap import TooFewClusters, cluster_weighted_mae, paired_cluster_bootstrap
from agepretext.eval.verdicts import verdict
from agepretext.validation.protocol import _canonical


def _df(effect, n_lab=3, n_cl=6, n_rec=5, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for L in range(n_lab):
        for c in range(n_cl):
            u = rng.normal(0, 0.3)                       # cluster random effect shared by both methods (pairing)
            for _ in range(n_rec):
                y = rng.normal(2, 0.5)
                rows.append(dict(lab=f"L{L}", cluster_id=f"L{L}:{c}", y_true_log_div=y,
                                 a=y + u + rng.normal(0, 0.1), b=y + u + effect + rng.normal(0, 0.1)))
    return pd.DataFrame(rows)


def test_paired_detects_effect_unpaired_noise_cancels():
    d = _df(effect=0.3)
    r = paired_cluster_bootstrap(d, lambda x: (x.a - x.y_true_log_div).abs().mean(),
                                 lambda x: (x.b - x.y_true_log_div).abs().mean(),
                                 cluster_col="cluster_id", strata_col="lab", n_resamples=300, seed=1)
    assert r.upper < 0 and r.n_clusters == 18


def test_stratified_requires_min_clusters_per_stratum():
    d = _df(effect=0.3, n_cl=4)
    with pytest.raises(TooFewClusters):
        paired_cluster_bootstrap(d, lambda x: 0.0, lambda x: 0.0, cluster_col="cluster_id", strata_col="lab",
                                 n_resamples=10)


def test_cluster_weighted_mae_weights_clusters_and_labs_equally():
    d = pd.DataFrame(dict(cluster_id=["a"] * 9 + ["b"], lab=["X"] * 9 + ["Y"], y_true_log_div=0.0,
                          p=[1.0] * 9 + [3.0]))
    assert cluster_weighted_mae(d, "p") == 2.0
    assert cluster_weighted_mae(d, "p", strata_col="lab") == 2.0
    assert d.p.abs().mean() == pytest.approx(1.2)


def test_paired_verdict_requires_every_gating_baseline():
    from agepretext.eval.bootstrap import BootstrapResult as B
    pre = yaml.safe_load(open("protocol/prereg.yaml"))
    good, bad = B(-0.05, -0.08, -0.01, 8, 4000), B(-0.02, -0.06, 0.01, 8, 4000)
    assert verdict("H-AGE-K", {"paired": {"BL-0": good, "BL-1": good}}, pre).label == "SUPPORTS"
    assert verdict("H-AGE-K", {"paired": {"BL-0": good, "BL-1": bad}}, pre).label == "REFUTES"
    assert verdict("primary", {"paired": {"BL-0": good, "BL-1": None}}, pre).label == "INCONCLUSIVE"


def test_b2_requires_detection_and_paired_lower_bound():
    from agepretext.eval.bootstrap import BootstrapResult as B
    pre = yaml.safe_load(open("protocol/prereg.yaml"))
    up = B(0.4, 0.1, 0.7, 10, 4000)
    both = {"BL-B1g": up, "BL-B2g": up}
    assert verdict("H-B2", {"paired": both, "null_p": 0.01}, pre).label == "SUPPORTS"
    assert verdict("H-B2", {"paired": both, "null_p": 0.08}, pre).label == "REFUTES"
    assert verdict("H-B2", {"paired": {**both, "BL-B2g": B(0.1, -0.1, 0.3, 10, 4000)}, "null_p": 0.01}, pre).label == "REFUTES"


def test_seal_policy_allows_only_architecture_changes():
    from agepretext.validation.protocol import SealRecord, check_seal_policy
    s1 = SealRecord("seal-1", "h1", "p", "c", "t", {})
    s2 = SealRecord("seal-2", "h2", "p", "c", "t", {"protocol/prereg.yaml": "a", "configs/model/set_encoder.yaml": "b"})
    check_seal_policy({"protocol/prereg.yaml": "a", "configs/model/set_encoder.yaml": "B2",
                       "configs/train/sampling.yaml": "n"}, [s1, s2])
    with pytest.raises(RuntimeError):
        check_seal_policy({"protocol/prereg.yaml": "CHANGED", "configs/model/set_encoder.yaml": "b"}, [s1, s2])
    with pytest.raises(RuntimeError):
        check_seal_policy({"protocol/prereg.yaml": "a", "configs/model/set_encoder.yaml": "b",
                           "splits/new.json": "x"}, [s1, s2])


def test_seal1_components_verifiable_by_content():
    seal = json.load(open("protocol/seals/seal-1.json"))["components"]
    archived = {"PREREGISTRATION.md": "protocol/archive/seal-1/PREREGISTRATION.md",
                "protocol/prereg.yaml": "protocol/archive/seal-1/prereg.yaml",
                "configs/splits.yaml": "protocol/archive/seal-1/splits.yaml"}
    for path, h in seal.items():
        src = archived.get(path, path)
        assert hashlib.sha256(_canonical(src)).hexdigest() == h, path


def test_prereg_v5_ready_for_seal_2():
    pre = yaml.safe_load(open("protocol/prereg.yaml"))
    assert pre["schema_version"] == 5 and not pre["open_decisions"]
    assert "TBD_SEAL2" not in open("protocol/prereg.yaml").read()
    assert pre["decision_rule"]["name"] == "paired_vs_each_gating_baseline"
    assert pre["dev_evaluation"]["primary"]["folds"] == ["eglen_grant", "epa_shafer", "potter_gatech"]
    fx = pre["data_roles"]["confirmatory"]["fragilex"]
    idx = pd.read_parquet("data/processed/recording_index.parquet") if __import__("os").path.exists(
        "data/processed/recording_index.parquet") else None
    if idx is not None:
        f = idx[idx.source == "fragilex"]
        assert sorted(f[f.genotype == "wt"].cluster_id.unique()) == fx["wt"]
        assert sorted(f[f.genotype == "fmr1_ko"].cluster_id.unique()) == fx["ko"]


def test_f2_selection_copied_into_prereg():
    pre = yaml.safe_load(open("protocol/prereg.yaml"))["features"]["selected"]
    cfg = yaml.safe_load(open("configs/features/burst_calibration.yaml"))["selected"]
    assert pre == cfg and cfg["multiwell_64"] == cfg["mcs_8x8"]
