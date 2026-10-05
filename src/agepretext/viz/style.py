"""Shared plotting style (WI-12).

Contract
--------
`apply_style()` sets a fixed bundled font (DejaVu Sans), a colour-blind-safe palette, 1920x1080
video canvas / report column widths, and `svg.hashsalt` + metadata stripping so identical inputs
render byte-identical files. `stamp(fig, protocol_hash, row_id)` adds the provenance footer
required on every frame and figure.
"""


def apply_style() -> None:
    raise NotImplementedError("WI-12")


def stamp(fig, protocol_hash: str, row_id: str) -> None:
    raise NotImplementedError("WI-12")
