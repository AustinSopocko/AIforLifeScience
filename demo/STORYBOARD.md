# Demo video storyboard (≤ 5:00), v2

Budget: 4 h of the fixed 10 h block (WI-V).

Rules:
- Every number on screen is produced live by the pipeline or read from the ledger.
- Every frame is stamped with `protocol_hash[:8]` and the `row_id` it shows.
- Driver: `scripts/demo.py --profile demo`.
- Capture with OBS at 1920×1080. Plot frames come from `viz/animate.py`.
- If CUT-2 is applied, shots become static frames plus a live terminal.

| t | Shot | Screen | Code that must exist |
|---|---|---|---|
| 0:00–0:20 | Hook | "Culture age is a free label on every MEA recording. We train an age-pretext encoder on it, test it three ways, and prove it isn't memorising the batch." | static card |
| 0:20–0:50 | Two corpora, one invariant | `agepretext index` prints Potter (8 batches > 30 cultures > 527 recordings) and NFA (18 preps > 99 plates). A deliberate recording-level split raises `InvariantViolation`. | `data/index.py`, `data/splits.py`, `invariants.py` |
| 0:50–1:15 | Seal + ledger | `agepretext seal` prints the hash. `ledger verify` passes; a one-byte edit makes it fail; the edit is reverted. The A13 disclosure row is shown. | `validation/*` |
| 1:15–2:15 | **Shot 3 first: batch probe vs canary (Potter, C)** | Left: real-batch 8×8 confusion matrix (should look uniform). Middle: after canary retraining (diagonal). Right: permutation null with the observed value; canary power k/10 vs the 0.8 line. Verdict badge. | `eval/claim_c_probe.py`, `viz/probe.py` |
| 2:15–3:15 | **Shot 2: forecasting curve fills in (Potter, A)** | Curve grows live as `run_fewshot` yields events for one fold (or a labelled replay). Guide line = best baseline at k = all. Marker = ours' upper bound at k = 4. Badge from `verdicts.py`. | `eval/claim_a_fewshot.py`, `viz/fewshot_curve.py` |
| 3:15–4:15 | **Shot 1: age-deviation trajectory (NFA, B)** | NTP compound chosen by the pre-declared rule. Control band; doses revealed by DIV; BL-B1 (firing + burst residual) inset; cytotoxic doses hatched. Caption: "dosing from DIV 0 — no pre-exposure recording". | `eval/claim_b_deviation.py`, `viz/trajectory.py` |
| 4:15–4:45 | Verdicts | Table of H-AGE-P/N, A, B and C with bounds vs best-baseline points, read from ledger rows. Refutations shown just as prominently. | `report_numbers.py` table renderer |
| 4:45–5:00 | Repro + sponsor link | `bash reproduce.sh --profile mvr`; one line on the batch-probe-plus-canary test as the acceptance test for pooled neural data assets. | `reproduce.sh` |

Claim C is shown first on purpose. It is the distinguishing contribution and frames A and B.
