"""Wagenaar/Pine/Potter 2006 loader (stretch S-1/S-2).

Contract
--------
Parses `<batch>-<culture>-<DIV>.spk.txt.bz2` (rows: time_s channel). prep_id = batch,
plate_id = well_id = culture (one culture per MEA dish), species = rat. Returns spike tables
keyed by recording_id and a RecordingIndex. Density class (dense/sparse/small) is recorded as
a covariate (downstream task T4 candidate). Data are cite-only: never written outside data/raw/.
"""


def load(cfg: dict):
    raise NotImplementedError("S-1")
