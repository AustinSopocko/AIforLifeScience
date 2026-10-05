"""Protocol canonicalisation, hashing and sealing (WI-02).

Contract
--------
protocol_hash = sha256 over the concatenation, in this fixed order, of canonical bytes of:
    1. protocol/prereg.yaml + PREREGISTRATION.md          (prereg_sha256)
    2. resolved profile config                             (config.ResolvedConfig.canonical_json)
    3. every SplitManifest referenced by the profile       (sorted by path)
    4. data/manifests/*.sha256 for sources in the profile  (sorted by path)
    5. git commit SHA of HEAD (tree must be clean)
Canonical = sorted-key JSON, floats via repr, UTF-8, LF (YAML parsed then re-serialised).
- `seal(profile) -> SealRecord` refuses if the tree is dirty, any manifest fails
  assert_group_disjoint, or any TBD_WI00 placeholder remains; writes protocol/seals/seal-N.json
  {seal_id, protocol_hash, prereg_sha256, components: {name: sha256}, git_commit, created_utc}
  and creates git tag `seal-N-<hash8>`.
- `current_hash(profile)` recomputes without sealing; `matching_seal(hash)` returns the SealRecord
  or None. Same inputs on two machines -> identical hash (tested).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class SealRecord:
    seal_id: str
    protocol_hash: str
    prereg_sha256: str
    git_commit: str
    created_utc: str
    components: dict


def current_hash(profile: str) -> str:
    raise NotImplementedError("WI-02")


def seal(profile: str) -> SealRecord:
    raise NotImplementedError("WI-02")


def matching_seal(protocol_hash: str) -> SealRecord | None:
    raise NotImplementedError("WI-02")
