#!/usr/bin/env python3
"""Experiment B: mutated Skolemization steps -- checker vs. entailment oracle (Vampire).

Idea
----
A Skolemization step  P  ==>  C  (status esa) is only *equisatisfiable*.
A prover such as Vampire can only answer entailment questions.  The only
entailment that holds for a correct step is  C |= P  (the Skolemized formula
implies the original one).  This is necessary but NOT sufficient.

For every skolemize step of the ProoVer 2026 reference proofs we create
mutants with known defects and compare two verdicts:
  * checker : src.checker.skolem_checker.check_skolemization (shape + dependencies)
  * oracle  : Vampire on  fof(c, axiom, C), fof(p, conjecture, P)
              "Theorem" -> the mutant looks fine, anything else -> defect found

Mutation kinds (ground truth in brackets)
  orig          unchanged step                                   [valid]
  drop_arg      remove one universal argument from the Skolem
                term (also in the conclusion)                    [INVALID: missing dependency]
  universal     "skolemize" a universally quantified variable    [INVALID: unsound]
  negate_atom   negate one atom of the conclusion                [INVALID: wrong formula]
  drop_conjunct replace a conjunction by one of its conjuncts    [INVALID: wrong formula]

Usage (project root, in WSL):
    python scripts/exp_skolem_mutants.py --vampire ~/vampire/vampire --per-kind 60
Output: results/skolem_mutants.csv, results/skolem_mutants_summary.json
"""

from __future__ import annotations

import argparse
import collections
import csv
import dataclasses
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.checker.alpha_eq import is_alpha_equivalent  # noqa: E402
from src.checker.external_atp_checker import formula_to_tptp  # noqa: E402
from src.checker.skolem_checker import check_skolemization  # noqa: E402
from src.parser.ast_nodes import (  # noqa: E402
    AnnotatedFormula,
    Atom,
    Constant,
    FunctionTerm,
    JunctionFormula,
    Negation,
    QuantifiedFormula,
    SkolemizeInfo,
    Variable,
)
from src.parser.parser import load_proof  # noqa: E402
from src.var_mapping import BinaryConnective, InferenceRule, Quantifier  # noqa: E402


# ----------------------------------------------------------------- AST helpers
def rebuild(node, fn):
    """Bottom-up rebuild of a dataclass tree, where fn may return a replacement or None."""
    if isinstance(node, list):
        return [rebuild(x, fn) for x in node]
    if dataclasses.is_dataclass(node) and not isinstance(node, type):
        changes = {f.name: rebuild(getattr(node, f.name), fn) for f in dataclasses.fields(node)}
        node = dataclasses.replace(node, **changes)
        out = fn(node)
        return node if out is None else out
    return node


def first_atom_path(node):
    """Return True if node contains an Atom (used to pick a mutation target)."""
    found = []

    def visit(n):
        if isinstance(n, Atom) and n.predicate:
            found.append(n)

    rebuild(node, lambda n: visit(n))
    return bool(found)


def skolem_functor(term):
    if isinstance(term, FunctionTerm):
        return term.functor
    if isinstance(term, Constant):
        return term.name
    return None


def replace_skolem_term(formula, functor, new_term_fn):
    def fn(n):
        if isinstance(n, FunctionTerm) and n.functor == functor:
            return new_term_fn(n)
        if isinstance(n, Constant) and n.name == functor:
            return new_term_fn(n)
        return None

    return rebuild(formula, fn)


def set_skolem_info(step, term):
    inf = step.inference
    info = [
        dataclasses.replace(i, term=term) if isinstance(i, SkolemizeInfo) else i for i in inf.info
    ]
    return dataclasses.replace(step, inference=dataclasses.replace(inf, info=info))


# ------------------------------------------------------------------- mutations
def _find_binder(node, var):
    """Return the QuantifiedFormula in `node` that binds `var` (first match)."""
    hit = []

    def fn(n):
        if isinstance(n, QuantifiedFormula) and var in [str(v) for v in n.variables] and not hit:
            hit.append(n)

    rebuild(node, lambda n: fn(n))
    return hit[0] if hit else None


def _occurs(node, name):
    seen = []

    def fn(n):
        if isinstance(n, Variable) and n.name == name:
            seen.append(1)

    rebuild(node, lambda n: fn(n))
    return bool(seen)


def m_drop_arg(step, parent):
    """Drop a Skolem argument that is semantically required (it occurs in the scope body)."""
    info = next((i for i in step.inference.info if isinstance(i, SkolemizeInfo)), None)
    if info is None or not isinstance(info.term, FunctionTerm) or not info.term.args:
        return None
    binder = _find_binder(parent.formula, info.variable)
    if binder is None:
        return None
    needed = [
        k
        for k, a in enumerate(info.term.args)
        if isinstance(a, Variable)
        and _occurs(binder.formula, a.name)
        and a.name not in [str(v) for v in binder.variables]
    ]
    if not needed:
        return None
    drop = needed[0]
    functor = info.term.functor
    new_args = [a for k, a in enumerate(info.term.args) if k != drop]

    def new_term(n):
        if isinstance(n, FunctionTerm):
            args = [a for k, a in enumerate(n.args) if k != drop]
            return FunctionTerm(functor, args) if args else Constant(functor)
        return n

    new_formula = replace_skolem_term(step.formula, functor, new_term)
    new_info_term = FunctionTerm(functor, new_args) if new_args else Constant(functor)
    return set_skolem_info(dataclasses.replace(step, formula=new_formula), new_info_term)


def m_negate_atom(step, parent):
    done = {"n": False}

    def fn(n):
        if isinstance(n, Atom) and not done["n"] and n.predicate not in ("$true", "$false"):
            done["n"] = True
            return Negation(n)
        return None

    # rebuild is bottom-up, so the first atom visited is the left-most one
    new_formula = rebuild(step.formula, fn)
    return dataclasses.replace(step, formula=new_formula) if done["n"] else None


def m_drop_conjunct(step, parent):
    done = {"n": False}

    def fn(n):
        if (
            isinstance(n, JunctionFormula)
            and n.connective == BinaryConnective.AND
            and len(n.operands) >= 2
            and not done["n"]
        ):
            done["n"] = True
            rest = n.operands[:-1]
            return rest[0] if len(rest) == 1 else JunctionFormula(n.connective, rest)
        return None

    new_formula = rebuild(step.formula, fn)
    return dataclasses.replace(step, formula=new_formula) if done["n"] else None


def m_universal(step, parent):
    """Eliminate the outermost universal variable by a fresh nullary Skolem constant."""
    f = parent.formula
    if not (isinstance(f, QuantifiedFormula) and f.quantifier == Quantifier.UNIVERSAL):
        return None
    var = f.variables[0]
    sk = "sKmut"
    rest_vars = f.variables[1:]
    body = f.formula

    def fn(n):
        if isinstance(n, Variable) and n.name == var:
            return Constant(sk)
        return None

    body = rebuild(body, fn)
    new_formula = QuantifiedFormula(f.quantifier, rest_vars, body) if rest_vars else body
    inf = step.inference
    info = []
    for i in inf.info:
        if isinstance(i, SkolemizeInfo):
            info.append(SkolemizeInfo(var, Constant(sk)))
        elif i.__class__.__name__ == "NewSymbolsInfo":
            info.append(dataclasses.replace(i, symbols=[sk]))
        else:
            info.append(i)
    return dataclasses.replace(
        step, formula=new_formula, inference=dataclasses.replace(inf, info=info)
    )


MUTATIONS = {
    "drop_arg": ("invalid", m_drop_arg),
    "universal": ("invalid", m_universal),
    "negate_atom": ("invalid", m_negate_atom),
    "drop_conjunct": ("invalid", m_drop_conjunct),
}


# ---------------------------------------------------------------------- oracle
def vampire_entails(vampire: str, conclusion, premise, timeout: int) -> str:
    """Return SZS status of  C |= P  (Theorem means 'looks fine')."""
    text = (
        f"fof(c, axiom, {formula_to_tptp(conclusion)}).\n"
        f"fof(p, conjecture, {formula_to_tptp(premise)}).\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".p", delete=False) as fh:
        fh.write(text)
        path = fh.name
    try:
        out = subprocess.run(
            [vampire, "--mode", "casc", "-t", str(timeout), path],
            capture_output=True,
            text=True,
            timeout=timeout + 10,
        ).stdout
    except subprocess.TimeoutExpired:
        return "Timeout"
    finally:
        Path(path).unlink(missing_ok=True)
    for line in out.splitlines():
        if line.startswith("% SZS status"):
            return line.split()[3]
    return "NoStatus"


# ------------------------------------------------------------------------ main
def collect_steps():
    items = []
    for p in sorted(
        q for d in ("PRV", "Deprecated", "Test") for q in (ROOT / "ProoVer2026" / d).glob("*.s")
    ):
        try:
            proof = load_proof(str(p))
        except Exception as exc:  # noqa: BLE001
            print(f"  skip {p.name}: {type(exc).__name__}")
            continue
        idx = {s.name: s for s in proof.steps if isinstance(s, AnnotatedFormula)}
        for s in idx.values():
            inf = s.inference
            if inf and inf.rule == InferenceRule.SKOLEMIZE and len(inf.parents) == 1:
                parent = idx.get(inf.parents[0])
                if parent is not None:
                    items.append((p.stem, s, parent))
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vampire", default=None, help="path to vampire (omit: checker only)")
    ap.add_argument("--per-kind", type=int, default=1000)
    ap.add_argument(
        "--max-per-proof",
        type=int,
        default=10,
        help="cap per proof and kind (PRV072 alone has ~5000 Skolem steps)",
    )
    ap.add_argument("--timeout", type=int, default=10)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()

    random.seed(args.seed)
    all_items = collect_steps()
    items = [t for t in all_items if not check_skolemization(t[1], t[2])]
    rejected_orig = sorted({t[0] for t in all_items if check_skolemization(t[1], t[2])})
    print(
        f"skolemize steps in reference proofs: {len(all_items)}; "
        f"accepted by checker: {len(items)}; rejected: {len(all_items) - len(items)} "
        f"(in proofs: {', '.join(rejected_orig)})"
    )
    random.shuffle(items)

    rows = []
    expected = {}
    for res_name in ("PRV_results.csv", "Deprecated_results.csv", "Test_results.csv"):
        res_csv = ROOT / "results" / res_name
        if res_csv.exists():
            with open(res_csv, newline="") as fh:
                for r in csv.DictReader(fh):
                    expected[Path(r["Proof"]).stem] = r["Expected"]
    bad_items = [t for t in all_items if check_skolemization(t[1], t[2])]
    kinds = {
        "orig": ("valid", lambda s, p: s),
        **MUTATIONS,
        "reference_rejected": ("invalid(?)", lambda s, p: s),
    }
    for kind, (truth, fn) in kinds.items():
        n = 0
        per_proof = collections.Counter()
        for proof, step, parent in (bad_items if kind == "reference_rejected" else items):
            if n >= args.per_kind and kind != "reference_rejected":
                break
            try:
                mutant = fn(step, parent)
            except Exception:  # noqa: BLE001
                mutant = None
            if mutant is None:
                continue
            if kind != "reference_rejected" and per_proof[proof] >= args.max_per_proof:
                continue
            if kind not in ("orig", "reference_rejected") and is_alpha_equivalent(
                mutant.formula, step.formula
            ):
                continue  # mutation had no effect
            n += 1
            per_proof[proof] += 1
            issues = check_skolemization(mutant, parent)
            checker = "reject" if issues else "accept"
            reason = issues[0].reason[:70] if issues else ""
            oracle = ""
            if args.vampire:
                st = vampire_entails(args.vampire, mutant.formula, parent.formula, args.timeout)
                oracle = (
                    "accept"
                    if st == "Theorem"
                    else ("reject" if st == "CounterSatisfiable" else st)
                )
            rows.append(
                dict(
                    kind=kind,
                    truth=truth,
                    proof=proof,
                    step=step.name,
                    expected_proof=expected.get(proof, ""),
                    checker=checker,
                    oracle=oracle,
                    checker_reason=reason,
                )
            )
        print(f"{kind}: {n} mutants")

    out = ROOT / "results"
    with open(out / "skolem_mutants.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    summ = {}
    for kind in kinds:
        r = [x for x in rows if x["kind"] == kind]
        summ[kind] = dict(
            n=len(r),
            checker=dict(collections.Counter(x["checker"] for x in r)),
            oracle=dict(collections.Counter(x["oracle"] for x in r)) if args.vampire else None,
        )
    summ["_reference_steps"] = dict(
        total=len(all_items), accepted=len(items), proofs_with_rejected_steps=rejected_orig
    )
    (out / "skolem_mutants_summary.json").write_text(json.dumps(summ, indent=2))
    print(json.dumps(summ, indent=2))


if __name__ == "__main__":
    main()
