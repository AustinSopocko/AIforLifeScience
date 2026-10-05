"""INVARIANT-1 tests (WI-03) on a synthetic prep > plate > well hierarchy, plus the committed manifests."""
import glob

import pandas as pd
import pytest

from agepretext.data.index import RecordingIndex
from agepretext.data.splits import SplitManifest, make_group_splits
from agepretext.invariants import InvariantViolation, SplitPurpose, assert_controls_only, assert_group_disjoint


def _idx():
    rows = [dict(recording_id=f"r{p}{w}{d}", source="s", prep_id=f"p{p}", plate_id=f"pl{p}", well_id=f"w{p}{w}", div=d,
                 species="rat", electrodes=16, is_control=True, dose_uM=0.0, inferential=True, payload="x",
                 compound=None, subset="TC" if p < 4 else "NTP", row=None, col=None)
            for p in range(6) for w in range(3) for d in (5, 7)]
    return RecordingIndex(pd.DataFrame(rows))


def test_crossfit_partitions_preps():
    m = make_group_splits(_idx(), name="t", source="s", unit="prep", purpose=SplitPurpose.PRETEXT_CROSSFIT, seed=1, n_folds=3)
    tests = sorted(p for f in m.folds.values() for p in f["test"])
    assert tests == sorted(f"p{i}" for i in range(6))


def test_shared_prep_raises():
    m = SplitManifest("t", "s", SplitPurpose.LOCKBOX, "prep", 0, {"dev": ["p0", "p1"], "lockbox": ["p1"]}, {})
    with pytest.raises(InvariantViolation):
        assert_group_disjoint(m, _idx())


def test_fold_overlap_raises():
    m = SplitManifest("t", "s", SplitPurpose.PRETEXT_CROSSFIT, "prep", 0, {"all": ["p0", "p1"]},
                      {"f0": {"train": ["p0", "p1"], "test": ["p1"]}, "f1": {"train": ["p1"], "test": ["p0"]}})
    with pytest.raises(InvariantViolation):
        assert_group_disjoint(m, _idx())


def test_non_prep_unit_refused():
    with pytest.raises(ValueError):
        make_group_splits(_idx(), name="t", source="s", unit="well", purpose=SplitPurpose.PRETEXT_CROSSFIT, seed=1, n_folds=2)


def test_identity_probe_purpose_caller_restricted():
    m = SplitManifest("t", "s", SplitPurpose.IDENTITY_PROBE, "prep", 0, {}, {})
    with pytest.raises(InvariantViolation):
        assert_group_disjoint(m, _idx())


def test_treated_rows_in_age_training_raise():
    t = _idx().table.assign(dose_uM=1.0)
    with pytest.raises(InvariantViolation):
        assert_controls_only(t)


def test_committed_manifests_hash_valid():
    paths = glob.glob("splits/*.json")
    assert len(paths) == 4
    for p in paths:
        SplitManifest.from_json(p)
