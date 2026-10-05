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


def load(cfg: dict):
    raise NotImplementedError("WI-P1")
