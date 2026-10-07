"""WI-03 + Phase 2 (D19): build data/processed/recording_index.parquet (one row per recording; metadata only, no
activity values). Sources: NFA, Potter, Kapucu rat (Seal 1) + EPAmeadev, EPA-MI, g2chvcdata, Fragile-X (Phase 2 dev).
Treated recordings of the dev corpora never enter the index (rules in configs/data/<source>.yaml); counts printed."""
import glob, hashlib, os, re, zipfile
from multiprocessing import Pool
import numpy as np, pandas as pd, yaml
from agepretext.data.index import LABS, PLATFORMS, RecordingIndex
from agepretext.data.sources import epa_mi, epameadev, fragilex, g2chvc
from agepretext.data.sources.potter import read_spikes as potter_spikes

def rid(*parts): return hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:16]

BASE = dict(region="cortex", genotype="wt", is_control=True, compound=None, dose_uM=0.0, subset=None, row=None, col=None,
            inferential=True, duration_s=np.nan, duration_source="none")

def row(source, **kw):
    r = {**BASE, "source": source, "lab": LABS[source], **kw}
    r["cluster_id"] = f"{r['lab']}:{r['prep_id']}"
    r["platform"] = PLATFORMS[source]
    r["recording_id"] = rid(source, r["prep_id"], r["plate_id"], r["well_id"], r["div"])
    return r

def potter_duration(path):
    t, _ = potter_spikes(path)
    return float(t[t <= QC_MAX_T].max())

rows, notes = [], {}
# --- NFA (confirmatory under Phase 2) ---
z = zipfile.ZipFile("data/raw/nfa/NTP_TC_Analysis.zip")
mem = yaml.safe_load(open("configs/data/nfa.yaml"))["members"]
tc_preps = set(pd.read_csv(z.open(mem["TC"]["features"]), usecols=["date"]).date)
n_dedup = 0
for sub in ("TC", "NTP"):
    d = pd.read_csv(z.open(mem[sub]["features"]), usecols=["date", "Plate.SN", "DIV", "well", "trt", "dose"])
    for i, r in enumerate(d.itertuples(index=False)):
        if sub == "NTP" and r.date in tc_preps:   # shared prep (20171011): recordings already present in TC -> keep TC copy
            n_dedup += 1
            continue
        rows.append(row("nfa", prep_id=str(r.date), plate_id=r._1, well_id=r.well, div=int(r.DIV), species="rat",
            electrodes=16, is_control=bool(r.dose == 0), compound=r.trt, dose_uM=float(r.dose), subset=sub,
            row=r.well[0], col=int(r.well[1:]), payload=f"{sub}:{i}"))
# --- Potter (dev) ---
pcfg = yaml.safe_load(open("configs/data/potter.yaml")); QC_MAX_T = pcfg["qc"]["max_spike_time_s"]
pfiles = sorted(glob.glob("data/raw/potter/*.spk.txt.bz2"))
CACHE = "data/processed/_potter_last_spike.json"   # keyed by file name + size; potter files are manifest-verified
import json
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
key = lambda f: f"{os.path.basename(f)}:{os.path.getsize(f)}"
todo = [f for f in pfiles if key(f) not in cache]
if todo:
    with Pool(4) as pool:
        cache.update({key(f): d for f, d in zip(todo, pool.map(potter_duration, todo, chunksize=8))})
    os.makedirs("data/processed", exist_ok=True); json.dump(cache, open(CACHE, "w"))
pdur = [cache[key(f)] for f in pfiles]
for f, dur in zip(pfiles, pdur):
    b, c, dv = re.match(r"(\d+)-(\d+)-(\d+)\.spk", os.path.basename(f)).groups()
    cult = f"{b}-{c}"
    rows.append(row("potter", prep_id=b, plate_id=cult, well_id=cult, div=int(dv), species="rat",
        electrodes=pcfg["electrodes"], duration_s=dur, duration_source="last_spike", payload=os.path.relpath(f, "data/raw/potter")))
# --- Kapucu rat (confirmatory; only well IDs read, as at Seal 1) ---
kc = yaml.safe_load(open("configs/data/kapucu.yaml"))
for prep, p in kc["rat_preps_claim_a"].items():
    for dv in p["divs"]:
        f = glob.glob(f"data/raw/kapucu_rat/{prep}/Rat_{prep}_*_DIV{dv}_spikes.csv")[0]
        wells = sorted(set(pd.read_csv(f, usecols=["Channel"]).Channel.astype(str).str.split("_").str[0].str.strip()))
        for w in wells:
            rows.append(row("kapucu_rat", prep_id=prep, plate_id=p["plate"], well_id=w, div=int(dv), species="rat",
                electrodes=kc["electrodes_per_well"], duration_source="deferred", row=w[0], col=int(w[1:]), payload=os.path.relpath(f, "data/raw/kapucu_rat")))
# --- Phase 2 dev corpora (D19) ---
for src, mod in (("epameadev", epameadev), ("epa_mi", epa_mi), ("g2chvc", g2chvc), ("fragilex", fragilex)):
    cfg = yaml.safe_load(open(f"configs/data/{src}.yaml"))
    recs = mod.recordings(cfg, f"data/raw/{src}")
    notes[src] = getattr(mod.recordings, "excluded", None)
    # >1 file for the same (plate, well, div): keep the first by (timestamp, payload) — pre-declared in each config
    recs = sorted(recs, key=lambda r: (r["plate_id"], r["well_id"], r["div"], r.get("timestamp", ""), r["payload"]))
    seen, keep = set(), []
    for r in recs:
        k = (r["plate_id"], r["well_id"], r["div"])
        if k not in seen:
            seen.add(k); keep.append(r)
    notes[src] = {**(notes[src] or {}), "duplicate_recordings_dropped": len(recs) - len(keep)}
    recs = keep
    el = cfg.get("electrodes", cfg.get("electrodes_per_well"))
    for r in recs:
        r.pop("timestamp", None); r.pop("plate_kind", None)
        rows.append(row(src, species=cfg["species"], electrodes=el, **{"region": cfg.get("region", "cortex"), **r}))

idx = RecordingIndex(pd.DataFrame(rows))
idx.validate()
os.makedirs("data/processed", exist_ok=True)
idx.table.to_parquet("data/processed/recording_index.parquet", index=False)
print(idx.table.groupby(["lab", "source"]).agg(recordings=("recording_id", "size"), preps=("prep_id", "nunique"),
      plates=("plate_id", "nunique")).to_string())
print("NFA NTP rows deduplicated (prep shared with TC):", n_dedup)
print("dev-corpus exclusions:", notes)
print("index sha256:", idx.sha256()[:16])
