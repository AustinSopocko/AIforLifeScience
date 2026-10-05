"""INVARIANT-1/2/3 tests (WI-04). Required cases — see PLAN.md §5.6 item 5.

(a) a split defined at well level raises InvariantViolation
(b) any prep shared across partitions raises
(c) FeatureTransform.fit on non-train rows raises
(d) treated rows in a pretext dataset raise
(e) property test (hypothesis): random prep>plate>well hierarchies -> partitions cover all preps, pairwise disjoint
(f) SplitPurpose.IDENTITY_PROBE requested outside eval.claim_c_probe raises
"""
import pytest

pytestmark = pytest.mark.skip(reason="WI-04 not implemented")


def test_well_level_split_raises(): ...
def test_shared_prep_raises(): ...
def test_normaliser_fit_on_test_rows_raises(): ...
def test_treated_rows_in_pretext_raise(): ...
def test_random_hierarchy_partitions_disjoint(): ...
def test_identity_probe_purpose_caller_restricted(): ...
