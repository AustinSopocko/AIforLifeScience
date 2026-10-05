# Demo video storyboard (≤ 5:00), draft

Rule: every number on screen is produced live by the pipeline or read from the ledger. Every
plot frame is stamped with `protocol_hash[:8]` and the `row_id` it shows. Driver:
`scripts/demo.py --profile demo`. Recording: OBS at 1920×1080. Plot frames come from
`viz/animate.py`.

| t | Shot | Screen | Code that must exist |
|---|---|---|---|
| 0:00–0:25 | Hook | Title card, then one sentence: "Culture age is a free label on every MEA recording. We use it to learn culture state, and we prove the model isn't memorising the plate." | static card (`demo/assets/`) |
| 0:25–0:55 | Data + invariant | Terminal: `agepretext index` prints the hierarchy (prep > plate > well). `agepretext split` shows the lockbox preps. A deliberately wrong well-level split raises `InvariantViolation`. | `data/splits.py`, `invariants.py`, CLI pretty-printing |
| 0:55–1:25 | Seal + ledger | `agepretext seal` prints the hash. `agepretext ledger verify` passes. Then one ledger line is edited and `verify` fails (the edit is reverted on camera). | `validation/protocol.py`, `validation/ledger.py` |
| 1:25–2:25 | **Shot 1: age deviation** | Trajectory animation: control band, then doses revealed. Compound chosen by the pre-declared rule (largest non-cytotoxic Δ-AUC lower bound on NTP). BL-5 raw-feature inset. Caption: "no pre-exposure baseline; dosing from DIV 0". | `viz/trajectory.py`, WI-10 artefacts |
| 2:25–3:25 | **Shot 2: few-shot curve** | Curve fills in live as `claim_a_fewshot` yields (k, method) events. A guide line marks "best from-scratch at k = 50". Verdict badge computed by `verdicts.py`. | `eval/claim_a_fewshot.py` generator, `viz/fewshot_curve.py` LiveCurve |
| 3:25–4:25 | **Shot 3: probe fails, canary succeeds** | Left: plate-identity confusion matrix on the embedding (uniform). Middle: same probe with the canary (diagonal). Right: permutation null with the observed value, and the canary power curve. | `eval/claim_c_probe.py`, `viz/probe.py` |
| 4:25–4:50 | Verdict table | Table of H-AGE/A/B/C verdicts with lower bounds, read from the confirmatory ledger rows. Refuted rows shown just as prominently. | `report_numbers.py` table renderer |
| 4:50–5:00 | Repro | `bash reproduce.sh --profile mvr` and the repo URL. | `reproduce.sh` |

Fallback if a live step is too slow to film: replay the recorded generator events at the same
pacing, with an on-screen "replay of run ⟨row_id⟩" label. Never splice in results from a
different run.
