#!/usr/bin/env bash
# Single entry point that reproduces every headline number and figure (WI-14).
# Usage: bash reproduce.sh [--profile smoke|mvr|full]
# Contract:
#   1. fetch      - download sources from origin, verify sha256 against data/manifests/
#   2. index      - build RecordingIndex (prep > plate > well > recording)
#   3. split      - regenerate SplitManifests and check they match committed splits/*.json
#   4. seal check - verify protocol hash matches the latest seal (refuses on dirty tree)
#   5. train      - P: age-pretext encoder, 4-fold batch cross-fit + final; N: ridge age, 6-fold TC cross-fit + final
#   6. eval       - H-AGE-P/N, H-A, H-C (Potter), H-B (NFA TC + NTP lockbox), all baselines (phase=reproduction rows)
#   7. figures    - every report/video figure from artefacts + ledger
#   8. report     - numbers.tex + PDF
set -euo pipefail
echo "reproduce.sh: not implemented (planning skeleton). See PLAN.md WI-O2." >&2
exit 1
