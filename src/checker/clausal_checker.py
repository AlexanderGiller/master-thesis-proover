"""Check clausal/equality inference steps: resolution, paramodulation,
reflexivity, transitivity, and rewrite.

These rules operate over disjunctive clauses and equations rather than the
simple structural transformations handled by ``propositional_checker`` and
``structural_checker``, so they need term unification and subterm rewriting
helpers of their own.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations

from src.checker.alpha_eq import is_alpha_equivalent
from src.checker.formula_utils import flatten_prefix, match_template_to_instance, substitute_node
from src.parser.ast_nodes import (
    AnnotatedFormula,
    Atom,
    BinaryFormula,
    Constant,
    Equality,
    FunctionTerm,
    JunctionFormula,
    Negation,
    QuantifiedFormula,
    Variable,
)
from src.var_mapping import BinaryConnective, InferenceRule, InferenceStatus, Quantifier

_FALSE_ATOM = Atom(predicate="$false", args=[])

# Guard against combinatorial blow-up when trying to match leftover quantifier
# variables against the stated conclusion in a different order.
_MAX_PERMUTATION_VARS = 6


@dataclass
class ClausalIssue:
    step_name: str
    reason: str


def _check_inference_metadata(step: AnnotatedFormula, rule: InferenceRule) -> list[ClausalIssue]:
    issues: list[ClausalIssue] = []
    if step.inference is None:
        return [ClausalIssue(step.name, f"{rule} step must have an inference record")]
    if step.inference.rule != rule:
        issues.append(ClausalIssue(step.name, f"rule must be '{rule}', got '{step.inference.rule}'"))
    if step.inference.status != InferenceStatus.THM:
        issues.append(ClausalIssue(step.name, f"status must be 'thm', got '{step.inference.status}'"))
    return issues


# --------------------------------------------------------------------------
# Shared term/formula helpers
# --------------------------------------------------------------------------


def _flatten_disjuncts(formula: object) -> list:
    """Flatten a (possibly n-ary) OR-junction into its list of disjuncts."""
    if isinstance(formula, JunctionFormula) and formula.connective == BinaryConnective.OR:
        return list(formula.operands)
    return [formula]


def _strip_negation(literal: object) -> tuple[object, bool]:
    """Split a literal into (base_atom, is_negative)."""
    if isinstance(literal, Negation):
        return literal.formula, True
    return literal, False


def _collect_variable_names(node: object, bound: frozenset[str] = frozenset()) -> set[str]:
    """Collect the names of all free (i.e. not locally quantifier-bound) variables."""
    if isinstance(node, Variable):
        return set() if node.name in bound else {node.name}
    if isinstance(node, Constant):
        return set()
    if isinstance(node, FunctionTerm):
        names: set[str] = set()
        for arg in node.args:
            names |= _collect_variable_names(arg, bound)
        return names
    if isinstance(node, Atom):
        names = set()
        for arg in node.args:
            names |= _collect_variable_names(arg, bound)
        return names
    if isinstance(node, Equality):
        return _collect_variable_names(node.left, bound) | _collect_variable_names(node.right, bound)
    if isinstance(node, Negation):
        return _collect_variable_names(node.formula, bound)
    if isinstance(node, BinaryFormula):
        return _collect_variable_names(node.left, bound) | _collect_variable_names(node.right, bound)
    if isinstance(node, JunctionFormula):
        names = set()
        for operand in node.operands:
            names |= _collect_variable_names(operand, bound)
        return names
    if isinstance(node, QuantifiedFormula):
        return _collect_variable_names(node.formula, bound | set(node.variables))
    return set()


def _collect_all_names(node: object) -> set[str]:
    """Collect every variable name occurring anywhere in a node, bound or free.

    Used to choose fresh names when renaming apart an equation's variables so
    they cannot accidentally clash with (and get captured by) names already
    used in the formula being rewritten.
    """
    names = _collect_variable_names(node)
    if isinstance(node, QuantifiedFormula):
        names |= set(node.variables)
        names |= _collect_all_names(node.formula)
    elif isinstance(node, Negation):
        names |= _collect_all_names(node.formula)
    elif isinstance(node, BinaryFormula):
        names |= _collect_all_names(node.left) | _collect_all_names(node.right)
    elif isinstance(node, JunctionFormula):
        for operand in node.operands:
            names |= _collect_all_names(operand)
    elif isinstance(node, Equality):
        names |= _collect_all_names(node.left) | _collect_all_names(node.right)
    elif isinstance(node, (Atom, FunctionTerm)):
        for arg in node.args:
            names |= _collect_all_names(arg)
    return names


def _matches_up_to_quantifier_permutation(candidate: object, target: object) -> bool:
    """Check alpha-equivalence, tolerating a differently ordered leading
    universal-quantifier prefix over the same (small) set of variables."""
    if is_alpha_equivalent(candidate, target):
        return True
    if (
        isinstance(candidate, QuantifiedFormula)
        and isinstance(target, QuantifiedFormula)
        and candidate.quantifier == target.quantifier
        and len(candidate.variables) == len(target.variables)
        and len(candidate.variables) <= _MAX_PERMUTATION_VARS
    ):
        for perm in permutations(candidate.variables):
            permuted = QuantifiedFormula(candidate.quantifier, list(perm), candidate.formula)
            if is_alpha_equivalent(permuted, target):
                return True
    return False


# --------------------------------------------------------------------------
# Reflexivity
# --------------------------------------------------------------------------


def check_reflexivity(step: AnnotatedFormula, parent: AnnotatedFormula) -> list[ClausalIssue]:
    """Check a reflexivity step: the conclusion must be a trivial `t = t`.

    The cited parent only serves as bookkeeping provenance for the term `t`;
    real ProoVer2026 proofs use it loosely (e.g. citing an unrelated equation
    that merely happens to be in scope), so its content is not otherwise
    constrained here.
    """
    del parent  # content intentionally not checked; see docstring
    issues = _check_inference_metadata(step, InferenceRule.REFLEXIVITY)
    if not isinstance(step.formula, Equality) or step.formula.negated:
        issues.append(ClausalIssue(step.name, "conclusion must be a non-negated equality"))
        return issues
    if not is_alpha_equivalent(step.formula.left, step.formula.right):
        issues.append(ClausalIssue(step.name, "conclusion is not a reflexive equality (left != right)"))
    return issues


# --------------------------------------------------------------------------
# Transitivity
# --------------------------------------------------------------------------


def check_transitivity(
    step: AnnotatedFormula, first_parent: AnnotatedFormula, second_parent: AnnotatedFormula
) -> list[ClausalIssue]:
    """Check a transitivity step chaining two equations sharing a common term."""
    issues = _check_inference_metadata(step, InferenceRule.TRANSITIVITY)

    eq1, eq2 = first_parent.formula, second_parent.formula
    if not isinstance(eq1, Equality) or eq1.negated:
        issues.append(ClausalIssue(step.name, "first parent must be a non-negated equality"))
        return issues
    if not isinstance(eq2, Equality) or eq2.negated:
        issues.append(ClausalIssue(step.name, "second parent must be a non-negated equality"))
        return issues

    endpoint_pairs = []
    if is_alpha_equivalent(eq1.right, eq2.left):
        endpoint_pairs.append((eq1.left, eq2.right))
    if is_alpha_equivalent(eq1.right, eq2.right):
        endpoint_pairs.append((eq1.left, eq2.left))
    if is_alpha_equivalent(eq1.left, eq2.left):
        endpoint_pairs.append((eq1.right, eq2.right))
    if is_alpha_equivalent(eq1.left, eq2.right):
        endpoint_pairs.append((eq1.right, eq2.left))

    if not endpoint_pairs:
        issues.append(ClausalIssue(step.name, "parents do not share a common term to chain transitivity on"))
        return issues

    if not isinstance(step.formula, Equality) or step.formula.negated:
        issues.append(ClausalIssue(step.name, "conclusion must be a non-negated equality"))
        return issues

    for left, right in endpoint_pairs:
        if (
            is_alpha_equivalent(step.formula.left, left) and is_alpha_equivalent(step.formula.right, right)
        ) or (
            is_alpha_equivalent(step.formula.left, right) and is_alpha_equivalent(step.formula.right, left)
        ):
            return issues

    issues.append(ClausalIssue(step.name, "conclusion does not match the transitive chain of its parents"))
    return issues


# --------------------------------------------------------------------------
# Rewrite (single-parent, no explicit equation cited)
# --------------------------------------------------------------------------


def check_rewrite(step: AnnotatedFormula, parent: AnnotatedFormula) -> list[ClausalIssue]:
    """Check a rewrite step.

    ProoVer2026 uses `rewrite` with a single parent and no separate equation
    reference, so the demodulator used is implicit/external. Without that
    equation we can only verify that the conclusion is the same formula as
    its parent (matching every occurrence observed in the corpus); the
    soundness of chains of such steps (e.g. cycles) is checked separately by
    the circular-dependency checker.
    """
    issues = _check_inference_metadata(step, InferenceRule.REWRITE)
    if not is_alpha_equivalent(step.formula, parent.formula):
        issues.append(ClausalIssue(step.name, "conclusion does not match its parent"))
    return issues


# --------------------------------------------------------------------------
# Paramodulation
# --------------------------------------------------------------------------


def _rewrite_occurrences(node: object, pattern: object, replacement: object, abstract_vars: set[str]) -> list:
    """Return every formula obtainable from `node` by replacing exactly one
    occurrence of a subterm matching `pattern` (which may use abstract_vars as
    schema variables) with the correspondingly-substituted `replacement`."""
    results: list = []
    substitutions: dict[str, object] = {}
    if match_template_to_instance(pattern, node, abstract_vars, {}, substitutions):
        results.append(substitute_node(replacement, dict(substitutions)))

    if isinstance(node, FunctionTerm):
        for i, arg in enumerate(node.args):
            for new_arg in _rewrite_occurrences(arg, pattern, replacement, abstract_vars):
                new_args = list(node.args)
                new_args[i] = new_arg
                results.append(FunctionTerm(node.functor, new_args))
    elif isinstance(node, Atom):
        for i, arg in enumerate(node.args):
            for new_arg in _rewrite_occurrences(arg, pattern, replacement, abstract_vars):
                new_args = list(node.args)
                new_args[i] = new_arg
                results.append(Atom(node.predicate, new_args))
    elif isinstance(node, Equality):
        for new_left in _rewrite_occurrences(node.left, pattern, replacement, abstract_vars):
            results.append(Equality(new_left, node.right, node.negated))
        for new_right in _rewrite_occurrences(node.right, pattern, replacement, abstract_vars):
            results.append(Equality(node.left, new_right, node.negated))
    elif isinstance(node, Negation):
        for new_inner in _rewrite_occurrences(node.formula, pattern, replacement, abstract_vars):
            results.append(Negation(new_inner))
    elif isinstance(node, BinaryFormula):
        for new_left in _rewrite_occurrences(node.left, pattern, replacement, abstract_vars):
            results.append(BinaryFormula(node.connective, new_left, node.right))
        for new_right in _rewrite_occurrences(node.right, pattern, replacement, abstract_vars):
            results.append(BinaryFormula(node.connective, node.left, new_right))
    elif isinstance(node, JunctionFormula):
        for i, operand in enumerate(node.operands):
            for new_op in _rewrite_occurrences(operand, pattern, replacement, abstract_vars):
                new_operands = list(node.operands)
                new_operands[i] = new_op
                results.append(JunctionFormula(node.connective, new_operands))
    elif isinstance(node, QuantifiedFormula):
        inner_abstract = abstract_vars - set(node.variables)
        for new_inner in _rewrite_occurrences(node.formula, pattern, replacement, inner_abstract):
            results.append(QuantifiedFormula(node.quantifier, list(node.variables), new_inner))
    return results


def _rename_apart(vars_: list[str], body: object, avoid: set[str]) -> tuple[list[str], object]:
    """Rename `vars_` (and their bound occurrences in `body`) to names that do
    not clash with anything in `avoid`, preventing accidental capture."""
    mapping: dict[str, str] = {}
    used = set(avoid)
    for name in vars_:
        candidate = name
        suffix = 0
        while candidate in used:
            suffix += 1
            candidate = f"{name}_r{suffix}"
        mapping[name] = candidate
        used.add(candidate)
    renamed_body = substitute_node(body, {name: Variable(new) for name, new in mapping.items()})
    return [mapping[name] for name in vars_], renamed_body


def _try_paramodulation(
    step_formula: object, equation_parent: AnnotatedFormula, target_parent: AnnotatedFormula
) -> bool:
    eq_vars, eq_body = flatten_prefix(equation_parent.formula, Quantifier.UNIVERSAL)
    if not isinstance(eq_body, Equality) or eq_body.negated:
        return False

    avoid = _collect_all_names(target_parent.formula)
    eq_vars, eq_body = _rename_apart(eq_vars, eq_body, avoid)
    abstract_vars = set(eq_vars)

    for pattern, replacement in ((eq_body.left, eq_body.right), (eq_body.right, eq_body.left)):
        for candidate in _rewrite_occurrences(target_parent.formula, pattern, replacement, abstract_vars):
            if _matches_up_to_quantifier_permutation(candidate, step_formula):
                return True
    return False


def check_paramodulation(
    step: AnnotatedFormula, first_parent: AnnotatedFormula, second_parent: AnnotatedFormula
) -> list[ClausalIssue]:
    """Check paramodulation: one parent supplies an equation, the other a
    formula in which one side of that equation is rewritten to the other."""
    issues = _check_inference_metadata(step, InferenceRule.PARAMODULATION)

    if _try_paramodulation(step.formula, first_parent, second_parent) or _try_paramodulation(
        step.formula, second_parent, first_parent
    ):
        return issues

    issues.append(
        ClausalIssue(
            step.name,
            "conclusion is not obtainable by rewriting one parent with an equation from the other",
        )
    )
    return issues


# --------------------------------------------------------------------------
# Resolution
# --------------------------------------------------------------------------


def _walk(term: object, subst: dict[str, object]) -> object:
    while isinstance(term, Variable) and term.name in subst:
        term = subst[term.name]
    return term


def _unify_terms(t1: object, t2: object, subst: dict[str, object]) -> dict[str, object] | None:
    t1 = _walk(t1, subst)
    t2 = _walk(t2, subst)
    if isinstance(t1, Variable) and isinstance(t2, Variable) and t1.name == t2.name:
        return subst
    if isinstance(t1, Variable):
        new_subst = dict(subst)
        new_subst[t1.name] = t2
        return new_subst
    if isinstance(t2, Variable):
        new_subst = dict(subst)
        new_subst[t2.name] = t1
        return new_subst
    if isinstance(t1, Constant) and isinstance(t2, Constant):
        return subst if t1.name == t2.name else None
    if isinstance(t1, FunctionTerm) and isinstance(t2, FunctionTerm):
        if t1.functor != t2.functor or len(t1.args) != len(t2.args):
            return None
        for a, b in zip(t1.args, t2.args):
            subst = _unify_terms(a, b, subst)
            if subst is None:
                return None
        return subst
    return None


def _unify_atoms(a1: object, a2: object, subst: dict[str, object]) -> dict[str, object] | None:
    if isinstance(a1, Atom) and isinstance(a2, Atom):
        if a1.predicate != a2.predicate or len(a1.args) != len(a2.args):
            return None
        for x, y in zip(a1.args, a2.args):
            subst = _unify_terms(x, y, subst)
            if subst is None:
                return None
        return subst
    if isinstance(a1, Equality) and isinstance(a2, Equality):
        if a1.negated != a2.negated:
            return None
        direct = _unify_terms(a1.left, a2.left, dict(subst))
        if direct is not None:
            direct = _unify_terms(a1.right, a2.right, direct)
            if direct is not None:
                return direct
        swapped = _unify_terms(a1.left, a2.right, dict(subst))
        if swapped is not None:
            swapped = _unify_terms(a1.right, a2.left, swapped)
            if swapped is not None:
                return swapped
        return None
    return None


def _build_resolvent(literals: list, preferred_order: list[str]) -> object:
    if not literals:
        return _FALSE_ATOM
    body = literals[0] if len(literals) == 1 else JunctionFormula(BinaryConnective.OR, literals)
    free_vars = _collect_variable_names(body)
    if not free_vars:
        return body
    ordered = [v for v in preferred_order if v in free_vars]
    ordered += sorted(free_vars - set(ordered))
    return QuantifiedFormula(Quantifier.UNIVERSAL, ordered, body)


def check_resolution(
    step: AnnotatedFormula, first_parent: AnnotatedFormula, second_parent: AnnotatedFormula
) -> list[ClausalIssue]:
    """Check binary clausal resolution between two (optionally universally
    quantified) disjunctive clauses, resolving on one pair of complementary,
    unifiable literals."""
    issues = _check_inference_metadata(step, InferenceRule.RESOLUTION)

    vars1, body1 = flatten_prefix(first_parent.formula, Quantifier.UNIVERSAL)
    vars2, body2 = flatten_prefix(second_parent.formula, Quantifier.UNIVERSAL)
    literals1 = _flatten_disjuncts(body1)
    literals2 = _flatten_disjuncts(body2)
    preferred_order = list(dict.fromkeys(vars1 + vars2))

    for i, lit1 in enumerate(literals1):
        base1, neg1 = _strip_negation(lit1)
        for j, lit2 in enumerate(literals2):
            base2, neg2 = _strip_negation(lit2)
            if neg1 == neg2:
                continue
            subst = _unify_atoms(base1, base2, {})
            if subst is None:
                continue

            remaining = [substitute_node(lit, subst) for k, lit in enumerate(literals1) if k != i]
            remaining += [substitute_node(lit, subst) for k, lit in enumerate(literals2) if k != j]

            deduped: list = []
            for lit in remaining:
                if not any(is_alpha_equivalent(lit, existing) for existing in deduped):
                    deduped.append(lit)

            resolvent = _build_resolvent(deduped, preferred_order)
            if _matches_up_to_quantifier_permutation(resolvent, step.formula):
                return issues

    issues.append(
        ClausalIssue(
            step.name,
            "no pair of complementary, unifiable literals in the parents produces the stated conclusion",
        )
    )
    return issues
