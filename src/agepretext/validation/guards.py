"""Run guards (WI-02). Called before any data is loaded by eval/train commands.

Contract
--------
- `require_clean_tree()` raises (exit 3) if `git status --porcelain` is non-empty (generated,
  gitignored paths excluded).
- `require_sealed_protocol(profile, *, min_seal=1)` raises unless current_hash(profile) matches a
  seal >= min_seal; returns the SealRecord for the ledger row.
- `lockbox_access(profile)` context manager: requires seal >= 2 for phase=confirmatory, writes a
  ledger row with lockbox_opened=true BEFORE yielding lockbox data, and marks a second opening
  under a different seal as `notes: "LOCKBOX RE-OPENED"` (allowed, must be disclosed in report).
  phase=reproduction re-runs under the same seal are logged as reproduction, not openings.
"""
from contextlib import contextmanager


def require_clean_tree() -> None:
    raise NotImplementedError("WI-02")


def require_sealed_protocol(profile: str, *, min_seal: int = 1):
    raise NotImplementedError("WI-02")


@contextmanager
def lockbox_access(profile: str, phase: str):
    raise NotImplementedError("WI-02")
    yield  # pragma: no cover
