"""WI-00: re-derive PLAN §2.3/§3 counts and gates K1-K3 from the fetched files. Writes recon/inventory.json.
Counts only (rows, units, DIV levels, wells with spikes); no activity statistic is computed."""
import collections, glob, json, os, re, zipfile
import pandas as pd, yaml

inv = {}
# --- NFA (counts; lockbox NTP read for counts/schema only) ---
z = zipfile.ZipFile("data/raw/nfa/NTP_TC_Analysis.zip")
mem = yaml.safe_load(open("configs/data/nfa.yaml"))["members"]
for sub in ("TC", "NTP"):
    d = pd.read_csv(z.open(mem[sub]["features"]), usecols=["date", "Plate.SN", "DIV", "well", "trt", "dose"])
    c = d[d.dose == 0]
    inv[f"nfa_{sub}"] = {"rows": len(d), "preps": int(d.date.nunique()), "plates": int(d["Plate.SN"].nunique()),
                         "treatments": int(d.trt.nunique()), "control_wells": int(c.groupby(["Plate.SN", "well"]).ngroups),
                         "div_levels": sorted(int(x) for x in d.DIV.unique()),
                         "preps_with_controls_at_ge3_divs": int((c.groupby("date").DIV.nunique() >= 3).sum())}
# --- Potter dense (filenames only) ---
recs = [tuple(map(int, re.match(r"(\d+)-(\d+)-(\d+)\.spk", os.path.basename(f)).groups()))
        for f in glob.glob("data/raw/potter/*.spk.txt.bz2")]
divs = collections.defaultdict(set)
for b, c, dv in recs:
    divs[(b, c)].add(dv)
per_batch = collections.Counter(b for b, _ in divs)
ge5 = collections.Counter(b for (b, _), s in divs.items() if len(s) >= 5)
def pairs(ds):
    ds = sorted(ds); return sum(1 for t in ds if any(6 <= u - t <= 8 for u in ds))
inv["potter_dense"] = {"recordings": len(recs), "cultures": len(divs), "batches": len(per_batch),
    "cultures_per_batch": {str(k): v for k, v in sorted(per_batch.items())},
    "div_range": [min(r[2] for r in recs), max(r[2] for r in recs)],
    "cultures_with_ge5_divs_per_batch": {str(k): ge5.get(k, 0) for k in sorted(per_batch)},
    "seven_day_pairs_per_culture": {"min": min(pairs(s) for s in divs.values()), "median": float(pd.Series([pairs(s) for s in divs.values()]).median()),
                                    "cultures_with_ge3": sum(pairs(s) >= 3 for s in divs.values())}}
k1 = len(per_batch) >= 8 and all(ge5.get(b, 0) >= 2 for b in per_batch)
# --- Kapucu rat (filenames + Channel column only) ---
kcfg = yaml.safe_load(open("configs/data/kapucu.yaml"))["rat_preps_claim_a"]
eval_pairs = {"190617": [(21, 28), (24, 31)], "250417": [(21, 28)], "31017": [(24, 31)]}
k3 = True
for prep, p in kcfg.items():
    wells_by_div = {}
    for dv in p["divs"]:
        f = glob.glob(f"data/raw/kapucu_rat/{prep}/Rat_{prep}_*_DIV{dv}_spikes.csv")[0]
        ch = pd.read_csv(f, usecols=["Channel"]).Channel.astype(str)
        wells_by_div[dv] = set(ch.str.split("_").str[0].str.strip())
    allw = set().union(*wells_by_div.values())
    ok = {f"{a}->{b}": len(wells_by_div[a] & wells_by_div[b]) for a, b in eval_pairs[prep]}
    k3 &= all(v >= 8 for v in ok.values())
    inv[f"kapucu_rat_{prep}"] = {"plate": p["plate"], "divs": sorted(wells_by_div), "wells_with_spikes_any_div": len(allw),
        "wells_with_spikes_both_ends_eval_pairs": ok,
        "seven_day_pairs_per_well": pairs(p["divs"])}
inv["gates"] = {"K1": "PASS" if k1 else "FAIL",
                "K2": "PASS (files available; chronic dosing not verifiable from files, see PLAN A3)",
                "K3": "PASS" if k3 else "FAIL -> alternative target"}
json.dump(inv, open("recon/inventory.json", "w"), indent=1, sort_keys=True)
for k, v in inv.items():
    print(k, json.dumps(v, sort_keys=True)[:300])
