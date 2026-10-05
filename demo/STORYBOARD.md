# Demo video storyboard (≤ 5:00), v3

**Budget:** 4 h of the fixed 10 h block. 0.5 h of asset capture on Thu 8 Oct, 3.5 h on Fri 9 Oct.

**Rules:**
- Every number on screen is produced by the pipeline or read from the ledger.
- Every frame is stamped with `protocol_hash[:8]` and the `row_id` it shows.
- Shots are pre-rendered frame sequences from `viz/animate.py`, played over a live terminal
  (this is the pre-applied trim).

| t | Segment | Screen | Code that must exist |
|---|---|---|---|
| 0:00–0:20 | Hook | Fixed title card: "Falsifiable by construction". The protocol is the contribution, and we apply it three times. | static card |
| 0:20–0:50 | Three corpora, one invariant | `agepretext index` prints Wagenaar (8 batches > 30 cultures), Kapucu rat (3 preps > 36 wells) and NFA (18 preps > 99 plates). A deliberate recording-level split raises `InvariantViolation`. | `data/index.py`, `data/splits.py`, `invariants.py` |
| 0:50–1:15 | Seal + ledger | `agepretext seal`; `ledger verify` passes; a one-byte edit makes it fail; the edit is reverted. Rows 1–2 (disclosures) shown. | `validation/*` |
| 1:15–2:15 | **Shot 3: Claim C** | Left: **C1** plate-within-prep confusion on Δ, beside its canary. Right: **C2** batch confusion on z, beside its canary. Null histograms and canary power against 0.8. Verdict badges. | `eval/identity_probe.py`, `eval/claim_c1_nfa.py`, `eval/claim_c2_wagenaar.py`, `viz/probe.py` |
| 2:15–3:15 | **Shot 2: Claim A full curve (required)** | Built progressively k = 1 → 2 → 4 → 8 → 16 → all; one panel per held-out Kapucu prep; four baselines; guide line at the best baseline point (k = all); ours' upper bound at k = 4. Worst-fold badge. | `eval/claim_a_fewshot.py`, `viz/fewshot_curve.py` |
| 3:15–4:15 | **Shot 1: Claim B trajectory** | NTP compound by pre-declared rule; control band; doses by DIV; BL-B1 inset; cytotoxic doses hatched; "dosing from DIV 0" caption. C1 badge shown, because B depends on it. | `eval/claim_b_deviation.py`, `viz/trajectory.py` |
| 4:15–4:45 | Verdicts | Table of H-AGE-P/N, A, B, C1, C2 with bounds vs best-baseline points, read from ledger rows. Refutations shown just as prominently. | `report_numbers.py` |
| 4:45–5:00 | Closing card | One of 8 pre-written lines, selected by `\CaseNumber`, then `bash reproduce.sh` and the repo URL. | `report_numbers.py` |

## Closing-card variants (pre-written, selected by case number; mirrors PLAN §6b)

1. "All three applications held. Hold your representation to the same protocol."
2. "The readout held and is certified; the transfer claim did not. The protocol said so first."
3. "Transfer held and the readout is certified; the age residual did not beat firing rate. Reported, not hidden."
4. "Both claims beat their baselines; the protocol could not certify them free of plate artefact. Uncertified, and labelled so."
5. "Two of three claims rejected; the readout is certified artefact-free. The test is the deliverable."
6. "One uncertified lead, two rejections. The protocol is why you know which is which."
7. "Transfer held. The readout fell, and the protocol shows exactly why."
8. "All three claims rejected by pre-declared rules. That is the protocol working. Use it on your data."
