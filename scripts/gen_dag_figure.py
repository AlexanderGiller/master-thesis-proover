#!/usr/bin/env python3
"""Draw the dependency graph (DAG) of a TSTP proof with Graphviz.

Nodes are the annotated formulas of the proof, edges point from a parent to the
step derived from it, and the fill colour shows which check of the verifier
validates the node. The result is written as PDF and PNG.

Usage:  python scripts/gen_dag_figure.py ProoVer2026/PRV/PRV089+1.s thesis/diagrams/dag_prv089
Requires the ``dot`` program of Graphviz.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import _formulas_are_complements  # noqa: E402
from src.checker.external_atp_checker import status_allows_atp  # noqa: E402
from src.parser.ast_nodes import FileSource  # noqa: E402
from src.parser.parser import load_proof  # noqa: E402

INTERNAL_RULES = {
    "copy", "duplicate", "rename_variable", "double_negation", "remove_double_negation",
    "modus_ponens", "instantiate_mp", "conjunction", "split_conjunct", "instantiate",
    "existential_gen", "weaken", "commute", "excluded_middle", "resolution",
    "paramodulation", "reflexivity", "transitivity", "rewrite",
}

COLOURS = {
    "provenance": ("#e6e6e6", "provenance check (file source)"),
    "negated": ("#fbd9b5", "negated-conjecture check"),
    "skolem": ("#cfe2f7", "Skolemization check"),
    "internal": ("#d5efd5", "internal rule checker"),
    "shortcut": ("#fff0a8", "sound shortcut (no prover call)"),
    "atp": ("#f6c9c9", "external prover"),
    "none": ("#ffffff", "no checker"),
}


def classify(step, by_name) -> str:
    inf = step.inference
    if inf is None:
        return "provenance" if isinstance(step.raw_source, FileSource) else "none"
    if str(step.role) == "negated_conjecture":
        return "negated"
    if inf.rule == "skolemize":
        return "skolem"
    if inf.rule in INTERNAL_RULES:
        return "internal"
    if inf.rule == "consequence" and len(inf.parents) == 2:
        f = step.formula
        parents = [by_name.get(p) for p in inf.parents]
        if repr(f) == "$false" and all(parents) and _formulas_are_complements(parents[0].formula, parents[1].formula):
            return "shortcut"
    return "atp" if status_allows_atp(inf.status) else "none"


def esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def main() -> None:
    proof_path, out_stem = Path(sys.argv[1]), Path(sys.argv[2])
    proof = load_proof(str(proof_path))
    by_name = {s.name: s for s in proof.steps}
    lines = [
        "digraph proof {",
        '  graph [rankdir=TB, nodesep=0.35, ranksep=0.45, fontname="Helvetica"];',
        '  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10, margin="0.12,0.06"];',
        '  edge [arrowsize=0.7, color="#555555"];',
    ]
    used = set()
    for s in proof.steps:
        kind = classify(s, by_name)
        used.add(kind)
        inf = s.inference
        how = f"{inf.rule} [{inf.status}]" if inf else "file(...)"
        label = f"{s.name}  ({s.role})\\n{esc(repr(s.formula))}\\n{esc(how)}"
        lines.append(f'  "{s.name}" [label="{label}", fillcolor="{COLOURS[kind][0]}"];')
    for s in proof.steps:
        if s.inference:
            for p in s.inference.parents:
                if p in by_name:
                    lines.append(f'  "{p}" -> "{s.name}";')
    # legend
    lines.append('  subgraph cluster_legend { label=""; style=invis;')
    prev = None
    for kind in COLOURS:
        if kind not in used:
            continue
        lines.append(f'    "leg_{kind}" [label="{COLOURS[kind][1]}", fillcolor="{COLOURS[kind][0]}", fontsize=9];')
        if prev:
            lines.append(f'    "{prev}" -> "leg_{kind}" [style=invis];')
        prev = f"leg_{kind}"
    lines.append("  }")
    lines.append("}")
    dot = "\n".join(lines) + "\n"
    out_stem.parent.mkdir(parents=True, exist_ok=True)
    out_stem.with_suffix(".dot").write_text(dot, encoding="utf-8")
    for fmt in ("pdf", "png"):
        subprocess.run(["dot", f"-T{fmt}", "-Gdpi=200", "-o", str(out_stem.with_suffix("." + fmt))], input=dot, text=True, check=True)
    print("wrote", out_stem.with_suffix(".pdf"))


if __name__ == "__main__":
    main()
