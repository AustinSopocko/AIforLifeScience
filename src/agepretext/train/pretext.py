"""Age-pretext training loop (WI-08). configs/train/pretext.yaml.

Contract
--------
`train_fold(index, features, manifest, fold, cfg) -> FoldArtefact`:
  1. guards.require_clean_tree(); invariants.assert_group_disjoint(manifest, index)
  2. select train-partition rows; invariants.assert_controls_only(...)   (INVARIANT-2)
  3. FeatureTransform.fit on those rows only
  4. inner early-stopping split is ALSO by prep (make_group_splits on the train preps)
  5. fit ClusterBaggedEnsemble; return FoldArtefact(transform_state, member weights, seeds,
     train/val prep lists, config sha256)
Artefacts are written under artifacts/<protocol_hash[:8]>/fold_<k>/ and listed with sha256
in the ledger row.
"""


def train_fold(index, features, manifest, fold: str, cfg):
    raise NotImplementedError("WI-08")
