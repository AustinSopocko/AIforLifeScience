"""Feature MLP encoder (WI-08). configs/model/feature_mlp.yaml.

Contract
--------
`FeatureMLP(n_inputs, hidden=(64, 64), embedding_dim=16, dropout=0.1)`:
  forward(x[B, n_inputs]) -> z[B, 16]; `encode` is forward in eval mode with no grad.
  Inputs are already transformed by features.harmonise.FeatureTransform.
Deterministic under a fixed seed with torch.use_deterministic_algorithms(True) on CPU.
`random_init(seed)` returns an untrained instance (baseline BL-4); BL-3 trains this same class.
"""


class FeatureMLP:  # becomes torch.nn.Module in WI-08
    def __init__(self, n_inputs: int, hidden=(64, 64), embedding_dim: int = 16, dropout: float = 0.1):
        raise NotImplementedError("WI-08")
