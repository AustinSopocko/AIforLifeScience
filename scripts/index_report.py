"""Phase 2: pooled RecordingIndex summary per lab and role -> research/phase2_pooled_index.json (+ printed table).
Metadata only (counts, DIV values, recording length); no activity values. QC = duration_s >= 600 (Seal 1 rule)."""
import json
import pandas as pd
from agepretext.data.index import RecordingIndex
from agepretext.data.splits import SplitManifest

idx = RecordingIndex.load(); t = idx.table.copy()
dc = SplitManifest.from_json("splits/dev_confirmatory.json", idx)
role = {c: r for r, cs in dc.partitions.items() for c in cs}
t["role"] = t.cluster_id.map(role)
t = t[t.is_control]                                   # treated NFA wells are Claim-B material, not age-pretext data
t["qc_ok"] = t.duration_s.isna() | (t.duration_s >= 600)
OV = (7, 12)
out = []
for (r, lab), g in t.groupby(["role", "lab"], sort=False):
    q = g[g.qc_ok]
    ov = q[q["div"].between(*OV)].groupby("cluster_id")["div"].nunique()
    out.append(dict(role=r, lab=lab, sources=sorted(g.source.unique()), species=sorted(g.species.unique()),
                    regions=sorted(g.region.unique()), genotypes=sorted(g.genotype.unique()),
                    preps=int(g.cluster_id.nunique()), plates=int(g.plate_id.nunique()), recordings=len(g),
                    recordings_qc=len(q), qc_measured=bool(g.duration_s.notna().any()),
                    div_min=int(q["div"].min()), div_max=int(q["div"].max()), div_values=sorted(map(int, q["div"].unique())),
                    preps_with_div_7_12=int(len(ov)), recordings_div_7_12=int(q["div"].between(*OV).sum())))
out.sort(key=lambda d: (d["role"] != "dev", d["lab"]))
json.dump({"index_sha256": idx.sha256(), "dev_confirmatory_sha256": dc.sha256(), "overlap_stratum_div": list(OV),
           "rows": out}, open("research/phase2_pooled_index.json", "w"), indent=1)
df = pd.DataFrame(out)
df["sp"] = df.species.str.join("/"); df["reg"] = df.regions.str.join("/")
print(df[["role", "lab", "sp", "reg", "preps", "plates", "recordings", "recordings_qc", "div_min", "div_max",
          "preps_with_div_7_12", "recordings_div_7_12"]].to_string(index=False))
for d in out:
    print(f"{d['lab']}: DIV {d['div_values']}")
