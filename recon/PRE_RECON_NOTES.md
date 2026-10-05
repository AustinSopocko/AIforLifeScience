# Pre-recon commands (evidence behind PLAN.md §3)

These are the ad-hoc checks run while drafting the plan. WI-00 must turn them into committed
scripts. Statistics here were computed on both TC and NTP before any split existed. That is
disclosed as assumption A13. The NTP figures quoted are row counts, schema and DIV medians
only, and no model was fit.

```bash
# EPA NFA archive size and listing
curl -sSIL https://pasteur.epa.gov/uploads/10.23719/1503191/NTP_TC_Analysis.zip   # Content-Length: 159560650
curl -sS -o ntp.zip https://pasteur.epa.gov/uploads/10.23719/1503191/NTP_TC_Analysis.zip && unzip -l ntp.zip
unzip ntp.zip "New TC/sourceData/*" "New NTP/sourceData/*"
# pandas: shape, DIV counts, unique date / Plate.SN / trt, dose==0 wells, well positions of controls,
#         NaN fractions, AB<0.7 counts, control medians of meanfiringrate and burst.per.min by DIV

# Potter dense index: file count, cultures, DIV coverage, one file's size and format
curl -sS https://potterlab.bme.gatech.edu/development-data/html/daily.spont.dense.text.html
curl -sSI https://potterlab.bme.gatech.edu/development-data/simple-text/daily/spont/dense/2-1-20.spk.txt.bz2  # 690161 bytes
```

## Added 2026-10-05 (v2 plan): Potter batch structure and Kapucu layout

```bash
# Potter: cultures per batch for dense/sparse/small (index pages only; no spike file parsed)
for p in dense sparse small; do curl -sS https://potterlab.bme.gatech.edu/development-data/html/daily.spont.$p.text.html \
  | grep -oE "$p/[0-9]+-[0-9]+-[0-9]+\.spk"; done
# Kapucu: GIN folder listing (HTML), then one spike CSV for format only
curl -sS https://gin.g-node.org/NeuroGroup_TUNI/Comparative_MEA_dataset/src/master/Data
curl -sSL https://gin.g-node.org/NeuroGroup_TUNI/Comparative_MEA_dataset/raw/master/Data/hPSC_MEA1/hPSC_MEA1_spikes_noise_explogs/hPSC_20517_MEA1_DIV28_spikes.csv \
  | head -5    # 9,369,904 bytes; 601,688 lines; header Channel,Time
```
These checks are recorded in ledger row 1 (A13 disclosure).
