"""Ledger tests (WI-02): append-only + hash chain."""
import json

import pytest

from agepretext.validation import ledger as L


def _two_rows(tmp_path):
    p = tmp_path / "l.jsonl"
    for m in ("a", "b"):
        r = {k: None for k in L.FIELDS}
        r.update(phase="infrastructure", status="ok", hypothesis_id="none", claim="none", metric=m, verdict="N/A",
                 kill_condition_triggered=False, seeds=[], lockbox_opened=False, artifacts=[], duration_s=0.0,
                 notes="", prereg_sha256="x", git_commit="x")
        L.append(r, str(p))
    return p


def test_repo_ledger_verifies():
    assert L.verify("ledger/results.jsonl") >= 2


def test_chain_links(tmp_path):
    assert L.verify(str(_two_rows(tmp_path))) == 2


def test_tamper_detected(tmp_path):
    p = _two_rows(tmp_path)
    lines = p.read_bytes().split(b"\n")
    row = json.loads(lines[0]); row["metric"] = "z"
    lines[0] = json.dumps(row, sort_keys=True, separators=(",", ":")).encode()
    p.write_bytes(b"\n".join(lines))
    with pytest.raises(L.LedgerError):
        L.verify(str(p))


def test_deletion_detected(tmp_path):
    p = _two_rows(tmp_path)
    p.write_bytes(p.read_bytes().split(b"\n", 1)[1])
    with pytest.raises(L.LedgerError):
        L.verify(str(p))


def test_schema_enforced(tmp_path):
    p = tmp_path / "l.jsonl"
    with pytest.raises(L.LedgerError):
        L.append({"metric": "x"}, str(p))
