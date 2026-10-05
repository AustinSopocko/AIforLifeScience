"""Configuration loading and canonical hashing (WI-01).

Contract
--------
- `load_profile(name)` resolves `configs/profiles/<name>.yaml`, recursively merges its
  `include:` list (later keys override earlier), and returns an immutable `ResolvedConfig`.
- `ResolvedConfig.canonical_json()` is deterministic across machines: sorted keys, floats in
  `repr` form, no NaN/inf, UTF-8, LF. `ResolvedConfig.sha256()` hashes exactly those bytes.
- Any value equal to the string "TBD_WI00" raises `UnresolvedPlaceholder` when an evaluation
  (not recon) command loads the config — placeholders must be resolved before Seal #1.
"""
from dataclasses import dataclass
from typing import Any, Mapping


class UnresolvedPlaceholder(RuntimeError):
    """A TBD_WI00 placeholder survived into an evaluation config."""


@dataclass(frozen=True)
class ResolvedConfig:
    data: Mapping[str, Any]

    def canonical_json(self) -> bytes:
        raise NotImplementedError("WI-01")

    def sha256(self) -> str:
        raise NotImplementedError("WI-01")


def load_profile(name: str, *, allow_placeholders: bool = False) -> ResolvedConfig:
    raise NotImplementedError("WI-01")
