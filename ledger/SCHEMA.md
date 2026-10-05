# Results ledger: format and rules

`ledger/results.jsonl` is UTF-8, LF line endings, one JSON object per line. Rows are **never**
deleted or edited. Three things enforce this:
1. The pre-commit hook `ledger-append-only` rejects any diff to `results.jsonl` that is not
   pure line additions at EOF.
2. CI runs `agepretext ledger verify`, which re-validates the hash chain and schema for every
   row and checks append-only against `origin/<base>`.
3. Each row embeds `prev_row_sha256`, so any rewrite breaks every later row.

Rows are serialised as canonical JSON (sorted keys, compact separators, UTF-8) so `prev_row_sha256`
is reproducible.

A run is ledgered **whether or not it supports a claim**: exploratory, failed, crashed after
data load, refuting and confirmatory runs alike. A crashed run gets a row with
`status: "error"`.

## Row schema (v2)

| Field | Type | Meaning |
|---|---|---|
| `row_id` | str (ULID) | Sortable unique ID. Video frames and report figures cite it. |
| `prev_row_sha256` | str | sha256 of the previous line's exact bytes (genesis: 64 × "0"). |
| `timestamp_utc` | str (ISO 8601) | When the row was written. |
| `phase` | enum | `exploratory` · `confirmatory` · `reproduction` · `infrastructure` |
| `status` | enum | `ok` · `error` |
| `hypothesis_id` | str | `H-AGE-P`, `H-AGE-N`, `H-A`, `H-B`, `H-C`, a baseline ID (`BL-0`, `BL-A1`, …), or `none` |
| `claim` | enum | `age` · `A` · `B` · `C` · `baseline` · `none` |
| `metric` | str | E.g. `mae_ours_k4`, `detection_rate`, `excess_balanced_accuracy`, `canary_power`, `disclosure_A13`, `cut_order_applied`. |
| `value` | float \| null | Point estimate. |
| `ci_lower`, `ci_upper` | float \| null | Interval bounds. |
| `ci_method` | str | E.g. `cluster_percentile_bootstrap`. |
| `n_clusters` | int | Number of independent preps behind the estimate. |
| `cluster_unit` | str \| null | `batch` (Potter prep) / `prep` (NFA) / `culture` / `plate` (sensitivity) |
| `verdict` | enum | `SUPPORTS` · `REFUTES` · `INCONCLUSIVE` · `N/A`. Computed by `eval/verdicts.py` from `protocol/prereg.yaml`. |
| `kill_condition_triggered` | bool | |
| `protocol_hash` | str \| null | sha256 from `validation/protocol.py` at run time. Null only for `phase: infrastructure` rows written before Seal #1 (e.g. the A13 disclosure). |
| `seal_id` | str \| null | `seal-1`, `seal-2`, … (null under the same exception). |
| `prereg_sha256` | str | Hash of `protocol/prereg.yaml` + `PREREGISTRATION.md`. |
| `git_commit` | str | Full SHA. The tree must be clean (enforced). |
| `config_sha256` | str | Hash of the resolved, canonicalised config. |
| `split_manifest_sha256` | str | Hash of the `SplitManifest` used. |
| `data_manifest_sha256` | str | Hash of `data/manifests/*.sha256` contents used. |
| `env_lock_sha256` | str \| null | Hash of `requirements.lock` (null before WI-01 creates it). |
| `seeds` | list[int] | |
| `lockbox_opened` | bool | True only on lockbox-reading runs. |
| `artifacts` | list[{path, sha256}] | Outputs (predictions, figures) produced by the run. |
| `duration_s` | float | |
| `notes` | str | Free text. Never used by code to compute verdicts. |

## Row 1 (genesis)

Row 1 is the operator-accepted **A13 pre-split disclosure** (PREREGISTRATION.md §6). It is
`phase: infrastructure`, and its protocol fields are null because it predates Seal #1.

## Example row (illustrative, not a real result)

```json
{"row_id":"01J9ZEXAMPLE0000000000000","prev_row_sha256":"0000…0000","timestamp_utc":"2026-10-06T12:00:00Z","phase":"confirmatory","status":"ok","hypothesis_id":"BL-0","claim":"baseline","metric":"mae_log_div","value":null,"ci_lower":null,"ci_upper":null,"ci_method":"cluster_percentile_bootstrap","n_clusters":8,"cluster_unit":"batch","verdict":"N/A","kill_condition_triggered":false,"protocol_hash":"…","seal_id":"seal-1","prereg_sha256":"…","git_commit":"…","config_sha256":"…","split_manifest_sha256":"…","data_manifest_sha256":"…","env_lock_sha256":"…","seeds":[0],"lockbox_opened":false,"artifacts":[],"duration_s":0.0,"notes":"example only"}
```

## Derived views (generated, never hand-edited)

- `ledger/results.csv`: flat export for humans (gitignored, regenerated).
- `report/generated/numbers.tex`: macros for the report. Each macro is tied to a `row_id`.
