# WI-00 Data Reconnaissance Report (TEMPLATE)

> Fill every ⟨…⟩ with evidence: a number, plus the script and line that produced it.
> `make recon` must regenerate every number here from a clean environment.
>
> **Order of operations (mandatory):**
> 1. `agepretext split` creates the NFA lockbox and fold manifests, seeded, **before** any
>    descriptive statistic is computed.
> 2. Descriptive statistics are computed on dev (TC) preps only.
> 3. The lockbox (NTP) is opened for schema and row counts only.
>
> Pre-recon evidence gathered while drafting the plan is in `PLAN.md` §3. Re-verify it here;
> do not copy it.

## Kill-gate verdict

| Gate | Verdict | Evidence |
|---|---|---|
| K1 no pretext | ⟨PASS/FAIL⟩ | ⟨⟩ |
| K2 no Claim B | ⟨PASS/FAIL⟩ | ⟨⟩ |
| K3 no Claim A task | ⟨PASS/FAIL⟩ | ⟨⟩ |
| K4 legal | ⟨PASS/FAIL⟩ | ⟨⟩ |

Signed off by operator: ⟨name, date⟩ → if all pass, proceed to WI-05. Otherwise go to the
fallback named in `PLAN.md` §4.

## R1 — Per-recording DIV metadata

| Source | DIV field location | Parse rate | Notes |
|---|---|---|---|
| NFA 2018 | `DIV` column | ⟨⟩ | |
| Potter 2006 | filename `<batch>-<culture>-<DIV>.spk.txt.bz2` | ⟨⟩ | |
| Kapucu 2022 | HDF5 `/DataInfo/DIV`; also filename? | ⟨⟩ | spike CSVs: where is DIV? |
| EPAmeadev | filename `DIVnn` | ⟨⟩ | |

## R2 — Age × culture distribution

- Table per source: preps, plates/dishes, wells, recordings, DIV levels, timepoints per well.
- Figure `recon/figures/<source>_div_by_culture.png`: heatmap of DIV × culture.
- Descriptive check (dev controls only): Spearman ρ(DIV, meanfiringrate) = ⟨⟩,
  ρ(DIV, burst.per.min) = ⟨⟩.

## R3 — Age series × perturbation series

- **(a) NFA:**
  - dosing schedule = ⟨DIV of first dose, re-dosing DIVs⟩ (cite paper section);
  - controls per plate = ⟨⟩;
  - compound → plate → prep nesting = ⟨⟩;
  - plate layout map (F2) = ⟨⟩.
- **(b) Public NFA spike lists?** Searched:
  - EPA ScienceHub ⟨⟩
  - CCTE Clowder ⟨⟩
  - Shafer 2019 suppl. ⟨⟩
  - Brown 2016 suppl. ⟨⟩
  - USEPA GitHub ⟨⟩
  - Verdict: ⟨FOUND/NOT FOUND⟩. **If FOUND, raise decision D1 again (promote S-4).**
- **(c) EPAmeadev treated plates?** ⟨⟩

## R4 — Downstream task candidates

| Task | Label source | Positives | Preps with positives | Label independent of activity? | Ceiling check (BL-2 k=10, dev) | Verdict |
|---|---|---|---|---|---|---|
| T1 early cytotoxicity | AB/LDH assay | ⟨⟩ | ⟨⟩ | yes (different assay) | (computed in WI-11, not here) | ⟨⟩ |
| T2 held-out-compound exposure | design | ⟨⟩ | ⟨⟩ | yes | | ⟨⟩ |
| T3 DNT reference class | literature (F4) | ⟨⟩ | ⟨⟩ | yes | | ⟨⟩ |
| T4 Potter density (stretch) | design | ⟨⟩ | ⟨⟩ | yes | | ⟨⟩ |

## R5 — Minimum download

| File | Bytes | sha256 | Needed for |
|---|---|---|---|
| `NTP_TC_Analysis.zip` | 159,560,650 (verify) | ⟨⟩ | MVR |
| ⟨…⟩ | | | |

## R6 — Licences

| Source | Licence (verbatim copy in `recon/licences/`) | Redistribution decision |
|---|---|---|
| NFA 2018 | EPA ScienceHub | ⟨⟩ |
| Potter 2006 | "cite the article"; code GPL-2 | CITE-ONLY, download at runtime |
| Kapucu 2022 | CC BY 4.0 | ⟨⟩ |
| EPAmeadev | "free to use … cite" | ⟨⟩ |
| MEA-NAP | ⟨⟩ (MATLAB, cite only) | not a dependency |

## Facts F1–F5

- **F1** AB/LDH replicate → plate mapping: ⟨⟩
- **F2** Control well positions and concentration-column order: ⟨⟩
- **F3** `cv.time`, `cv.network` part of EPA's 17 endpoints? ⟨⟩ → final list in `configs/features/nfa17.yaml`
- **F4** NTP DNT reference designations available? ⟨⟩
- **F5** Hardware per source (electrodes, layout, pitch): ⟨⟩
