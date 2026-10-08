"""Electrode-set age-pretext encoder (architecture: G-time gate; training: WI-P2, CORE). configs/model/set_encoder.yaml.

Contract
--------
Input: counts [B, E, T] (variable E with padding mask) + population rate [B, T].
Shared per-electrode dilated 1-D CNN (channels 16->32->32, kernel 5, dilations 1/4/16; ~17 s
receptive field at 200 ms bins) -> per-electrode tokens -> pooling = concat of cfg["pooling"] members, in order,
from {attention_pma_1seed, mean, max} -> z [B, 32]. Seal 1: [attention_pma_1seed, mean, max]. Phase 3.1:
[mean, attention_pma_1seed] — max is dropped because its expectation grows with the electrode count N (16 vs 59/60
by platform) and so leaks platform/lab; mean and PMA are weighted averages, unbiased in N. Recording-level z / prediction = mean over its windows.
Invariance: for any electrode permutation P, encode(x[:, P]) == encode(x) to 1e-6 (unit-tested).
Training augmentation: uniform electrode subsampling to E' in [16, E].
Electrode coordinates are NOT an input (Claim C). `random_init(seed)` gives BL-A3's frozen encoder;
BL-A2 trains this same class from scratch on the forecasting target.
Deterministic on CPU under torch.use_deterministic_algorithms(True) with a fixed seed.
"""


import torch
from torch import nn


class SetEncoder(nn.Module):
    """Architecture only (built for the G-time gate). Training lives in train/pretext.py (WI-P2).

    forward(counts [B, E, T] float, mask [B, E] bool True=real electrode) -> (z [B, d], age_pred [B]).
    Per-electrode input channels: log1p(own counts) and log1p(population count / E); shared dilated CNN; mean over
    time -> electrode token; pooling = concat(PMA with one learned seed, masked mean, masked max) -> linear -> z.
    """

    def __init__(self, cfg: dict):
        super().__init__()
        ch, k, dil = cfg["electrode_encoder"]["channels"], cfg["electrode_encoder"]["kernel"], cfg["electrode_encoder"]["dilations"]
        layers, cin = [], 2
        for c, d in zip(ch, dil):
            layers += [nn.Conv1d(cin, c, k, dilation=d, padding=d * (k - 1) // 2), nn.GELU()]
            cin = c
        self.cnn = nn.Sequential(*layers)
        self.seed = nn.Parameter(torch.randn(1, 1, cin) * 0.02)
        self.pma = nn.MultiheadAttention(cin, num_heads=4, batch_first=True)
        self.pooling = list(cfg.get("pooling", ["attention_pma_1seed", "mean", "max"]))
        assert set(self.pooling) <= {"attention_pma_1seed", "mean", "max"} and self.pooling
        self.proj = nn.Linear(len(self.pooling) * cin, cfg["embedding_dim"])
        self.age_head = nn.Linear(cfg["embedding_dim"], 1)

    def forward(self, counts: torch.Tensor, mask: torch.Tensor):
        B, E, T = counts.shape
        pop = (counts * mask[..., None]).sum(1, keepdim=True) / mask.sum(1).clamp(min=1)[:, None, None]
        x = torch.stack([torch.log1p(counts), torch.log1p(pop).expand(B, E, T)], dim=2)
        real = x[mask]                                   # CNN only on real electrode rows (padding is never computed)
        tok_real = self.cnn(real).mean(-1)
        tok = tok_real.new_zeros(B, E, tok_real.shape[-1])
        tok[mask] = tok_real
        out = []
        for p in self.pooling:
            if p == "attention_pma_1seed":
                att, _ = self.pma(self.seed.expand(B, -1, -1), tok, tok, key_padding_mask=~mask)
                out.append(att[:, 0])
            elif p == "mean":
                m = mask[..., None].float()
                out.append((tok * m).sum(1) / m.sum(1).clamp(min=1))
            else:
                out.append(tok.masked_fill(~mask[..., None], float("-inf")).max(1).values)
        z = self.proj(torch.cat(out, dim=-1))
        return z, self.age_head(z).squeeze(-1)
