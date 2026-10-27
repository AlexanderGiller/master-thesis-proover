#!/usr/bin/env python3
"""Experiment A: how compatible are Vampire-generated proofs with the ProoVer checker?

For every proof in results/vampire/proofs/*.s this script records
  * whether a proof (and not a saturation) was produced,
  * whether the checker's TPTP parser accepts the file (and why not),
  * which inference rules are used and how many of them are part of the
    ProoVer 2026 reference calculus (= rules occurring in ProoVer2026/PRV, Deprecated and Test),
  * proof size (number of steps),
  * optionally (--verify) the verdict of main.check_proof_file.

Usage (project root):
    python scripts/exp_vampire_compat.py [--verify] [--timeout 60]
Output: results/vampire/compat.csv and results/vampire/compat_summary.json
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

RULE_RE = re.compile(r"inference\(\s*([A-Za-z_][A-Za-z0-9_]*)")
FOF_RE = re.compile(r"^(fof|cnf|tff)\(", re.M)


def rules_in(text: str) -> collections.Counter:
    return collections.Counter(RULE_RE.findall(text))


def reference_rules() -> set[str]:
    rules: set[str] = set()
    for d in ("PRV", "Deprecated", "Test"):
        for p in (ROOT / "ProoVer2026" / d).glob("*.s"):
            rules |= set(rules_in(p.read_text()))
    return rules


def classify_parse_error(exc: Exception) -> str:
    msg = str(exc).split("\n")[0]
    if "Token('COMMA'" in msg:
        return "unsupported source/annotation syntax (introduced(...))"
    if "Token('LOWER_WORD', 'cnf')" in msg:
        return "cnf(...) formulas not supported"
    return type(exc).__name__ + ": " + msg[:80]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--proofs", default=str(ROOT / "results" / "vampire" / "proofs"))
    ap.add_argument("--summary", default=str(ROOT / "results" / "vampire" / "summary.csv"))
    ap.add_argument(
        "--verify", action="store_true", help="also run the checker (needs ATP for thm steps)"
    )
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--out", default=str(ROOT / "results" / "vampire"))
    args = ap.parse_args()

    from src.parser.parser import parse_file

    ref = reference_rules()
    status = {}
    with open(args.summary, newline="") as fh:
        for row in csv.DictReader(fh):
            status[row["Problem"]] = row["SZS_Status"]

    rows = []
    for p in sorted(Path(args.proofs).glob("*.s")):
        name = p.stem
        text = p.read_text()
        is_proof = "SZS output start Proof" in text
        rc = rules_in(text)
        total = sum(rc.values())
        in_ref = sum(n for r, n in rc.items() if r in ref)
        unknown = sorted(r for r in rc if r not in ref)
        parse_ok, parse_reason = "", ""
        if is_proof:
            try:
                parse_file(str(p))
                parse_ok = "yes"
            except Exception as exc:  # noqa: BLE001
                parse_ok, parse_reason = "no", classify_parse_error(exc)
        verdict = ""
        if args.verify and parse_ok == "yes":
            from main import check_proof_file_with_timeout

            group = "Test" if name.startswith("TST") else "PRV"
            if (
                group == "PRV"
                and not (ROOT / "ProoVer2026" / "PRV" / "Problems" / f"{name}.p").exists()
            ):
                group = "Deprecated"
            problem = ROOT / "ProoVer2026" / group / "Problems" / f"{name}.p"
            try:
                kind, res = check_proof_file_with_timeout(str(p), str(problem), args.timeout)
                if kind == "result":
                    bad = sorted(k[:-7] for k, v in res.items() if k.endswith("_issues") and v)
                    verdict = (
                        "VerifiedGood" if res.get("all_ok") else "VerifiedBad:" + ",".join(bad)
                    )
                else:
                    verdict = kind if res is None else f"{kind}: {str(res)[:60]}"
            except Exception as exc:  # noqa: BLE001
                verdict = "error: " + str(exc)[:60]
        rows.append(
            dict(
                problem=name,
                szs=status.get(name, ""),
                is_proof="yes" if is_proof else "no",
                steps=len(FOF_RE.findall(text)) if is_proof else 0,
                inferences=total,
                inferences_in_prover_calculus=in_ref,
                rules_not_in_prover_calculus=" ".join(unknown),
                parse_ok=parse_ok,
                parse_failure=parse_reason,
                checker_verdict=verdict,
            )
        )

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "compat.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    proofs = [r for r in rows if r["is_proof"] == "yes"]
    summ = {
        "files": len(rows),
        "with_proof": len(proofs),
        "parse_ok": sum(r["parse_ok"] == "yes" for r in proofs),
        "parse_failure_reasons": collections.Counter(
            r["parse_failure"] for r in proofs if r["parse_ok"] == "no"
        ),
        "proofs_using_only_prover_calculus": sum(
            r["inferences"] and r["inferences"] == r["inferences_in_prover_calculus"]
            for r in proofs
        ),
        "median_steps": sorted(r["steps"] for r in proofs)[len(proofs) // 2] if proofs else 0,
        "max_steps": max((r["steps"] for r in proofs), default=0),
        "reference_rules": sorted(ref),
    }
    tot = collections.Counter()
    for r in proofs:
        tot.update(rules_in((Path(args.proofs) / f"{r['problem']}.s").read_text()))
    summ["rule_usage_vampire"] = dict(tot.most_common())
    summ["checker_verdicts"] = dict(
        collections.Counter(r["checker_verdict"] for r in proofs if r["checker_verdict"])
    )
    summ["share_inferences_in_prover_calculus"] = round(
        sum(r["inferences_in_prover_calculus"] for r in proofs)
        / max(1, sum(r["inferences"] for r in proofs)),
        4,
    )
    summ["parse_failure_reasons"] = dict(summ["parse_failure_reasons"])
    (out / "compat_summary.json").write_text(json.dumps(summ, indent=2))
    print(
        json.dumps(
            {k: v for k, v in summ.items() if k not in ("rule_usage_vampire", "reference_rules")},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
