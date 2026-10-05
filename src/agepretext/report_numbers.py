"""Report number macros (WI-12).

Contract
--------
`write_numbers_tex(ledger_path, out_path, phase="confirmatory")` emits one LaTeX macro per
headline quantity, e.g. `\\newcommand{\\HBDetectLower}{0.41}` followed by a comment carrying the
source `row_id`. Only rows with the requested phase and `status == "ok"` are eligible; if two
rows claim the same macro the most recent under the latest seal wins and the collision is
listed in the report appendix. `check_no_literal_numbers(sections_dir)` fails if any
`report/sections/*.tex` contains a decimal number outside a macro (whitelist: years, section
numbers, citations).
"""


def write_numbers_tex(ledger_path: str, out_path: str, phase: str = "confirmatory") -> None:
    raise NotImplementedError("WI-12")


def check_no_literal_numbers(sections_dir: str) -> None:
    raise NotImplementedError("WI-12")
