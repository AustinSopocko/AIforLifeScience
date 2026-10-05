"""Skeleton sanity: every module imports, and the planning documents parse."""
import importlib
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULES = [
    "agepretext", "agepretext.cli", "agepretext.config", "agepretext.invariants", "agepretext.report_numbers",
    "agepretext.data.download", "agepretext.data.index", "agepretext.data.splits", "agepretext.data.windows",
    "agepretext.data.sources.nfa", "agepretext.data.sources.potter", "agepretext.data.sources.epameadev",
    "agepretext.data.sources.kapucu", "agepretext.features.harmonise", "agepretext.features.canonical",
    "agepretext.features.bursts", "agepretext.features.network_spikes", "agepretext.models.feature_mlp",
    "agepretext.models.set_encoder", "agepretext.models.heads", "agepretext.models.ensemble",
    "agepretext.train.pretext", "agepretext.train.crossfit", "agepretext.eval.bootstrap", "agepretext.eval.nulls",
    "agepretext.eval.verdicts", "agepretext.eval.age", "agepretext.eval.baselines", "agepretext.eval.claim_a_fewshot",
    "agepretext.eval.claim_b_deviation", "agepretext.eval.claim_c_probe", "agepretext.validation.ledger",
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


def test_ledger_starts_empty():
    assert (ROOT / "ledger/results.jsonl").read_text() == ""
