"""[Seal-1 run: refuses at HEAD (protocol is v4); reproducible at commits 353cc113..fef0404, rules in protocol/archive/seal-1/.]
WI-P2 (under Seal 1): Wagenaar 4-fold batch cross-fit -> artifacts/potter/oof.parquet; final encoder on all 8 batches ->
artifacts/potter/final_encoder/ + final_pred.parquet. Hyperparameters come only from the sealed configs."""
import hashlib, json, os, sys, time
import pandas as pd, yaml
from agepretext.data.splits import SplitManifest
from agepretext.data.index import RecordingIndex
from agepretext.train.pretext import load_potter, predict, save, train_model
from agepretext.validation.guards import require_clean_tree, require_sealed_protocol
from agepretext.validation import ledger as L

require_clean_tree(); seal = require_sealed_protocol(min_seal=1)
head = os.popen("git rev-parse HEAD").read().strip()
mcfg = yaml.safe_load(open("configs/model/set_encoder.yaml")); tcfg = yaml.safe_load(open("configs/train/pretext.yaml"))
man = SplitManifest.from_json(tcfg["crossfit"]["manifest"], RecordingIndex.load())
recs = load_potter(); os.makedirs("artifacts/potter", exist_ok=True)
t0 = time.time(); oof = []
for i, (fid, f) in enumerate(sorted(man.folds.items())):
    tr = [r for r in recs if r["prep_id"] in f["train"]]; te = [r for r in recs if r["prep_id"] in f["test"]]
    assert not {r["prep_id"] for r in tr} & {r["prep_id"] for r in te}
    model, stats = train_model(tr, mcfg, tcfg, seed=tcfg["seed"] + i)
    oof.append(predict(model, stats, te).assign(fold=fid))
    print(f"{fid}: train {len(tr)} rec, test {len(te)} rec, {time.time()-t0:.0f}s", flush=True)
oof = pd.concat(oof).sort_values("recording_id"); oof.to_parquet("artifacts/potter/oof.parquet", index=False)
assert oof.recording_id.is_unique and len(oof) == len(recs)
model, stats = train_model(recs, mcfg, tcfg, seed=tcfg["seed"] + 100)
save(model, stats, "artifacts/potter/final_encoder", {"seal_id": seal.seal_id, "protocol_hash": seal.protocol_hash, "git_commit": head})
predict(model, stats, recs).to_parquet("artifacts/potter/final_pred.parquet", index=False)
dur = time.time() - t0; print(f"final: {len(recs)} rec, total {dur/60:.1f} min", flush=True)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
arts = ["artifacts/potter/oof.parquet", "artifacts/potter/final_encoder/model.pt", "artifacts/potter/final_encoder/meta.json", "artifacts/potter/final_pred.parquet"]
L.append(L.infra_row("training_completed",
    f"WI-P2 under {seal.seal_id}: 4-fold batch cross-fit ({len(oof)} out-of-fold recordings) + final encoder on all 8 batches, "
    f"1 member, seeds {tcfg['seed']}+fold / {tcfg['seed']+100}. Wall-clock {dur/60:.1f} min. No evaluation in this run.",
    phase="confirmatory", hypothesis_id="H-AGE-P", claim="age", protocol_hash=seal.protocol_hash, seal_id=seal.seal_id,
    split_manifest_sha256=man.sha256(), seeds=[tcfg["seed"] + i for i in range(4)] + [tcfg["seed"] + 100], duration_s=dur,
    artifacts=[{"path": p, "sha256": sha(p)} for p in arts]))
