"""Statistics core tests (WI-06).

- cluster bootstrap coverage 95% +/- 3% over 500 synthetic sims with known effect and ICC > 0
- naive (row-level) bootstrap on the same sims under-covers (documents why cluster unit matters)
- <5 clusters raises
- verdict engine reproduces each PREREGISTRATION rule on hand-built result dicts, incl. canary gate -> INCONCLUSIVE
"""
import pytest

pytestmark = pytest.mark.skip(reason="WI-06 not implemented")


def test_cluster_bootstrap_coverage(): ...
def test_row_bootstrap_undercovers(): ...
def test_too_few_clusters_raises(): ...
def test_verdict_rules(): ...
