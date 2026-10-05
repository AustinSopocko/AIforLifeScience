"""Pipeline P age-pretext training loop (WI-P2). configs/train/pretext.yaml.

Contract
--------
`train_fold(index, spikes, manifest, fold, cfg) -> FoldArtefact`:
  1. guards.require_clean_tree(); invariants.assert_group_disjoint(manifest, index)
  2. select recordings of the fold's train batches
  3. fit ClusterBaggedEnsemble(SetEncoder + AgeHead) for exactly cfg.epochs (no early stopping,
     no tuning surface), sampling cfg.windows_per_recording_per_epoch windows per recording
  4. return FoldArtefact(member weights, seeds, train batches, config sha256)
`train_final(...)` trains on all 8 batches (Claim C primary probe, S-1).
`train_with_canary(..., canary_seed)` identical, after applying eval.claim_c_probe.inject_canary to
training spikes (Claim C validity gate).
Artefacts go to artifacts/<protocol_hash[:8]>/potter/... and are listed with sha256 in the ledger row.
"""


def train_fold(index, spikes, manifest, fold: str, cfg):
    raise NotImplementedError("WI-P2")


def train_final(index, spikes, cfg):
    raise NotImplementedError("WI-P2")


def train_with_canary(index, spikes, cfg, canary_seed: int):
    raise NotImplementedError("WI-P4")
