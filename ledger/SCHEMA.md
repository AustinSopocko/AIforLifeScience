# Results ledger: format and rules

`ledger/results.jsonl` is UTF-8, LF line endings, one JSON object per line. Rows are **never**
deleted or edited. Three things enforce this:
1. The pre-commit hook `ledger-append-only` rejects any diff to `results.jsonl` that is not
   pure line additions at EOF.
2. CI runs `agepretext ledger verify`, which re-validates the hash chain and schema for every
   row and checks append-only against `origin/<base>`.
3. Each row embeds `prev_row_sha256`, so any rewrite breaks every later row.

A run is ledgered **whether or not it supports a claim**: exploratory, failed, crashed after
data load, refuting and confirmatory runs alike. A crashed run gets a row with
`status: "error"`.

## Row schema (v1)

| Field | Type | Meaning |
|---|---|---|
| `row_id` | str (ULID) | Sortable unique ID. Video frames and report figures cite it. |
| `prev_row_sha256` | str | sha256 of the previous line's exact bytes (genesis: 64 × "0"). |
| `timestamp_utc` | str (ISO 8601) | When the row was written. |
| `phase` | enum | `exploratory` · `confirmatory` · `reproduction` · `infrastructure` |
| `status` | enum | `ok` · `error` |
| `hypothesis_id` | str | `H-AGE`, `H-A`, `H-B`, `H-C`, `BL-n`, or `none` |
| `claim` | enum | `age` · `A` · `B` · `C` · `baseline` · `none` |
| `metric` | str | E.g. `auroc_k10_minus_best_k50`, `excess_balanced_accuracy`. |
| `value` | float \| null | Point estimate. |
| `ci_lower`, `ci_upper` | float \| null | Interval bounds. |
| `ci_method` | str | E.g. `cluster_percentile_bootstrap`. |
| `n_clusters` | int | Number of independent preps behind the estimate. |
| `cluster_unit` | str | `prep` / `plate` / `batch` / `dish` |
| `verdict` | enum | `SUPPORTS` · `REFUTES` · `INCONCLUSIVE` · `N/A`. Computed by `eval/verdicts.py` from `protocol/prereg.yaml`. |
| `kill_condition_triggered` | bool | |
| `protocol_hash` | str | sha256 from `validation/protocol.py` at run time. |
| `seal_id` | str | `seal-1`, `seal-2`, … (the seal this protocol hash matches). |
| `prereg_sha256` | str | Hash of `protocol/prereg.yaml` + `PREREGISTRATION.md`. |
| `git_commit` | str | Full SHA. The tree must be clean (enforced). |
| `config_sha256` | str | Hash of the resolved, canonicalised config. |
| `split_manifest_sha256` | str | Hash of the `SplitManifest` used. |
| `data_manifest_sha256` | str | Hash of `data/manifests/*.sha256` contents used. |
| `env_lock_sha256` | str | Hash of `requirements.lock`. |
| `seeds` | list[int] | |
| `lockbox_opened` | bool | True only on lockbox-reading runs. |
| `artifacts` | list[{path, sha256}] | Outputs (predictions, figures) produced by the run. |
| `duration_s` | float | |
| `notes` | str | Free text. Never used by code to compute verdicts. |

## Example row (illustrative, not a real result)

```json
{"row_id":"01J9ZEXAMPLE0000000000000","prev_row_sha256":"0000…0000","timestamp_utc":"2026-10-06T12:00:00Z","phase":"exploratory","status":"ok","hypothesis_id":"BL-0","claim":"baseline","metric":"mae_log_div","value":null,"ci_lower":null,"ci_upper":null,"ci_method":"cluster_percentile_bootstrap","n_clusters":12,"cluster_unit":"prep","verdict":"N/A","kill_condition_triggered":false,"protocol_hash":"…","seal_id":"seal-1","prereg_sha256":"…","git_commit":"…","config_sha256":"…","split_manifest_sha256":"…","data_manifest_sha256":"…","env_lock_sha256":"…","seeds":[0],"lockbox_opened":false,"artifacts":[],"duration_s":0.0,"notes":"example only"}
```

## Derived views (generated, never hand-edited)

- `ledger/results.csv`: flat export for humans (gitignored, regenerated).
- `report/generated/numbers.tex`: macros for the report. Each macro is tied to a `row_id`.
