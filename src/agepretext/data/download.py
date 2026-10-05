"""Checksummed downloads from origin (WI-00 manifests, WI-14 reproduction).

Contract
--------
- `fetch(source_cfg, dest)` downloads each listed file over HTTPS, streams to a temp file,
  verifies sha256 against `data/manifests/<source>.sha256`, then atomically renames. A mismatch
  deletes the temp file and raises `ChecksumMismatch` — never silently accepts changed upstream data.
- Respects `allowed_globs` / `forbidden_globs` (e.g. Kapucu raw *.h5 is forbidden: 2.3 TiB).
- CITE-ONLY sources are fetched from origin only; no mirror URLs are permitted (decision D10).
- `write_manifest(source_cfg, dest)` (recon only) records sha256 + bytes for files fetched.
- Idempotent: an existing file with matching hash is not re-downloaded.
"""


class ChecksumMismatch(RuntimeError):
    pass


def fetch(source_cfg: dict, dest: str) -> list[str]:
    raise NotImplementedError("WI-00 / WI-03")


def write_manifest(source_cfg: dict, dest: str) -> str:
    raise NotImplementedError("WI-00")
