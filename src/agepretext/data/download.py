"""Checksummed downloads from origin (WI-00 manifests, WI-O2 reproduction).

Contract
--------
- `file_list(source, cfg)` returns [(relpath, url)] for a source. Potter dense: hrefs of the configured
  index page; NFA: the configured archive; Kapucu rat: names constructed from configs/data/kapucu.yaml
  (no listing calls).
- `fetch(source, cfg, dest)` downloads each file (streamed to a temp file, then atomic rename). If
  `data/manifests/<source>.sha256` exists, every file must match it (ChecksumMismatch otherwise); an
  existing file with a matching hash is not re-downloaded.
- `write_manifest(source, dest)` records "<sha256>  <bytes>  <relpath>" lines, sorted by relpath.
- Kapucu raw *.h5 is forbidden. CITE-ONLY sources are fetched from origin only (no mirrors).
- Phase 2 bundles (`fetch_bundle(source, cfg, dest)`; cfg["fetch"]["kind"] in {git, zip}): git sources are cloned at
  the pinned commit (optionally sparse); zip sources are downloaded, extracted (each archive into its own directory,
  nested archives included) and never executed. `bundle_files(source, cfg, dest)` lists the manifest set: every
  file the loader can read plus the archives. Afterwards every manifest line must match (ChecksumMismatch otherwise).
"""
import hashlib
import os
import glob
import re
import subprocess
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor

MANIFEST_DIR = "data/manifests"


class ChecksumMismatch(RuntimeError):
    pass


def _get(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read()


def file_list(source: str, cfg: dict) -> list[tuple[str, str]]:
    if source == "nfa":
        return [(f["name"], cfg["base_url"] + f["name"]) for f in cfg["files"]]
    if source == "potter":
        idx = cfg["index_urls"]["dense"]
        html = _get(idx).decode("latin-1")
        rels = sorted(set(re.findall(r'href="(\.\./simple-text/daily/spont/dense/[^"]+\.spk\.txt\.bz2)"', html)))
        base = idx.rsplit("/", 1)[0] + "/"
        return [(r.rsplit("/", 1)[1], urllib.request.urljoin(base, r)) for r in rels]
    if source == "kapucu_rat":
        out = []
        for prep, p in cfg["rat_preps_claim_a"].items():
            short = p["plate"].replace("Rat_", "")
            names = [f"Rat_{prep}_{short}_DIV{d}_spikes.csv" for d in p["divs"]]
            names += [f"Rat_{prep}_{short}_DIV{p['divs'][0]}_expLog.csv", f"noisy_electrodes_{p['plate']}.csv"]
            out += [(f"{prep}/{n}", cfg["raw_base"] + p["dir"] + "/" + n) for n in names]
        assert not any(r.endswith(".h5") for r, _ in out)
        return out
    raise KeyError(source)


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_manifest(source: str) -> dict:
    path = os.path.join(MANIFEST_DIR, f"{source}.sha256")
    if not os.path.exists(path):
        return {}
    out = {}
    for line in open(path):
        h, n, rel = line.rstrip("\n").split("  ", 2)
        out[rel] = (h, int(n))
    return out


def fetch(source: str, cfg: dict, dest: str, workers: int = 8) -> list[str]:
    os.makedirs(dest, exist_ok=True)
    expected = read_manifest(source)
    items = file_list(source, cfg)

    def one(item):
        rel, url = item
        path = os.path.join(dest, rel)
        if os.path.exists(path) and (not expected or _sha256(path) == expected.get(rel, (None,))[0]):
            return path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".part"
        with urllib.request.urlopen(url, timeout=300) as r, open(tmp, "wb") as f:
            for chunk in iter(lambda: r.read(1 << 20), b""):
                f.write(chunk)
        if expected and _sha256(tmp) != expected.get(rel, (None,))[0]:
            os.remove(tmp)
            raise ChecksumMismatch(f"{source}: {rel}")
        os.replace(tmp, path)
        return path

    with ThreadPoolExecutor(workers) as ex:
        paths = list(ex.map(one, items))
    if expected and set(expected) != {r for r, _ in items}:
        raise ChecksumMismatch(f"{source}: file set differs from manifest")
    return paths


def write_manifest(source: str, dest: str, rels: list[str]) -> str:
    os.makedirs(MANIFEST_DIR, exist_ok=True)
    path = os.path.join(MANIFEST_DIR, f"{source}.sha256")
    with open(path, "w") as f:
        for rel in sorted(rels):
            p = os.path.join(dest, rel)
            f.write(f"{_sha256(p)}  {os.path.getsize(p)}  {rel}\n")
    return path


BUNDLE_GLOBS = {
    "epameadev": ["repo/allH5Files/*.h5"],
    "g2chvc": ["repo/inst/extdata/*.h5"],
    "fragilex": ["MEA_experiments.zip", "readme.txt", "extracted/MEA_experiments/*/CultureSession*/MEA_*/*_spikes.mat"],
    "epa_mi": ["Mutual Information Data and Scripts.zip", "spikelists/*/*_spike_list.csv",
               "spikelists/*/*_Neural Statistics Compiler(*).csv"],
}


def bundle_files(source: str, cfg: dict, dest: str) -> list[str]:
    rels = {os.path.relpath(p, dest) for g in BUNDLE_GLOBS[source] for p in glob.glob(os.path.join(dest, g))}
    return sorted(r for r in rels if "__MACOSX" not in r)


def _download(url: str, path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with urllib.request.urlopen(url, timeout=900) as r, open(path + ".part", "wb") as f:
        for chunk in iter(lambda: r.read(1 << 20), b""):
            f.write(chunk)
    os.replace(path + ".part", path)


def fetch_bundle(source: str, cfg: dict, dest: str) -> list[str]:
    fc = cfg["fetch"]
    os.makedirs(dest, exist_ok=True)
    if fc["kind"] == "git":
        repo = os.path.join(dest, "repo")
        if not os.path.isdir(repo):
            sparse = ["--sparse"] if fc.get("sparse") else []
            subprocess.run(["git", "clone", "-q", "--filter=blob:none", *sparse, fc["url"], repo], check=True)
            if fc.get("sparse"):
                subprocess.run(["git", "-C", repo, "sparse-checkout", "set", *fc["sparse"]], check=True)
        subprocess.run(["git", "-C", repo, "checkout", "-q", fc["commit"]], check=True)
    elif fc["kind"] == "zip":
        arc = os.path.join(dest, fc["archive"])
        if not os.path.exists(arc):
            _download(fc["url"], arc)
        for name, url in fc.get("extra", {}).items():
            if not os.path.exists(os.path.join(dest, name)):
                _download(url, os.path.join(dest, name))
        if not os.path.isdir(os.path.join(dest, fc["extract_to"])):
            zipfile.ZipFile(arc).extractall(os.path.join(dest, fc["extract_to"]))
        inner = fc.get("inner")
        if inner and not os.path.isdir(os.path.join(dest, inner["extract_to"])):
            zipfile.ZipFile(os.path.join(dest, inner["archive"])).extractall(os.path.join(dest, inner["extract_to"]))
    else:
        raise KeyError(fc["kind"])
    rels = bundle_files(source, cfg, dest)
    expected = read_manifest(source)
    if expected:
        if set(expected) != set(rels):
            raise ChecksumMismatch(f"{source}: file set differs from manifest")
        for r in rels:
            if _sha256(os.path.join(dest, r)) != expected[r][0]:
                raise ChecksumMismatch(f"{source}: {r}")
    return rels
