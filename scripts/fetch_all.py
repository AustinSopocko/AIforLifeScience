"""WI-00: fetch NFA, Potter dense and Kapucu rat into data/raw/<source>/ and verify/write sha256 manifests."""
import sys, time, yaml
from agepretext.data import download as d
CFG = {"nfa": "configs/data/nfa.yaml", "potter": "configs/data/potter.yaml", "kapucu_rat": "configs/data/kapucu.yaml"}
write = "--write-manifest" in sys.argv
for src, cfgp in CFG.items():
    t = time.time(); cfg = yaml.safe_load(open(cfgp)); dest = f"data/raw/{src}"
    paths = d.fetch(src, cfg, dest)
    rels = [r for r, _ in d.file_list(src, cfg)]
    if write:
        d.write_manifest(src, dest, rels)
    print(f"{src}: {len(paths)} files ok ({time.time()-t:.0f}s){' manifest written' if write else ' verified'}")
