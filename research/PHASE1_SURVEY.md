# Phase 1: Power survey (public in vitro MEA developmental corpora)

Date: 2026-10-07. This is web and metadata verification only. No new corpus has been downloaded into `data/`.

**Reserved as CONFIRMATORY and excluded from the dev pool:** Kapucu 2022 and EPA NFA 2018.

## 1.1 Corpora found

**What counts as a prep.** "Preps" means independent preparations: dissection, plating date or differentiation batch. Wells, chips, plates and arrays from one prep are not counted. A **YES** dataset meets all four conditions:
1. public;
2. spike-level, or raw data we can spike-detect;
3. prep IDs recoverable;
4. a developmental series labelled by DIV.

**Verification levels:**
- (b) file listing or in-file metadata inspected;
- (a) repository metadata only;
- (c) paper only.

### Usable now

| Corpus | Source | Species / tissue | Independent preps (evidence) | DIV range | Electrodes / platform | Format | Licence | Size | Verification | Fit |
|---|---|---|---|---|---|---|---|---|---|---|
| Wagenaar 2006 (in hand) | potterlab.bme.gatech.edu | rat cortex E18 | 8 dissections (paper, batch IDs in filenames) | 3–39, near daily | MCS 59 | spike times | cite-only | 665 MB | (b), fetched | YES (dev) |
| Cotterill 2016 EPAmeadev | github.com/sje30/EPAmeadev | rat cortex P0 | **15** culture dates. Filenames show 16 dates, but one is almost certainly a mistyped 20140528; the paper says 15 | 2/5/7/9/12; 4 preps run to 14–37 | Axion 48-well, 16 per well | spike times (HDF5, 107 files) | "free to use, cite"; paper CC-BY 3.0 | 307 MB | (b) | YES |
| Ball 2017 EPA "Mutual Information" | doi 10.23719/1375317 | rat cortex | 4 dates, **+1 new** (20140423); 3 overlap EPAmeadev dissections | 2/5/7/9/12 | Axion 48-well | Axion spike lists | US public domain | 203 MB | (a), partial | YES (12 control wells per plate only) |
| Charlesworth 2015 g2chvcdata | github.com/sje30/g2chvcdata | mouse C57, 15 hippocampal + 8 cortical | **23** plating dates, read from `meta/DIV0` in one file per array (93 arrays). No overlap between hippocampal and cortical dates | 6/7–28/30, twice weekly | MCS 59 | spike times (HDF5) | GPL-2 | 303 MB | (b), plating dates read | YES. Exclude KN62-treated cortical arrays (from DIV 17) and UO126/APV hippocampal series |
| Moskalyuk/Giugliano 2020 Fragile-X | doi 10.6084/m9.figshare.6531293 | mouse cortex, WT + Fmr1-KO | **10** culture sessions on distinct dates (README): 5 WT, 5 KO; 57 MEAs | 7–35 | MCS 60 | spike times (.mat) | CC-BY 4.0 | 0.24 GB | (b) | YES. Genotype is a covariate; WT-only gives 5 |
| Pavlinek/Srivastava (KCL) organoids | doi 10.18742/30394168 (+ raw items) | human, 6 lines, dissociated cortical organoids | **15** line × batch differentiations (metadata.csv) | days post-dissociation 6/15/22/29/37; treatment from day 29 | Axion 24-well, 16 per well (inferred) | **raw only** (spike detection needed) | CC0 | about 138 GB | (b) | YES, raw-only |

### Partial (prep IDs or DIV not recoverable, or no developmental series)

| Corpus | Preps | Problem |
|---|---|---|
| Charlesworth 2016 g2c-1 (Zenodo 31085, CC0, 1.34 GB) | 90 cultures in the paper (35 WT) | Metadata has no prep or date field. WT files overlap g2chvcdata. Knockout preps could add clusters only if prep IDs can be rebuilt |
| DANDI:002020 (rat cortex, MaxOne, daily) | 7 chips, about 5–7 platings (inferred from dates) | **No DIV in the files.** Plating dates must come from the authors |
| Mossink 2021 (Mendeley, 50 MB) | ≥20 batches | Deposited data is a single DIV 27–35 window; no developmental series |
| autoMEA (Zenodo 12685150, 37 GB raw) | about 10 batch codes | Mostly DIV 7 and 14 pairs; batches undocumented |
| Trujillo 2019 / Akarca 2025 / DeePhys / DANDI:001374 / 001603 | 1–3 or unknown | Single plate, unknown preps, proprietary format, or 1.6 TB raw |

### Rejected
- EPA NFA papers (Brown 2016, Frank 2017, Shafer 2019, Carstens 2022): well-level features only.
- MEA-NAP sample data: 1 prep.
- Sharf 2022: one developing organoid.
- CRCNS ssc-3: organotypic, single timepoint.
- EBRAINS: no dissociated-culture MEA in the public index.
- CARMEN: offline.
- Other DANDI, Zenodo, Dryad and figshare candidates: stimulation-only, acute, or single-prep (full list in the session survey notes).

## 1.2 Cluster count and projected interval width

| Pool | Independent preps |
|---|---|
| Wagenaar 8 + EPAmeadev 15 + EPA-MI 1 + g2chvcdata 23 + Fragile-X 10 | **57 rodent** (52 if Fragile-X is restricted to WT) |
| + KCL human organoids 15 (after spike detection from 138 GB raw) | **72** |
| Partial sets, if resolved (002020, g2c-1 knockout lines, Mossink) | could add about 5–40, all unconfirmed |

**Target ≥ 25 clusters: met** (57 confirmed, spike-level, about 0.9 GB total excluding KCL).

**Projected 95% half-width** of the age MAE (log-DIV) under the batch-clustered bootstrap. This scales the cluster-level variance observed in the Wagenaar dev results by √(8/C) (`scripts/power_projection.py`). Observed effect so far: encoder − BL-1 = −0.016 log-DIV.

| C | Half-width (encoder MAE) | Half-width (paired encoder − BL-1) | Min detectable effect, sealed rule (UB vs point) | Min detectable effect, paired test |
|---|---|---|---|---|
| 8 | 0.058 | 0.044 | 0.058 | 0.044 |
| 25 | 0.033 | 0.025 | 0.033 | 0.025 |
| 52 | 0.023 | 0.017 | 0.023 | 0.017 |
| 57 | 0.022 | 0.017 | 0.022 | 0.017 |
| 72 | 0.019 | 0.015 | 0.019 | 0.015 |
| ~99 | 0.016 | — | detects 0.016 | — |
| ~59 | — | 0.016 | — | detects 0.016 |

## Findings that constrain Phases 2–4

1. **25 clusters is not enough for the effect seen so far.** At the observed effect (0.016), the sealed relative rule needs about 99 clusters and a paired comparison about 59. With 57 rodent clusters, the encoder must improve to about 0.022 better than BL-1 under the current rule, or about 0.017 under a paired rule. That is roughly 1.1–1.4× the current effect, before heterogeneity.
2. **The projection is optimistic.** It assumes pooled clusters behave like Wagenaar batches. Pooling adds species, region, platform and lab variance, which will widen intervals.
3. **Preps are not labs.** The 57 clusters come from **4 labs/sources**: Potter (Georgia Tech), EPA (Shafer), Grant/Eglen (Edinburgh/Cambridge), Giugliano (Antwerp/SISSA). Inference over preps is "within these labs". Any claim of generalisation across labs rests on n ≈ 4, plus the sealed confirmatory labs.
4. **Age is confounded with lab.** DIV windows differ by source: EPA mostly 2–12, Charlesworth 6–30, Wagenaar 3–39, Fragile-X 7–35. A pooled age regressor can lower its error by recognising the lab, which is exactly the shortcut Claim C forbids. Dev evaluation must therefore include leave-one-lab-out and an overlapping-window (DIV 7–12) stratum, and the lab/batch identity probes must run on the pooled model.
5. **Heterogeneity is unavoidable:**
   - species: rat, mouse, human;
   - tissue: cortex, hippocampus;
   - platform: MCS 59-electrode 8×8 grid, Axion 16-electrode wells, Axion 24-well;
   - treatments in the files: KN62, UO126, APV, Fmr1-KO genotype, EPA dose wells.

   This argues for Phase 3.1 (set encoder) being a prerequisite, not an option.
6. **The confirmatory corpus has been touched.** Kapucu and NFA were both inspected earlier: counts, layout and medians (ledger rows 1–4), and Kapucu wells-with-spikes counts (K3). Neither has been used by any model. The Phase 2 prereg must disclose this. Kapucu's 3 rat preps and NFA's 5 NTP-only lockbox preps also limit what the final confirmatory run can resolve.
