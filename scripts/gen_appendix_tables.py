#!/usr/bin/env python3
"""Write the per-proof result tables of the appendix from results/eval/runs.json.

Output: thesis/generated/tab_app_prv.tex and tab_app_tst.tex (longtable; needs \\usepackage{longtable}).
Usage:  python scripts/gen_appendix_tables.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "thesis" / "generated"


def status(rec: dict) -> str:
    if rec.get("timeout"):
        return "Timeout"
    if rec.get("error") or rec.get("all_ok") is None:
        return "Error"
    return rec.get("verdict") or ("VerifiedGood" if rec["all_ok"] else "VerifiedBad")


def outcome(expected: str, st: str) -> str:
    if st in ("Timeout", "Unknown"):
        return "abstain"
    good = st == "VerifiedGood"
    if expected == "CORRECT":
        return "ok" if good else "wrong reject"
    if expected == "INCORRECT":
        return "wrong accept" if good else "ok"
    return "edge case"


def tex(s: str) -> str:
    return s.replace("_", "\\_").replace("+", "{+}")


def table(rows: list[dict], caption: str, label: str) -> str:
    lines = [
        "\\begin{longtable}{@{}l l l l r r@{}}",
        f"\\caption{{{caption}}}\\label{{{label}}}\\\\",
        "\\toprule",
        "Proof & Expected & Status & Result & Time (s) & ATP calls \\\\",
        "\\midrule",
        "\\endfirsthead",
        "\\toprule",
        "Proof & Expected & Status & Result & Time (s) & ATP calls \\\\",
        "\\midrule",
        "\\endhead",
        "\\bottomrule",
        "\\endlastfoot",
    ]
    for r in sorted(rows, key=lambda x: x["name"]):
        st = status(r)
        t = r.get("total_wall_median", r.get("total_wall", 0.0)) or 0.0
        lines.append(
            f"\\texttt{{{tex(r['name'].removesuffix('.s'))}}} & {r['expected'].lower()} & "
            f"{st} & {outcome(r['expected'], st)} & {t:.2f} & {r.get('atp_calls') or 0} \\\\"
        )
    lines.append("\\end{longtable}")
    return "\n".join(lines) + "\n"


def main() -> None:
    runs = json.loads((ROOT / "results" / "eval" / "runs.json").read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    prv = [r for r in runs if r["group"] == "PRV"]
    tst = [r for r in runs if r["group"] == "TST"]
    (OUT / "tab_app_prv.tex").write_text(
        table(prv, "Results for each proof of the ProoVer set (official proofs and samples).", "tab:app-prv"),
        encoding="utf-8",
    )
    (OUT / "tab_app_tst.tex").write_text(
        table(tst, "Results for each proof of the TST set (own test proofs).", "tab:app-tst"),
        encoding="utf-8",
    )
    print(f"wrote {len(prv)} PRV and {len(tst)} TST rows")


if __name__ == "__main__":
    main()
