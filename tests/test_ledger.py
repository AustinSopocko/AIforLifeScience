"""Ledger tests (WI-02): append-only + hash chain.

- append twice -> verify passes; prev_row_sha256 links rows
- editing any byte of an earlier row -> verify raises LedgerError
- deleting a row -> verify raises
- staged diff with a modified line -> verify(staged=True) raises
- crashed run inside ledgered_run -> a status="error" row is written
"""
import pytest

pytestmark = pytest.mark.skip(reason="WI-02 not implemented")


def test_chain_links(): ...
def test_tamper_detected(): ...
def test_deletion_detected(): ...
def test_staged_modification_rejected(): ...
def test_error_row_on_crash(): ...
