#!/usr/bin/env python3
"""Generate extra ProoVer-style test cases for the inference rules that the
TST group does not cover (resolution, paramodulation, rewrite, transitivity,
reflexivity, weaken, commute, excluded_middle, existential_gen, instantiate,
modus_ponens, conjunction, split_conjunct, double_negation,
remove_double_negation, copy, duplicate, rename_variable, add_hypothesis).

For every rule there is one CORRECT base proof and several mutants whose
defect is known by construction (unsound conclusion, parents that do not fit,
status 'cth' on a non-negated-conjecture step, missing parent). A few EDGE
cases are sound but unusual (e.g. swapped operand order); they are listed
separately because the expected verdict depends on how strict the rules are.

Output (default: ProoVer2026/Extra):
    EXTnnn+1.s              proof file
    Problems/EXTnnn+1.p     problem file
    EXT_expected.csv        name,test,expected,comment   (same layout as TST_expected.csv)

Usage:  python scripts/gen_extra_tests.py [--out ProoVer2026/Extra]
"""

from __future__ import annotations

import argparse
import copy
import csv
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Step:
    name: str
    formula: str
    rule: str
    status: str = "thm"
    parents: list[str] = field(default_factory=list)


@dataclass
class Base:
    rule: str
    axioms: dict[str, str]
    conj: str
    steps: list[Step]  # derived steps; the last one is the step that proves the conjecture
    bot_parents: list[str] | None = None  # default: [negc, last step]


@dataclass
class Case:
    rule: str
    tag: str
    expected: str  # CORRECT | INCORRECT | EDGE
    comment: str
    base: Base


CASES: list[Case] = []


def add(base: Base, tag: str, expected: str, comment: str) -> None:
    CASES.append(Case(base.rule, tag, expected, comment, copy.deepcopy(base)))


def variant(
    base: Base,
    tag: str,
    expected: str,
    comment: str,
    *,
    axioms: dict[str, str] | None = None,
    conj: str | None = None,
    formula: str | None = None,
    status: str | None = None,
    parents: list[str] | None = None,
    rule: str | None = None,
    bot_parents: list[str] | None = None,
) -> None:
    """Copy `base` and change the last derived step (and optionally the problem)."""
    b = copy.deepcopy(base)
    if axioms:
        b.axioms.update(axioms)
    if conj is not None:
        b.conj = conj
    last = b.steps[-1]
    if formula is not None:
        last.formula = formula
        if conj is None:
            # make the final $false step valid so that only the rule step carries the defect
            b.conj = formula
    if status is not None:
        last.status = status
    if parents is not None:
        last.parents = parents
    if rule is not None:
        last.rule = rule
    if bot_parents is not None:
        b.bot_parents = bot_parents
    CASES.append(Case(base.rule, tag, expected, comment, b))


def standard(rule, axioms, conj, concl, parents, status="thm"):
    return Base(rule, axioms, conj, [Step("s", concl, rule, status, parents)])


# --------------------------------------------------------------------------
# resolution
# --------------------------------------------------------------------------
b = standard(
    "resolution",
    {"a1": "![X]: (p(X) | q(X))", "a2": "![X]: (~p(X) | r(X))", "a3": "![X]: (u(X) | r(X))"},
    "![X]: (q(X) | r(X))",
    "![X]: (q(X) | r(X))",
    ["a1", "a2"],
)
add(b, "base", "CORRECT", "Binary resolution on p(X)")
variant(
    b,
    "wrong_conclusion_and",
    "INCORRECT",
    "Resolvent is a conjunction q & r (unsound)",
    formula="![X]: (q(X) & r(X))",
)
variant(
    b,
    "dropped_literal",
    "INCORRECT",
    "Literal r(X) dropped from the resolvent (unsound)",
    formula="![X]: q(X)",
)
variant(
    b,
    "not_complementary",
    "INCORRECT",
    "Parents have no complementary literals",
    parents=["a1", "a3"],
)
variant(b, "status_cth", "INCORRECT", "cth is reserved for the negated conjecture", status="cth")
variant(b, "missing_parent", "INCORRECT", "Second parent does not exist", parents=["a1", "zz"])
b = standard(
    "resolution",
    {"a1": "p(a) | q(a)", "a2": "~p(a) | r(a)"},
    "q(a) | r(a)",
    "q(a) | r(a)",
    ["a1", "a2"],
)
add(b, "ground", "CORRECT", "Ground resolution")
variant(
    b,
    "ground_wrong_atom",
    "INCORRECT",
    "Resolvent mentions an atom (s) that occurs in no parent",
    formula="q(a) | s(a)",
)
variant(
    b,
    "swapped_literal_order",
    "EDGE",
    "Sound resolvent with the literals in the other order; a strict syntactic matcher may reject it",
    formula="r(a) | q(a)",
)

# --------------------------------------------------------------------------
# paramodulation
# --------------------------------------------------------------------------
b = standard(
    "paramodulation",
    {"a1": "p(f(a))", "a2": "![X]: f(X) = g(X)", "a3": "![X]: f(X) = h(X)"},
    "p(g(a))",
    "p(g(a))",
    ["a1", "a2"],
)
add(
    b,
    "base",
    "CORRECT",
    "Rewrite f(a) to g(a) with an instance of a universally quantified equation",
)
variant(b, "wrong_instance", "INCORRECT", "Rewritten to g(b) instead of g(a)", formula="p(g(b))")
variant(
    b,
    "wrong_symbol",
    "INCORRECT",
    "Rewritten to h(a), which the equation does not give",
    formula="p(h(a))",
)
variant(
    b,
    "wrong_predicate",
    "INCORRECT",
    "Predicate changed from p to q during rewriting",
    formula="q(g(a))",
)
variant(
    b,
    "wrong_equation",
    "INCORRECT",
    "Equation used is f(X)=h(X) but the conclusion contains g(a)",
    parents=["a1", "a3"],
)
variant(
    b,
    "same_parent_twice",
    "INCORRECT",
    "Both parents are the atom p(f(a)); no equation available",
    parents=["a1", "a1"],
)
variant(b, "status_cth", "INCORRECT", "cth is reserved for the negated conjecture", status="cth")
b = standard(
    "paramodulation",
    {"a1": "![Y]: p(f(Y))", "a2": "![X]: f(X) = c"},
    "![Y]: p(c)",
    "![Y]: p(c)",
    ["a1", "a2"],
)
add(b, "under_quantifier", "CORRECT", "Rewrite below a universal quantifier")
variant(
    b,
    "under_quantifier_wrong",
    "INCORRECT",
    "Rewrite below a universal quantifier produces f(c)",
    formula="![Y]: p(f(c))",
)
b = standard(
    "paramodulation",
    {"a1": "p(f(a), f(a))", "a2": "![X]: f(X) = g(X)"},
    "p(g(a), f(a))",
    "p(g(a), f(a))",
    ["a1", "a2"],
)
add(b, "one_occurrence", "CORRECT", "Rewrite exactly one of two occurrences")
variant(
    b,
    "one_occurrence_wrong",
    "INCORRECT",
    "Second argument rewritten to the unrelated term g(b)",
    formula="p(g(a), g(b))",
)

# --------------------------------------------------------------------------
# reflexivity
# --------------------------------------------------------------------------
b = standard("reflexivity", {"a1": "p(a)"}, "f(a) = f(a)", "f(a) = f(a)", ["a1"])
add(b, "base", "CORRECT", "t = t")
variant(
    b,
    "not_reflexive",
    "INCORRECT",
    "Conclusion f(a) = f(b) is not reflexive",
    formula="f(a) = f(b)",
    conj="f(a) = f(b)",
)
variant(
    b,
    "negated_equality",
    "INCORRECT",
    "Conclusion f(a) != f(a) is false",
    formula="f(a) != f(a)",
    conj="f(a) != f(a)",
)
variant(
    b,
    "not_an_equation",
    "INCORRECT",
    "Conclusion is p(a), not an equation",
    formula="p(a)",
    conj="p(a)",
)
variant(b, "status_cth", "INCORRECT", "cth is reserved for the negated conjecture", status="cth")

# --------------------------------------------------------------------------
# transitivity
# --------------------------------------------------------------------------
b = standard(
    "transitivity",
    {"a1": "a = b", "a2": "b = c", "a3": "d = e"},
    "a = c",
    "a = c",
    ["a1", "a2"],
)
add(b, "base", "CORRECT", "a=b, b=c |- a=c")
variant(
    b,
    "fresh_constant",
    "INCORRECT",
    "Conclusion c = d relates a constant that is not chained",
    formula="c = d",
    conj="c = d",
)
variant(
    b,
    "no_common_term",
    "INCORRECT",
    "Parents a=b and d=e share no term",
    parents=["a1", "a3"],
    formula="a = e",
    conj="a = e",
)
variant(
    b,
    "negated_parent",
    "INCORRECT",
    "Second parent is the disequation b != c",
    axioms={"a2": "b != c"},
)
variant(b, "status_cth", "INCORRECT", "cth is reserved for the negated conjecture", status="cth")

# --------------------------------------------------------------------------
# rewrite (single parent, implicit equation)
# --------------------------------------------------------------------------
b = standard("rewrite", {"a1": "p(a)", "a2": "a = b"}, "p(a)", "p(a)", ["a1"])
add(
    b,
    "identity",
    "CORRECT",
    "Rewrite step whose conclusion is its parent (the only form seen in the corpus)",
)
variant(
    b,
    "unjustified_rewrite",
    "INCORRECT",
    "p(a) rewritten to p(b) although the equation a=b is not cited as a parent",
    formula="p(b)",
    conj="p(b)",
)
variant(
    b,
    "unrelated_conclusion",
    "INCORRECT",
    "Conclusion q(a) does not follow from the parent",
    formula="q(a)",
    conj="q(a)",
)

# --------------------------------------------------------------------------
# weaken
# --------------------------------------------------------------------------
b = standard("weaken", {"a1": "p(a)"}, "p(a) | q(a)", "p(a) | q(a)", ["a1"])
add(b, "base", "CORRECT", "p(a) |- p(a) | q(a)")
variant(
    b,
    "not_a_disjunction",
    "INCORRECT",
    "Conclusion p(a) & q(a) is stronger than the parent",
    formula="p(a) & q(a)",
    conj="p(a) & q(a)",
)
variant(
    b,
    "parent_missing",
    "INCORRECT",
    "Disjunction q(a) | r(a) does not contain the parent",
    formula="q(a) | r(a)",
    conj="q(a) | r(a)",
)
variant(
    b,
    "plain_atom",
    "INCORRECT",
    "Conclusion q(a) is unrelated to the parent",
    formula="q(a)",
    conj="q(a)",
)
variant(
    b,
    "new_disjunct_first",
    "EDGE",
    "Sound weakening with the new disjunct in front; a strict prefix check may reject it",
    formula="q(a) | p(a)",
    conj="q(a) | p(a)",
)

# --------------------------------------------------------------------------
# commute
# --------------------------------------------------------------------------
b = standard("commute", {"a1": "p(a) & q(a)"}, "q(a) & p(a)", "q(a) & p(a)", ["a1"])
add(b, "conjunction", "CORRECT", "Swap of the operands of a conjunction")
variant(
    b,
    "conjunction_new_operand",
    "INCORRECT",
    "Swap with an unrelated operand r(a)",
    formula="q(a) & r(a)",
    conj="q(a) & r(a)",
)
variant(
    b,
    "conjunction_three_operands",
    "INCORRECT",
    "Extra operand added while swapping",
    formula="q(a) & p(a) & r(a)",
    conj="q(a) & p(a) & r(a)",
)
b = standard("commute", {"a1": "p(a) | q(a)"}, "q(a) | p(a)", "q(a) | p(a)", ["a1"])
add(b, "disjunction", "CORRECT", "Swap of the operands of a disjunction")
variant(
    b,
    "disjunction_new_operand",
    "INCORRECT",
    "Swap with an unrelated operand r(a)",
    formula="q(a) | r(a)",
    conj="q(a) | r(a)",
)

# --------------------------------------------------------------------------
# excluded_middle
# --------------------------------------------------------------------------
b = standard("excluded_middle", {"a1": "p(a)"}, "q(a) | ~q(a)", "q(a) | ~q(a)", ["a1"])
add(b, "base", "CORRECT", "phi | ~phi")
variant(
    b,
    "different_atoms",
    "INCORRECT",
    "q(a) | ~r(a) is not a tautology",
    formula="q(a) | ~r(a)",
    conj="q(a) | ~r(a)",
)
variant(
    b,
    "no_negation",
    "INCORRECT",
    "q(a) | q(a) is not a tautology",
    formula="q(a) | q(a)",
    conj="q(a) | q(a)",
)
variant(
    b,
    "contradiction",
    "INCORRECT",
    "q(a) & ~q(a) is a contradiction",
    formula="q(a) & ~q(a)",
    conj="q(a) & ~q(a)",
)
variant(b, "status_cth", "INCORRECT", "cth is reserved for the negated conjecture", status="cth")

# --------------------------------------------------------------------------
# existential_gen
# --------------------------------------------------------------------------
b = standard("existential_gen", {"a1": "p(a)"}, "?[X]: p(X)", "?[X]: p(X)", ["a1"])
add(b, "base", "CORRECT", "p(a) |- ?X p(X)")
variant(
    b,
    "other_predicate",
    "INCORRECT",
    "?X q(X) does not follow from p(a)",
    formula="?[X]: q(X)",
    conj="?[X]: q(X)",
)
variant(
    b,
    "universal_instead",
    "INCORRECT",
    "Universal generalization !X p(X) is unsound",
    formula="![X]: p(X)",
    conj="![X]: p(X)",
)
variant(
    b,
    "no_quantifier",
    "INCORRECT",
    "No existential quantifier introduced; the term is replaced by b",
    formula="p(b)",
    conj="p(b)",
)
b = standard("existential_gen", {"a1": "r(a, b)"}, "?[X,Y]: r(X,Y)", "?[X,Y]: r(X,Y)", ["a1"])
add(b, "two_variables", "CORRECT", "r(a,b) |- ?X,Y r(X,Y)")
variant(
    b,
    "diagonal",
    "INCORRECT",
    "?X r(X,X) would need a = b",
    formula="?[X]: r(X,X)",
    conj="?[X]: r(X,X)",
)

# --------------------------------------------------------------------------
# instantiate
# --------------------------------------------------------------------------
b = standard("instantiate", {"a1": "![X]: p(X)"}, "p(a)", "p(a)", ["a1"])
add(b, "base", "CORRECT", "!X p(X) |- p(a)")
variant(
    b,
    "wrong_predicate",
    "INCORRECT",
    "q(a) does not follow from !X p(X)",
    formula="q(a)",
    conj="q(a)",
)
b = standard("instantiate", {"a1": "![X,Y]: r(X,Y)"}, "![Y]: r(a,Y)", "![Y]: r(a,Y)", ["a1"])
add(b, "partial", "CORRECT", "Instantiate one of two universal variables")
b = standard("instantiate", {"a1": "![X]: r(X,X)"}, "r(a,a)", "r(a,a)", ["a1"])
add(b, "same_variable", "CORRECT", "Both occurrences get the same instance")
variant(
    b,
    "inconsistent_instance",
    "INCORRECT",
    "Occurrences of X replaced by different terms",
    formula="r(a,b)",
    conj="r(a,b)",
)
b = standard("instantiate", {"a1": "p(a)"}, "![X]: p(X)", "![X]: p(X)", ["a1"])
add(b, "generalisation", "INCORRECT", "Direction reversed: p(a) does not give !X p(X)")

# --------------------------------------------------------------------------
# modus_ponens
# --------------------------------------------------------------------------
b = standard(
    "modus_ponens", {"a1": "p(a) => q(a)", "a2": "p(a)", "a3": "q(a)"}, "q(a)", "q(a)", ["a1", "a2"]
)
add(b, "base", "CORRECT", "p => q, p |- q")
variant(
    b,
    "affirming_consequent",
    "INCORRECT",
    "p => q, q |- p is unsound",
    parents=["a1", "a3"],
    formula="p(a)",
    conj="p(a)",
)
variant(b, "wrong_conclusion", "INCORRECT", "r(a) does not follow", formula="r(a)", conj="r(a)")
variant(b, "status_cth", "INCORRECT", "cth is reserved for the negated conjecture", status="cth")
b = standard(
    "modus_ponens", {"a1": "![X]: (p(X) => q(X))", "a2": "p(a)"}, "q(a)", "q(a)", ["a1", "a2"]
)
add(b, "universal", "CORRECT", "Universally quantified implication instantiated by the premise")
variant(
    b,
    "universal_wrong_instance",
    "INCORRECT",
    "q(b) does not follow from p(a)",
    formula="q(b)",
    conj="q(b)",
)

# --------------------------------------------------------------------------
# conjunction / split_conjunct
# --------------------------------------------------------------------------
b = standard(
    "conjunction", {"a1": "p(a)", "a2": "q(a)"}, "p(a) & q(a)", "p(a) & q(a)", ["a1", "a2"]
)
add(b, "base", "CORRECT", "p, q |- p & q")
variant(
    b,
    "unsupported_operand",
    "INCORRECT",
    "r(a) is not among the parents",
    formula="p(a) & r(a)",
    conj="p(a) & r(a)",
)
variant(
    b,
    "single_parent_repeated",
    "INCORRECT",
    "q(a) is not derivable from the single parent p(a)",
    parents=["a1", "a1"],
)
variant(
    b,
    "swapped_order",
    "EDGE",
    "Sound conclusion q & p with the operands in the other order; strict operand order may reject it",
    formula="q(a) & p(a)",
    conj="q(a) & p(a)",
)
b = standard("split_conjunct", {"a1": "p(a) & q(a)", "a2": "p(a) | q(a)"}, "q(a)", "q(a)", ["a1"])
add(b, "base", "CORRECT", "p & q |- q")
variant(
    b,
    "not_a_conjunct",
    "INCORRECT",
    "r(a) is not a conjunct of the parent",
    formula="r(a)",
    conj="r(a)",
)
variant(
    b,
    "parent_is_disjunction",
    "INCORRECT",
    "Parent is p | q, from which q does not follow",
    parents=["a2"],
)

# --------------------------------------------------------------------------
# double_negation / remove_double_negation
# --------------------------------------------------------------------------
b = standard("double_negation", {"a1": "p(a)"}, "~~p(a)", "~~p(a)", ["a1"])
add(b, "base", "CORRECT", "p |- ~~p")
variant(
    b,
    "single_negation",
    "INCORRECT",
    "~p(a) is the negation, not a double negation",
    formula="~p(a)",
    conj="~p(a)",
)
variant(
    b,
    "wrong_atom",
    "INCORRECT",
    "~~q(a) does not follow from p(a)",
    formula="~~q(a)",
    conj="~~q(a)",
)
b = standard("remove_double_negation", {"a1": "~~p(a)", "a2": "~p(a)"}, "p(a)", "p(a)", ["a1"])
add(b, "base", "CORRECT", "~~p |- p")
variant(
    b,
    "single_negation_parent",
    "INCORRECT",
    "Parent ~p(a) is not a double negation",
    parents=["a2"],
)
variant(
    b, "wrong_atom", "INCORRECT", "q(a) does not follow from ~~p(a)", formula="q(a)", conj="q(a)"
)

# --------------------------------------------------------------------------
# copy / duplicate / rename_variable
# --------------------------------------------------------------------------
b = standard("copy", {"a1": "p(a)"}, "p(a)", "p(a)", ["a1"])
add(b, "base", "CORRECT", "Copy of an axiom")
variant(b, "changed_formula", "INCORRECT", "Copy changes p(a) to q(a)", formula="q(a)", conj="q(a)")
variant(b, "negated_copy", "INCORRECT", "Copy changes p(a) to ~p(a)", formula="~p(a)", conj="~p(a)")
b = standard("duplicate", {"a1": "p(a)", "a2": "q(a)"}, "p(a)", "p(a)", ["a1", "a1"])
add(b, "base", "CORRECT", "Duplicate of the same premise")
variant(b, "different_parents", "INCORRECT", "Parents p(a) and q(a) differ", parents=["a1", "a2"])
variant(
    b,
    "changed_formula",
    "INCORRECT",
    "Conclusion q(a) differs from the duplicated formula",
    formula="q(a)",
    conj="q(a)",
)
b = standard(
    "rename_variable",
    {"a1": "![X]: ?[Y]: r(X,Y)"},
    "![U]: ?[V]: r(U,V)",
    "![U]: ?[V]: r(U,V)",
    ["a1"],
)
add(b, "base", "CORRECT", "Consistent renaming of bound variables")
variant(
    b,
    "swapped_arguments",
    "INCORRECT",
    "Renaming also swaps the arguments",
    formula="![U]: ?[V]: r(V,U)",
    conj="![U]: ?[V]: r(V,U)",
)
variant(
    b,
    "variable_capture",
    "INCORRECT",
    "Both variables renamed to the same name (capture)",
    formula="![Y]: ?[Y]: r(Y,Y)",
    conj="![Y]: ?[Y]: r(Y,Y)",
)

# --------------------------------------------------------------------------
# add_hypothesis
# --------------------------------------------------------------------------
b = standard("add_hypothesis", {"a1": "p(a)"}, "q(a) => p(a)", "q(a) => p(a)", ["a1"])
add(b, "base", "CORRECT", "p |- q => p")
variant(
    b,
    "wrong_consequent",
    "INCORRECT",
    "q => r does not follow from p",
    formula="q(a) => r(a)",
    conj="q(a) => r(a)",
)


# --------------------------------------------------------------------------
# harder cases: unification, variable clashes, capture, scoping
# --------------------------------------------------------------------------
b = standard(
    "resolution",
    {"a1": "![X]: (p(X) | q(X))", "a2": "~p(a) | r(a)"},
    "q(a) | r(a)",
    "q(a) | r(a)",
    ["a1", "a2"],
)
add(b, "needs_unifier", "CORRECT", "Resolution needs the unifier X := a")
variant(
    b,
    "wrong_unifier",
    "INCORRECT",
    "Resolvent uses X := b instead of the unifier X := a",
    formula="q(b) | r(a)",
)
b = standard(
    "resolution",
    {"a1": "![X]: (p(X, c) | q(X))", "a2": "![X]: (~p(a, X) | r(X))"},
    "q(a) | r(c)",
    "q(a) | r(c)",
    ["a1", "a2"],
)
add(
    b,
    "variables_standardised_apart",
    "CORRECT",
    "Both parents use X; the unifier is X1 := a, X2 := c",
)
variant(
    b,
    "variables_conflated",
    "INCORRECT",
    "Resolvent identifies the two variables X (q(a) | r(a))",
    formula="q(a) | r(a)",
)
b = standard(
    "resolution",
    {"a1": "![X]: (p(X, X) | q(X))", "a2": "![Y]: (~p(Y, f(Y)) | r(Y))"},
    "![X]: (q(X) | r(X))",
    "![X]: (q(X) | r(X))",
    ["a1", "a2"],
)
add(b, "occurs_check", "INCORRECT", "p(X,X) and p(Y,f(Y)) are not unifiable (occurs check)")

b = standard(
    "paramodulation",
    {"a1": "p(g(a))", "a2": "![X]: f(X) = g(X)"},
    "p(f(a))",
    "p(f(a))",
    ["a1", "a2"],
)
add(b, "reverse_orientation", "CORRECT", "Equation used right to left")
b = standard(
    "paramodulation",
    {"a1": "p(f(a), f(a))", "a2": "![X]: f(X) = g(X)"},
    "p(g(a), g(a))",
    "p(g(a), g(a))",
    ["a1", "a2"],
)
add(
    b,
    "rewrites_all_occurrences",
    "EDGE",
    "Sound, but two rewrite steps in one inference; a one-position check rejects it",
)
b = standard(
    "paramodulation",
    {"a1": "![X]: p(f(X))", "a2": "f(a) = c"},
    "p(c)",
    "p(c)",
    ["a1", "a2"],
)
add(
    b,
    "target_needs_instantiation",
    "EDGE",
    "Sound (superposition unifies X := a in the target), but the target variable is not instantiated by a one-sided matcher",
)

b = standard("instantiate", {"a1": "![X]: ?[Y]: r(X,Y)"}, "?[Y]: r(a,Y)", "?[Y]: r(a,Y)", ["a1"])
add(b, "under_existential", "CORRECT", "Instantiate X := a below the universal prefix")
variant(
    b,
    "variable_capture",
    "INCORRECT",
    "Instantiating X := Y would be captured by ?[Y]",
    formula="?[Y]: r(Y,Y)",
)

b = standard(
    "modus_ponens", {"a1": "![X]: (p(X) => q(X,X))", "a2": "p(a)"}, "q(a,a)", "q(a,a)", ["a1", "a2"]
)
add(b, "repeated_variable", "CORRECT", "Both occurrences of X receive the same instance")
variant(
    b,
    "inconsistent_instance",
    "INCORRECT",
    "q(a,b) uses different instances for the two occurrences of X",
    formula="q(a,b)",
)

b = standard("split_conjunct", {"a1": "![X]: (p(X) & q(X))"}, "![X]: q(X)", "![X]: q(X)", ["a1"])
add(
    b,
    "below_quantifier",
    "EDGE",
    "Sound, but the parent is a quantified conjunction, not a conjunction at top level",
)
b = standard(
    "excluded_middle", {"a1": "p(a)"}, "![X]: (q(X) | ~q(X))", "![X]: (q(X) | ~q(X))", ["a1"]
)
add(
    b,
    "quantified",
    "EDGE",
    "Sound tautology below a universal quantifier; the rule's shape check expects a top-level disjunction",
)
b = standard("reflexivity", {"a1": "p(a)"}, "![X]: X = X", "![X]: X = X", ["a1"])
add(b, "quantified", "EDGE", "Sound, but the conclusion is a quantified equation, not t = t")
b = standard("transitivity", {"a1": "a = b", "a2": "c = b"}, "a = c", "a = c", ["a1", "a2"])
add(b, "shared_right_term", "CORRECT", "a=b, c=b |- a=c (common term on the right)")
b = standard("weaken", {"a1": "p(a)"}, "p(a) | q(a) | r(a)", "p(a) | q(a) | r(a)", ["a1"])
add(b, "two_new_disjuncts", "CORRECT", "Two disjuncts added at once")
b = standard(
    "commute",
    {"a1": "(p(a) | q(a)) & r(a)"},
    "r(a) & (p(a) | q(a))",
    "r(a) & (p(a) | q(a))",
    ["a1"],
)
add(b, "nested_operand", "CORRECT", "Swap with a compound operand")


# --------------------------------------------------------------------------
# bot step / dependency structure
# --------------------------------------------------------------------------
b = standard("modus_ponens", {"a1": "p(a) => q(a)", "a2": "p(a)"}, "q(a)", "q(a)", ["a1", "a2"])
b.steps.append(Step("t", "r(a)", "modus_ponens", "thm", ["a1", "a2"]))
CASES.append(
    Case(
        "consequence",
        "bot_unrelated",
        "INCORRECT",
        "Final $false uses an unrelated derived step (r(a)) instead of the proof of the conjecture",
        copy.deepcopy(b),
    )
)
CASES[-1].base.bot_parents = ["negc", "t"]


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------
def render(case: Case, ident: str) -> tuple[str, str]:
    b = case.base
    prob_lines = [
        "%------------------------------------------------------------------------------",
        f"% File     : {ident}.p : extra test ({case.rule}/{case.tag})",
        "%------------------------------------------------------------------------------",
    ]
    for name, f in b.axioms.items():
        prob_lines.append(f"fof({name}, axiom, {f}).")
    prob_lines.append(f"fof(c, conjecture, {b.conj}).")
    prob_lines.append("")

    ref = f"file('Problems/{ident}.p',"
    proof = [
        "%------------------------------------------------------------------------------",
        f"% File     : {ident}.s : ProoVer 2026 (extra test)",
        f"% Proof    : Problems/{ident}.p",
        f"% Test     : {case.rule}/{case.tag} - {case.comment}",
        f"% Expected : {case.expected}",
        "%------------------------------------------------------------------------------",
        "% SZS output start Proof",
    ]
    for name, f in b.axioms.items():
        proof.append(f"fof({name}, axiom, {f}, {ref}{name})).\n")
    proof.append(f"fof(c, conjecture, {b.conj}, {ref}c)).\n")
    proof.append(
        "fof(negc, negated_conjecture, ~("
        + b.conj
        + "), inference(negated_conjecture, [status(cth)], [c])).\n"
    )
    for st in b.steps:
        parents = ", ".join(st.parents)
        proof.append(
            f"fof({st.name}, plain, {st.formula}, inference({st.rule}, [status({st.status})], [{parents}])).\n"
        )
    bot_parents = b.bot_parents or ["negc", b.steps[-1].name]
    proof.append(
        f"fof(bot, plain, $false, inference(consequence, [status(thm)], [{', '.join(bot_parents)}])).\n"
    )
    proof.append("% SZS output end Proof")
    return "\n".join(prob_lines) + "\n", "\n".join(proof) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="ProoVer2026/Extra")
    args = ap.parse_args()
    out = Path(args.out)
    (out / "Problems").mkdir(parents=True, exist_ok=True)

    rows = []
    for i, case in enumerate(CASES, start=1):
        ident = f"EXT{i:03d}+1"
        problem, proof = render(case, ident)
        (out / "Problems" / f"{ident}.p").write_text(problem, encoding="utf-8", newline="\n")
        (out / f"{ident}.s").write_text(proof, encoding="utf-8", newline="\n")
        rows.append([f"{ident}.s", f"{case.rule}_{case.tag}", case.expected, case.comment])

    with open(out / "EXT_expected.csv", "w", encoding="utf-8", newline="") as fh:
        csv.writer(fh).writerows(rows)

    kinds = {}
    for c in CASES:
        kinds[c.expected] = kinds.get(c.expected, 0) + 1
    print(f"wrote {len(CASES)} cases to {out}: {kinds}")


if __name__ == "__main__":
    main()
