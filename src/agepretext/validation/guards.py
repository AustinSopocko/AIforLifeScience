"""Run guards (WI-02). Called before any data is loaded by train/eval commands.

Contract
--------
- `require_clean_tree()` raises (exit 3) if `git status --porcelain` is non-empty (gitignored paths excluded).
- `require_sealed_protocol(min_seal=1)` raises unless validation.protocol.frozen_hash() matches a seal whose number is
  >= min_seal; returns that SealRecord for the ledger row.
- `lockbox_access(...)` (NFA NTP lockbox, Seal #2): TODO WI-O2.
"""
import subprocess
from contextlib import contextmanager


class GuardError(RuntimeError):
    pass


def require_clean_tree() -> None:
    out = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
    if out:
        raise GuardError(f"dirty tree:\n{out[:400]}")


def require_sealed_protocol(profile: str | None = None, *, min_seal: int = 1):
    from agepretext.validation.protocol import frozen_hash, matching_seal
    h = frozen_hash()
    rec = matching_seal(h)
    if rec is None or int(rec.seal_id.split("-")[1]) < min_seal:
        raise GuardError(f"frozen protocol {h[:12]} does not match any seal >= {min_seal}")
    return rec


@contextmanager
def lockbox_access(profile: str, phase: str):
    raise NotImplementedError("WI-O2")
    yield  # pragma: no cover
