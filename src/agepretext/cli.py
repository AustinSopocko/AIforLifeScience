"""Command-line entry point (WI-01).

Contract
--------
`agepretext <command> [--profile PROFILE] [options]` with commands:

    recon            run WI-00 scripts, regenerate recon/RECON.md numbers + recon/inventory.json
    fetch            download sources for the profile, verify sha256 against data/manifests/
    index            build the RecordingIndex parquet for each source
    split            (re)generate SplitManifests; with --check, assert equality with committed splits/
    seal             canonicalise + hash the protocol, write protocol/seals/seal-N.json, git-tag it
    train            train the age-pretext ensemble (cross-fit on dev; final model on all dev)
    eval             run baselines and claims; --phase {exploratory,confirmatory,reproduction}
    figures          regenerate every figure in the viz.figures registry
    report           write report/generated/numbers.tex and build the PDF
    demo             drive the live demo sequence (scripts/demo.py)
    reproduce        equivalent to reproduce.sh
    ledger verify    validate hash chain + schema; --staged for pre-commit; --against REF for CI

Every command that reads data first calls validation.guards; every command that produces a
result appends a ledger row (including on error). Exit codes: 0 ok, 2 invariant violation,
3 protocol not sealed / dirty tree, 4 ledger verification failure.
"""


def main(argv: list[str] | None = None) -> int:
    raise NotImplementedError("WI-01")
