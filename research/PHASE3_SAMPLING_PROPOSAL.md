# Phase 3.0: EPA imbalance — training sampling scheme (DECIDED: option A, frozen by ledger row before any fit)

This scheme is frozen at Seal 3 (`configs/train/*.yaml`). It needs an operator decision before the first Phase 3 fit.

## The imbalance, measured

Dev data after Amendment A1 and F1 QC, by lab:

| Lab | Preps | Recordings | Recordings per prep (min/median/max) | DIVs per prep (median) | Recordings % | Windows % | Electrode-windows % | Preps % | Mean log-DIV |
|---|---|---|---|---|---|---|---|---|---|
| eglen_grant | 22 | 518 | 6 / 21 / 72 | 7 | 8.1 | 6.5 | 14.7 | 47.8 | 2.70 |
| epa_shafer | 16 | 5,328 | 60 / 264 / 1,152 | 5 | **83.7** | **76.1** | 46.4 | 34.8 | **2.08** |
| potter_gatech | 8 | 521 | 27 / 42 / 161 | 19 | 8.2 | 17.3 | 38.9 | 17.4 | 2.71 |

- **Where the "10×" comes from:** wells, not cultures. Each EPA plate records 48 (EPAmeadev) or 12 (EPA-MI) sibling
  wells of **one** culture at each DIV. Those wells are pseudo-replicates of a single prep-by-DIV cell.
- **Label skew:** 76% of EPA recordings are DIV ≤ 12. Recording-weighted training therefore also shifts the *label*
  distribution young, and rewards "looks like EPA → young". That is the lab-age shortcut that LOLO and H-LAB police.
- **Current trainer:** it samples 2 windows per recording per epoch, which is recording-weighted, i.e. 84% EPA.

## Options

### A. Cluster-equal, DIV-stratified (RECOMMENDED)

**How it works.** Each epoch, every training cluster (prep) contributes the same number of windows, m. Within a
cluster, a draw picks a DIV uniformly from that cluster's DIVs, then a recording at that DIV, then a window. The draws
are resampled every epoch.

**Resulting lab shares** (prep counts): eglen 48%, EPA 35%, potter 17%.

**For:**
- It is the same unit as the sealed evaluation weighting (cluster-equal MAE) and the bootstrap. Training then optimises
  the quantity that is scored.
- It counts EPA's 48 sibling wells once per prep-by-DIV, which is the right independence model.
- DIV stratification flattens each prep's label distribution. EPA's 48-wells-per-DIV and Potter's 19-DIV series stop
  dominating within their own clusters.
- It adds no new tunable parameter. m is only a compute knob: m ≈ 277 matches the current epoch size of about 12.7k
  windows.
- LOLO folds inherit it unchanged.

**Against:**
- Small eglen preps (6 recordings) are revisited often, which risks memorising them. Electrode-subset augmentation and
  window resampling soften this.
- Each EPA prep-by-DIV cell is drawn about 4× more often than a Potter one, because EPA has fewer DIVs per prep.
- Lab shares follow prep counts, not labs.

### B. Lab-equal, then cluster-equal within lab

**How it works.** Each lab gets one third of each epoch (half in a 2-lab LOLO fold). Within a lab, sampling is as in A.

**For:** it matches the LOLO aggregate (lab-equal) and the cross-lab aim. Lab, species and platform are balanced by
construction.

**Against:**
- Potter's 8 preps get a third of training. Each Potter prep weighs 4.2%, against 2.1% for EPA and 1.5% for eglen.
  Training then leans on the idiosyncrasies of the fewest preps.
- The effective number of independent units falls from 46 to about 39 (Kish).
- In LOLO folds the split is 50/50 whatever the prep counts (e.g. EPA 16 vs eglen 22), so the training mix changes more
  between folds and the final model than under A.

### C. Cap recordings per prep-by-DIV cell, then recording-uniform

**How it works.** Keep at most k recordings per (prep, DIV) cell, resampled each epoch. Then sample recordings
uniformly, as the current trainer does. At k = 4 the recording shares become EPA 33%, eglen 33%, potter 35%.

**For:**
- It is the smallest change to the existing trainer.
- It targets exactly the pseudo-replication (wells per plate-by-DIV) and nothing else.

**Against:**
- It adds a hyperparameter, k, that changes lab weights and so must be frozen blind. EPA's share is 27% at k = 2,
  33% at k = 4 and 44% at k = 8.
- Lab weights become a by-product of each lab's DIV *schedule*. Potter's near-daily series would carry most of the
  late-DIV signal.
- It does not match the evaluation weighting.

## Recommendation: A

A weights preps equally, which is the unit the protocol already treats as independent everywhere else (bootstrap,
cluster-equal MAE, splits). It removes the well pseudo-replication without adding a free parameter. B buys lab balance
by over-weighting the 8 Potter preps. C introduces a parameter that sets lab weights indirectly.

**Proposed commitment.** Freeze the scheme now, by ledger row, before any Phase 3 fit. LOLO results then cannot be used
to choose between A, B and C. Report B as a single sensitivity run on the final architecture, not used for any
decision.

**Interaction to note for the architecture work, not part of this decision.** EPA windows carry 16 electrodes and MCS
windows carry 59–60. The trainer's existing electrode-subset augmentation (subsets of 16 up to E) already exposes the
encoder to 16-electrode views of MCS data.

## Decision (operator, 2026-10-08)

**Option A**, frozen in `configs/train/sampling.yaml` by ledger row before any Phase 3 fit. Recorded reasoning: prep is
the unit that the splits, the bootstrap and the scoring already treat as independent, so training and evaluation
agree, and A adds no free parameter.

**What the B sensitivity run tests.** Under A the lab shares are eglen 48 / EPA 35 / Potter 17. Potter is the only lab
with near-daily DIV 3–39 coverage, and it contributes least. Option B runs once on the final architecture as a
pre-declared sensitivity check that decides nothing. It tests whether giving Potter a third of training changes the
result.
