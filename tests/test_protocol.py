"""Protocol hashing/sealing tests (WI-02).

- identical inputs -> identical hash (YAML key order / whitespace / CRLF do not matter)
- any change to prereg thresholds, configs, split manifests or data manifests changes the hash
- seal refuses on dirty tree, on TBD_WI00 placeholders, on a non-disjoint manifest
- require_sealed_protocol refuses when current hash has no matching seal
"""
import pytest

pytestmark = pytest.mark.skip(reason="WI-02 not implemented")


def test_hash_deterministic(): ...
def test_hash_sensitive_to_each_component(): ...
def test_seal_refusals(): ...
def test_unsealed_eval_refused(): ...
