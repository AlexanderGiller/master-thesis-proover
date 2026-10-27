#!/usr/bin/env python3
"""Run the verifier on the generated extra tests (ProoVer2026/Extra) and
compare the verdicts with the ground truth in EXT_expected.csv.

Record the verdict and the rule-specific issue maps that fired per case, so
that a rejection caused by the rule checker can be told apart from a rejection
that only comes from the final consequence step ($false).

Usage:  python scripts/exp_extra_tests.py [--dir ProoVer2026/Extra] [--out results/extra]
Needs the external ATP (Vampire) for the consequence step; see EXTERNAL_ATP_BINARY.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import main as verifier  # noqa: E402

verifier.DEBUG_PROOF_FLOW = False

RULE_KEYS = {
    "resolution": ["resolution_issues"],
    "paramodulation": ["paramodulation_issues"],
    "reflexivity": ["reflexivity_issues"],
    "transitivity": ["transitivity_issues"],
    "rewrite": ["rewrite_issues"],
    "weaken": ["weaken_issues"],
    "commute": ["commute_issues"],
    "excluded_middle": ["excluded_middle_issues"],
    "existential_gen": ["existential_gen_issues"],
    "instantiate": ["instantiate_issues"],
    "modus_ponens": ["modus_ponens_issues"],
    "conjunction": ["conjunction_issues"],
    "split_conjunct": ["split_conjunct_issues"],
    "double_negation": ["double_negation_issues"],
    "remove_double_negation": ["remove_double_negation_issues"],
    "copy": ["copy_issues"],
    "duplicate": ["duplicate_issues"],
    "rename_variable": ["rename_variable_issues"],
    "add_hypothesis": ["external_atp_issues"],
    "consequence": ["external_atp_issues"],
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="ProoVer2026/Extra")
    ap.add_argument("--out", default="results/extra")
    ap.add_argument("--timeout", type=float, default=60.0)
    args = ap.parse_args()

    base = (ROOT / args.dir).resolve()
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)

    expected = list(
        csv.reader(open(ROOT / "src" / "scoring" / "EXT_expected.csv", encoding="utf-8"))
    )
    rows = []
    for name, test, exp, comment in expected:
        proof = base / name
        problem = base / "Problems" / (proof.stem + ".p")
        kind, payload = verifier.check_proof_file_with_timeout(
            str(proof), str(problem), args.timeout
        )
        rule = (
            test.split("_", 1)[0] if test.split("_", 1)[0] in RULE_KEYS else test.rsplit("_", 1)[0]
        )
        # the rule name may itself contain underscores (excluded_middle, ...)
        for r in sorted(RULE_KEYS, key=len, reverse=True):
            if test.startswith(r + "_"):
                rule = r
                break
        if kind == "result":
            verdict = "VerifiedGood" if payload["all_ok"] else "VerifiedBad"
            issue_keys = [k for k, v in payload.items() if k.endswith("_issues") and v]
            rule_flagged = any(payload.get(k) for k in RULE_KEYS.get(rule, []))
            only_atp = issue_keys == ["external_atp_issues"]
        else:
            verdict = "Timeout" if kind == "timeout" else "Error"
            issue_keys, rule_flagged, only_atp = [], False, False
        if exp == "CORRECT":
            outcome = "ok" if verdict == "VerifiedGood" else "false_reject"
        elif exp == "INCORRECT":
            outcome = "ok" if verdict == "VerifiedBad" else "false_accept"
        else:
            outcome = "edge_" + verdict
        rows.append(
            dict(
                proof=name,
                rule=rule,
                test=test,
                expected=exp,
                verdict=verdict,
                outcome=outcome,
                rule_checker_flagged=rule_flagged,
                only_atp_flagged=only_atp,
                issues=";".join(issue_keys),
                comment=comment,
            )
        )
        print(f"{name:14s} {test:34s} exp={exp:9s} got={verdict:12s} {outcome}")

    with open(out / "results.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    per_rule: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in rows:
        per_rule[r["rule"]][r["outcome"]] += 1
        per_rule[r["rule"]]["n"] += 1
        if r["expected"] == "INCORRECT" and r["outcome"] == "ok":
            per_rule[r["rule"]]["rejected_by_rule_checker"] += int(r["rule_checker_flagged"])
    summary = {
        "total": len(rows),
        "false_accept": sum(r["outcome"] == "false_accept" for r in rows),
        "false_reject": sum(r["outcome"] == "false_reject" for r in rows),
        "per_rule": {k: dict(v) for k, v in sorted(per_rule.items())},
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
