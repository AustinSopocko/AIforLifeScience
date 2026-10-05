"""Append-only, hash-chained results ledger (WI-02). Format: ledger/SCHEMA.md.

Contract
--------
- `append(row: dict, path="ledger/results.jsonl") -> str` fills row_id (ULID), timestamp_utc,
  prev_row_sha256 (sha256 of the exact bytes of the last line, or 64 zeros), validates the
  schema, writes ONE line with O_APPEND + fsync, returns row_id. Never rewrites the file.
- `verify(path, *, staged=False, against_ref=None) -> None` raises LedgerError if: any line
  fails schema; any prev_row_sha256 mismatches; (against_ref) the file is not a byte-prefix
  extension of the file at that git ref; (staged) the staged diff contains removed/modified lines.
- `export_csv(path, out)` writes a flat view (gitignored).
- Crashes after data load still produce a row (status="error") via `ledgered_run` context manager.
"""
from contextlib import contextmanager


class LedgerError(RuntimeError):
    pass


def append(row: dict, path: str = "ledger/results.jsonl") -> str:
    raise NotImplementedError("WI-02")


def verify(path: str = "ledger/results.jsonl", *, staged: bool = False, against_ref: str | None = None) -> None:
    raise NotImplementedError("WI-02")


def export_csv(path: str, out: str) -> None:
    raise NotImplementedError("WI-02")


@contextmanager
def ledgered_run(hypothesis_id: str, claim: str, phase: str, **context):
    raise NotImplementedError("WI-02")
    yield  # pragma: no cover
