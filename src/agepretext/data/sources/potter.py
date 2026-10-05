"""Wagenaar/Pine/Potter 2006 loader (WI-P1, CORE: encoder corpus for Claims A and C).

Contract
--------
Parses `<batch>-<culture>-<DIV>.spk.txt.bz2` (rows: time_s channel) for DENSE cultures only
(sparse/small exist only in batches 5-7, confounding density with batch; they are stretch S-5).
prep_id = batch (8), plate_id = well_id = culture (30), species = rat.
Returns per-recording spike arrays keyed by recording_id and a validated RecordingIndex.
Post-conditions (asserted against configs/data/potter.yaml `verified`): 30 cultures, 527 recordings,
cultures-per-batch as listed, DIV in [3, 39]. Cite-only data: files live only under data/raw/.
"""


import numpy as np
import pandas as pd


def read_spikes(path: str) -> tuple[np.ndarray, np.ndarray]:
    """One `.spk.txt.bz2` file -> (times_s float64, channel int16). Channels are hardware IDs 0..59."""
    d = pd.read_csv(path, sep=r"\s+", header=None, names=["t", "ch"], dtype={"t": np.float64, "ch": np.int16})
    return d.t.to_numpy(), d.ch.to_numpy()


def load(cfg: dict):
    raise NotImplementedError("index is built by scripts/build_index.py; spikes via read_spikes()")
