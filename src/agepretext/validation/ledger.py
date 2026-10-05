"""Append-only, hash-chained results ledger (WI-02). Format: ledger/SCHEMA.md.

Contract
--------
- `append(row, path)` fills row_id (ULID), timestamp_utc and prev_row_sha256 (sha256 of the exact bytes,
  including the trailing LF, of the last line; 64 zeros for genesis), validates the schema, and appends ONE
  canonical-JSON line (sorted keys, compact separators, UTF-8). It never rewrites the file. Returns row_id.
- `verify(path, against_ref=None, staged=False)` raises LedgerError if any line fails the schema, any
  prev_row_sha256 mismatches, or (against_ref / staged) the file is not a byte-prefix extension of the
  version at that git ref / at HEAD (i.e. a row was edited or deleted).
- `export_csv(path, out)` writes a flat view (gitignored).
"""
import csv
import datetime
import hashlib
import json
import os
import subprocess
import time

GENESIS = "0" * 64
FIELDS = {
    "row_id": str, "prev_row_sha256": str, "timestamp_utc": str, "phase": str, "status": str,
    "hypothesis_id": str, "claim": str, "metric": str, "value": (int, float, type(None)),
    "ci_lower": (int, float, type(None)), "ci_upper": (int, float, type(None)), "ci_method": (str, type(None)),
    "n_clusters": (int, type(None)), "cluster_unit": (str, type(None)), "verdict": str,
    "kill_condition_triggered": bool, "protocol_hash": (str, type(None)), "seal_id": (str, type(None)),
    "prereg_sha256": str, "git_commit": str, "config_sha256": (str, type(None)),
    "split_manifest_sha256": (str, type(None)), "data_manifest_sha256": (str, type(None)),
    "env_lock_sha256": (str, type(None)), "seeds": list, "lockbox_opened": bool, "artifacts": list,
    "duration_s": (int, float), "notes": str,
}
ENUMS = {
    "phase": {"exploratory", "confirmatory", "reproduction", "infrastructure"},
    "status": {"ok", "error"},
    "claim": {"age", "A", "B", "C", "baseline", "none"},
    "verdict": {"SUPPORTS", "REFUTES", "INCONCLUSIVE", "N/A"},
}
_ULID = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


class LedgerError(RuntimeError):
    pass


def _canonical(row: dict) -> bytes:
    return (json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode()


def _ulid() -> str:
    n = (int(time.time() * 1000) << 80) | int.from_bytes(os.urandom(10), "big")
    return "".join(_ULID[(n >> (5 * i)) & 31] for i in reversed(range(26)))


def _check_row(row: dict, i: int) -> None:
    missing = set(FIELDS) - set(row)
    extra = set(row) - set(FIELDS)
    if missing or extra:
        raise LedgerError(f"row {i}: missing {sorted(missing)} extra {sorted(extra)}")
    for k, t in FIELDS.items():
        if not isinstance(row[k], t) or (t in ((int, float), (int, float, type(None))) and isinstance(row[k], bool)):
            raise LedgerError(f"row {i}: field {k} has type {type(row[k]).__name__}")
    for k, allowed in ENUMS.items():
        if row[k] not in allowed:
            raise LedgerError(f"row {i}: {k}={row[k]!r} not in {sorted(allowed)}")
    if row["protocol_hash"] is None and row["phase"] != "infrastructure":
        raise LedgerError(f"row {i}: protocol_hash null outside phase=infrastructure")


def _lines(data: bytes) -> list[bytes]:
    if data and not data.endswith(b"\n"):
        raise LedgerError("file does not end with LF")
    return [line + b"\n" for line in data.split(b"\n")[:-1]] if data else []


def verify_bytes(data: bytes) -> int:
    prev = GENESIS
    for i, line in enumerate(_lines(data), 1):
        row = json.loads(line)
        _check_row(row, i)
        if row["prev_row_sha256"] != prev:
            raise LedgerError(f"row {i}: hash chain broken")
        if _canonical(row) != line:
            raise LedgerError(f"row {i}: not canonical JSON")
        prev = hashlib.sha256(line).hexdigest()
    return len(_lines(data))


def _git_show(spec: str) -> bytes | None:
    r = subprocess.run(["git", "show", spec], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def verify(path: str = "ledger/results.jsonl", *, staged: bool = False, against_ref: str | None = None) -> int:
    data = open(path, "rb").read() if not staged else (_git_show(f":{path}") or b"")
    n = verify_bytes(data)
    base_spec = f"{against_ref}:{path}" if against_ref else (f"HEAD:{path}" if staged else None)
    if base_spec:
        base = _git_show(base_spec)
        if base is not None and not data.startswith(base):
            raise LedgerError(f"not an append-only extension of {base_spec}")
    return n


def append(row: dict, path: str = "ledger/results.jsonl") -> str:
    data = open(path, "rb").read() if os.path.exists(path) else b""
    verify_bytes(data)
    lines = _lines(data)
    row = dict(row)
    row["row_id"] = _ulid()
    row["timestamp_utc"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    row["prev_row_sha256"] = hashlib.sha256(lines[-1]).hexdigest() if lines else GENESIS
    _check_row(row, len(lines) + 1)
    with open(path, "ab") as f:
        f.write(_canonical(row))
        f.flush()
        os.fsync(f.fileno())
    return row["row_id"]


def infra_row(metric: str, notes: str, **kw) -> dict:
    """Convenience: a phase=infrastructure row with null protocol fields (pre-Seal #1)."""
    def h(p):
        return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None
    row = {k: None for k in FIELDS}
    row.update(phase="infrastructure", status="ok", hypothesis_id="none", claim="none", metric=metric,
               verdict="N/A", kill_condition_triggered=False, seeds=[], lockbox_opened=False, artifacts=[],
               duration_s=0.0, notes=notes,
               prereg_sha256=hashlib.sha256(open("protocol/prereg.yaml", "rb").read()
                                            + open("PREREGISTRATION.md", "rb").read()).hexdigest(),
               git_commit=subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
               env_lock_sha256=h("requirements.lock"))
    row.update(kw)
    return row


def export_csv(path: str, out: str) -> None:
    rows = [json.loads(line) for line in _lines(open(path, "rb").read())]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(FIELDS))
        w.writeheader()
        for r in rows:
            w.writerow({k: json.dumps(v) if isinstance(v, (list, dict)) else v for k, v in r.items()})
