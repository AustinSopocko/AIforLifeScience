"""Command-line entry point (WI-01; built incrementally).

Implemented: `ledger verify [--staged] [--against REF]`, `seal`, `fetch`, `recon`, `index`, `split [--check]`,
`bin`, `gtime`. Every other command in PLAN.md raises NotImplementedError until its work item lands.
Exit codes: 0 ok, 2 invariant violation, 3 protocol not sealed / dirty tree, 4 ledger verification failure.
"""
import argparse
import runpy
import sys

SCRIPTS = {"fetch": "scripts/fetch_all.py", "recon": "scripts/recon_inventory.py", "index": "scripts/build_index.py",
           "split": "scripts/make_splits.py", "bin": "scripts/potter_bin.py", "gtime": "scripts/gtime.py"}


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:2] == ["ledger", "verify"]:
        from agepretext.validation.ledger import LedgerError, verify
        ap = argparse.ArgumentParser(prog="agepretext ledger verify")
        ap.add_argument("--staged", action="store_true")
        ap.add_argument("--against")
        a = ap.parse_args(argv[2:])
        try:
            n = verify(staged=a.staged, against_ref=a.against)
        except LedgerError as e:
            print(f"ledger verify: FAIL: {e}")
            return 4
        print(f"ledger verify: OK ({n} rows, hash chain intact)")
        return 0
    if argv[:1] == ["seal"]:
        from agepretext.validation.protocol import seal
        rec = seal()
        print(f"{rec.seal_id}: protocol_hash {rec.protocol_hash} at commit {rec.git_commit[:12]} ({len(rec.components)} files)")
        return 0
    if argv and argv[0] in SCRIPTS:
        sys.argv = [SCRIPTS[argv[0]], *argv[1:]]
        runpy.run_path(SCRIPTS[argv[0]], run_name="__main__")
        return 0
    raise NotImplementedError(f"agepretext {' '.join(argv)}: not built yet (see PLAN.md §7)")


if __name__ == "__main__":
    raise SystemExit(main())
