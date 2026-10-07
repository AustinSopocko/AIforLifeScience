"""WI-00 + Phase 2: fetch NFA, Potter dense, Kapucu rat and the D19 dev bundles (EPAmeadev, EPA-MI, g2chvcdata,
Fragile-X) into data/raw/<source>/ and verify/write sha256 manifests."""
import sys, time, yaml
from agepretext.data import download as d
CFG = {"nfa": "configs/data/nfa.yaml", "potter": "configs/data/potter.yaml", "kapucu_rat": "configs/data/kapucu.yaml"}
write = "--write-manifest" in sys.argv
for src, cfgp in ({} if "--bundles-only" in sys.argv else CFG).items():
    t = time.time(); cfg = yaml.safe_load(open(cfgp)); dest = f"data/raw/{src}"
    paths = d.fetch(src, cfg, dest)
    rels = [r for r, _ in d.file_list(src, cfg)]
    if write:
        d.write_manifest(src, dest, rels)
    print(f"{src}: {len(paths)} files ok ({time.time()-t:.0f}s){' manifest written' if write else ' verified'}")
BUNDLES = {s: f"configs/data/{s}.yaml" for s in ("epameadev", "epa_mi", "g2chvc", "fragilex")}
for src, cfgp in BUNDLES.items():
    t = time.time(); cfg = yaml.safe_load(open(cfgp)); dest = f"data/raw/{src}"
    rels = d.fetch_bundle(src, cfg, dest) if not write else d.bundle_files(src, cfg, dest)
    if write:
        d.write_manifest(src, dest, rels)
        d.fetch_bundle(src, cfg, dest)
    print(f"{src}: {len(rels)} files ok ({time.time()-t:.0f}s){' manifest written' if write else ' verified'}")
