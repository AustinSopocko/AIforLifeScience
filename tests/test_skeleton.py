"""Skeleton sanity: every module imports, and the planning documents parse."""
import importlib
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULES = [
    "agepretext", "agepretext.cli", "agepretext.config", "agepretext.invariants", "agepretext.report_numbers",
    "agepretext.data.download", "agepretext.data.index", "agepretext.data.splits", "agepretext.data.windows",
    "agepretext.data.sources.nfa", "agepretext.data.sources.potter", "agepretext.data.sources.kapucu",
    "agepretext.data.sources.epameadev", "agepretext.data.sources.epa_mi", "agepretext.data.sources.g2chvc",
    "agepretext.data.sources.fragilex",
    "agepretext.features.harmonise", "agepretext.features.potter_handcrafted", "agepretext.models.ridge_age",
    "agepretext.models.set_encoder", "agepretext.models.heads", "agepretext.models.ensemble",
    "agepretext.train.pretext", "agepretext.train.crossfit", "agepretext.eval.bootstrap", "agepretext.eval.nulls",
    "agepretext.eval.verdicts", "agepretext.eval.age", "agepretext.eval.baselines", "agepretext.eval.claim_a_fewshot",
    "agepretext.eval.claim_b_deviation", "agepretext.eval.identity_probe",
    "agepretext.eval.claim_c1_nfa", "agepretext.eval.claim_c2_wagenaar", "agepretext.validation.ledger",
    "agepretext.validation.protocol", "agepretext.validation.guards", "agepretext.validation.prereg",
    "agepretext.viz.style", "agepretext.viz.trajectory", "agepretext.viz.fewshot_curve", "agepretext.viz.probe",
    "agepretext.viz.animate", "agepretext.viz.figures",
]


def test_modules_import_and_have_contracts():
    for name in MODULES:
        mod = importlib.import_module(name)
        assert mod.__doc__ and len(mod.__doc__.strip()) > 20, f"{name} lacks a contract docstring"


def test_yaml_documents_parse():
    for p in [ROOT / "protocol/prereg.yaml", ROOT / "workitems.yaml", *ROOT.glob("configs/**/*.yaml")]:
        yaml.safe_load(p.read_text())


def test_prereg_has_no_absolute_claim_thresholds():
    """D5: every non-C hypothesis is decided by the relative rule against named gating baselines."""
    pre = yaml.safe_load((ROOT / "protocol/prereg.yaml").read_text())
    for hid, h in pre["hypotheses"].items():
        if hid in ("H-C1", "H-C2"):
            assert h["verdict"]["rule"] == "identity_rule" and "canary" in h
            continue
        assert h.get("gating_baselines"), f"{hid} has no gating baselines"
        assert "metric" in h and h["metric"]["direction"] in {"higher", "lower"}
        for b in h["gating_baselines"]:
            assert b in pre["baselines"], f"{hid} references undefined baseline {b}"


def test_workitem_deps_exist_and_acyclic():
    items = yaml.safe_load((ROOT / "workitems.yaml").read_text())["items"]
    for k, v in items.items():
        for d in v["deps"]:
            assert d in items, f"{k} depends on unknown {d}"
    seen, stack = set(), set()

    def visit(n):
        assert n not in stack, f"cycle at {n}"
        if n in seen:
            return
        stack.add(n)
        for d in items[n]["deps"]:
            visit(d)
        stack.discard(n)
        seen.add(n)

    for n in items:
        visit(n)


def test_case_table_covers_all_eight_outcomes():
    """D16: every combination of A/B/C holds|falls maps to exactly one pre-declared case."""
    import itertools
    pre = yaml.safe_load((ROOT / "protocol/prereg.yaml").read_text())
    cases = {k: v for k, v in pre["case_number"].items() if k != "collapse_rule"}
    combos = {(v["A"], v["B"], v["C"]) for v in cases.values()}
    assert combos == set(itertools.product(["holds", "falls"], repeat=3))


def test_ledger_rows_chain():
    """Structural hash-chain check; full schema verification is `agepretext ledger verify` (WI-02)."""
    import hashlib
    import json
    raw = (ROOT / "ledger/results.jsonl").read_bytes().split(b"\n")
    lines = [l for l in raw if l]
    prev = "0" * 64
    for line in lines:
        row = json.loads(line)
        assert row["prev_row_sha256"] == prev
        prev = hashlib.sha256(line + b"\n").hexdigest()


def test_ledger_genesis_row_is_the_a13_disclosure():
    """Structural check only; full schema + hash-chain verification is `agepretext ledger verify` (WI-02)."""
    import json
    lines = (ROOT / "ledger/results.jsonl").read_text().splitlines()
    assert lines, "ledger must contain the A13 disclosure as its genesis row"
    rows = [json.loads(line) for line in lines]
    assert rows[0]["prev_row_sha256"] == "0" * 64
    assert rows[0]["phase"] == "infrastructure" and rows[0]["metric"] == "disclosure_A13"
