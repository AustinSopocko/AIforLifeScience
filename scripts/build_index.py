"""WI-03: build data/processed/recording_index.parquet (one row per recording; metadata only, no activity values)."""
import glob, hashlib, os, re, zipfile
import pandas as pd, yaml
from agepretext.data.index import RecordingIndex

def rid(*parts): return hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:16]
rows = []
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
        prep, plate, well, div = str(r.date), r._1, r.well, int(r.DIV)
        rows.append(dict(recording_id=rid("nfa", prep, plate, well, div), source="nfa", prep_id=prep, plate_id=plate,
            well_id=well, div=div, species="rat", electrodes=16, is_control=bool(r.dose == 0), compound=r.trt,
            dose_uM=float(r.dose), subset=sub, row=well[0], col=int(well[1:]), inferential=True, payload=f"{sub}:{i}"))
pel = yaml.safe_load(open("configs/data/potter.yaml"))["electrodes"]
for f in sorted(glob.glob("data/raw/potter/*.spk.txt.bz2")):
    b, c, dv = re.match(r"(\d+)-(\d+)-(\d+)\.spk", os.path.basename(f)).groups()
    cult = f"{b}-{c}"
    rows.append(dict(recording_id=rid("potter", b, cult, cult, dv), source="potter", prep_id=b, plate_id=cult, well_id=cult,
        div=int(dv), species="rat", electrodes=pel, is_control=True, compound=None, dose_uM=0.0, subset=None, row=None,
        col=None, inferential=True, payload=os.path.relpath(f, "data/raw/potter")))
kc = yaml.safe_load(open("configs/data/kapucu.yaml"))
for prep, p in kc["rat_preps_claim_a"].items():
    for dv in p["divs"]:
        f = glob.glob(f"data/raw/kapucu_rat/{prep}/Rat_{prep}_*_DIV{dv}_spikes.csv")[0]
        wells = sorted(set(pd.read_csv(f, usecols=["Channel"]).Channel.astype(str).str.split("_").str[0].str.strip()))
        for w in wells:
            rows.append(dict(recording_id=rid("kapucu_rat", prep, p["plate"], w, dv), source="kapucu_rat", prep_id=prep,
                plate_id=p["plate"], well_id=w, div=int(dv), species="rat", electrodes=kc["electrodes_per_well"],
                is_control=True, compound=None, dose_uM=0.0, subset=None, row=w[0], col=int(w[1:]), inferential=True,
                payload=os.path.relpath(f, "data/raw/kapucu_rat")))
idx = RecordingIndex(pd.DataFrame(rows))
idx.validate()
os.makedirs("data/processed", exist_ok=True)
idx.table.to_parquet("data/processed/recording_index.parquet", index=False)
print(idx.table.groupby("source").agg(recordings=("recording_id", "size"), preps=("prep_id", "nunique"),
      plates=("plate_id", "nunique")).to_string())
print("NFA NTP rows deduplicated (prep shared with TC):", n_dedup)
print("index sha256:", idx.sha256()[:16])
