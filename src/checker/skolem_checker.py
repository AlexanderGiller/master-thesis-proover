"""Checker for Skolemization in logical formulas."""

from dataclasses import dataclass
from itertools import count

from src.checker.alpha_eq import is_alpha_equivalent
from src.checker.negated_conjecture_checker import _clone_with_fresh_bound_vars
from src.parser.ast_nodes import (
    AnnotatedFormula,
    Atom,
    BinaryFormula,
    Constant,
    Equality,
    FunctionTerm,
    JunctionFormula,
    Negation,
    NewSymbolsInfo,
    QuantifiedFormula,
    SkolemizeInfo,
    Variable,
)
from src.var_mapping import InferenceRule, InferenceStatus, Quantifier


@dataclass
class SkolemizationIssue:
    step_name: str
    reason: str


def _normalize_variables(variables: object) -> list[str]:
    if isinstance(variables, (list, tuple)):
        return [str(var) for var in variables]
    return [str(variables)]


def _skolem_term_argument_names(term: object) -> list[str] | None:
    if not isinstance(term, FunctionTerm):
        return None
    names: list[str] = []
    for arg in term.args:
        if not isinstance(arg, Variable):
            return None
        names.append(arg.name)
    return names


def _fresh_name(used_names: set[str], counter: count) -> str:
    while True:
        candidate = f"V{next(counter)}"
        if candidate not in used_names:
            used_names.add(candidate)
            return candidate


def _rename_node(node: object, rename_map: dict[str, str]) -> object:
    if isinstance(node, Variable):
        return Variable(rename_map.get(node.name, node.name))
    if isinstance(node, Constant):
        return Constant(node.name)
    if isinstance(node, FunctionTerm):
        return FunctionTerm(
            functor=node.functor,
            args=[_rename_node(arg, rename_map) for arg in node.args],
        )
    if isinstance(node, Atom):
        return Atom(
            predicate=node.predicate,
            args=[_rename_node(arg, rename_map) for arg in node.args],
        )
    if isinstance(node, Equality):
        return Equality(
            left=_rename_node(node.left, rename_map),
            right=_rename_node(node.right, rename_map),
            negated=node.negated,
        )
    if isinstance(node, Negation):
        return Negation(_rename_node(node.formula, rename_map))
    if isinstance(node, BinaryFormula):
        return BinaryFormula(
            connective=node.connective,
            left=_rename_node(node.left, rename_map),
            right=_rename_node(node.right, rename_map),
        )
    if isinstance(node, JunctionFormula):
        return JunctionFormula(
            connective=node.connective,
            operands=[_rename_node(op, rename_map) for op in node.operands],
        )
    if isinstance(node, QuantifiedFormula):
        return QuantifiedFormula(
            quantifier=node.quantifier,
            variables=[rename_map.get(str(var), str(var)) for var in _normalize_variables(node.variables)],
            formula=_rename_node(node.formula, rename_map),
        )
    return node


def _skolemize_formula(
    node: object,
    target_var: str,
    skolem_term: object,
    scope: list[str],
    active: bool,
    rename_map: dict[str, str],
    used_names: set[str],
    counter: count,
    capture: dict[str, object],
) -> tuple[object, bool]:
    if isinstance(node, Atom):
        return (
            Atom(
                predicate=node.predicate,
                args=[
                    _skolemize_formula(
                        arg, target_var, skolem_term, scope, active, rename_map, used_names, counter, capture
                    )[0]
                    for arg in node.args
                ],
            ),
            capture["found"],
        )

    if isinstance(node, FunctionTerm):
        return (
            FunctionTerm(
                functor=node.functor,
                args=[
                    _skolemize_formula(
                        arg, target_var, skolem_term, scope, active, rename_map, used_names, counter, capture
                    )[0]
                    for arg in node.args
                ],
            ),
            capture["found"],
        )

    if isinstance(node, Variable):
        renamed = rename_map.get(node.name, node.name)
        if active and node.name == target_var:
            return _rename_node(skolem_term, capture.get("rename_map", rename_map)), capture["found"]
        return Variable(renamed), capture["found"]

    if isinstance(node, Constant):
        return Constant(node.name), capture["found"]

    if isinstance(node, Negation):
        inner, found = _skolemize_formula(
            node.formula, target_var, skolem_term, scope, active, rename_map, used_names, counter, capture
        )
        return Negation(inner), found

    if isinstance(node, BinaryFormula):
        left, found_left = _skolemize_formula(
            node.left, target_var, skolem_term, scope, active, rename_map, used_names, counter, capture
        )
        right, found_right = _skolemize_formula(
            node.right, target_var, skolem_term, scope, active, rename_map, used_names, counter, capture
        )
        return BinaryFormula(connective=node.connective, left=left, right=right), found_left or found_right

    if isinstance(node, JunctionFormula):
        operands = []
        found = False
        for operand in node.operands:
            transformed, operand_found = _skolemize_formula(
                operand, target_var, skolem_term, scope, active, rename_map, used_names, counter, capture
            )
            operands.append(transformed)
            found = found or operand_found
        return JunctionFormula(connective=node.connective, operands=operands), found

    if isinstance(node, Equality):
        left, found_left = _skolemize_formula(
            node.left, target_var, skolem_term, scope, active, rename_map, used_names, counter, capture
        )
        right, found_right = _skolemize_formula(
            node.right, target_var, skolem_term, scope, active, rename_map, used_names, counter, capture
        )
        return Equality(left=left, right=right, negated=node.negated), found_left or found_right

    if isinstance(node, QuantifiedFormula):
        vars_iter = _normalize_variables(node.variables)
        local_map = dict(rename_map)
        fresh_vars = []
        for var in vars_iter:
            fresh = _fresh_name(used_names, counter)
            local_map[var] = fresh
            fresh_vars.append(fresh)

        if node.quantifier == Quantifier.UNIVERSAL:
            next_scope = scope + fresh_vars
            inner, found = _skolemize_formula(
                node.formula,
                target_var,
                skolem_term,
                next_scope,
                active,
                local_map,
                used_names,
                counter,
                capture,
            )
            return (
                QuantifiedFormula(
                    quantifier=node.quantifier, variables=fresh_vars, formula=inner
                ),
                found,
            )

        if node.quantifier == Quantifier.EXISTENTIAL and target_var in vars_iter:
            if active or capture["found"]:
                inner, found = _skolemize_formula(
                    node.formula,
                    target_var,
                    skolem_term,
                    scope,
                    False,
                    local_map,
                    used_names,
                    counter,
                    capture,
                )
                return (
                    QuantifiedFormula(
                        quantifier=node.quantifier, variables=fresh_vars, formula=inner
                    ),
                    found,
                )

            capture["found"] = True
            capture["universals"] = list(scope)
            capture["rename_map"] = dict(rename_map)
            remaining = [fresh for original, fresh in zip(vars_iter, fresh_vars) if original != target_var]
            inner, _ = _skolemize_formula(
                node.formula,
                target_var,
                skolem_term,
                scope,
                True,
                local_map,
                used_names,
                counter,
                capture,
            )
            if remaining:
                return (
                    QuantifiedFormula(
                        quantifier=node.quantifier, variables=remaining, formula=inner
                    ),
                    True,
                )
            return inner, True

        inner, found = _skolemize_formula(
            node.formula,
            target_var,
            skolem_term,
            scope,
            active,
            local_map,
            used_names,
            counter,
            capture,
        )
        return (
            QuantifiedFormula(quantifier=node.quantifier, variables=fresh_vars, formula=inner),
            found,
        )

    return node, capture["found"]


def check_skolemization(
    skolem_step: AnnotatedFormula, parent_step: AnnotatedFormula
) -> list[SkolemizationIssue]:
    """Check if the skolem_step is a valid Skolemization of the parent_step."""
    issues: list[SkolemizationIssue] = []

    if skolem_step.inference is None:
        issues.append(
            SkolemizationIssue(skolem_step.name, "skolemize step must have an inference record")
        )
        return issues

    inf = skolem_step.inference
    if inf.rule != InferenceRule.SKOLEMIZE:
        issues.append(
            SkolemizationIssue(skolem_step.name, f"rule must be 'skolemize', got '{inf.rule}'")
        )

    if inf.status != InferenceStatus.ESA:
        issues.append(
            SkolemizationIssue(skolem_step.name, f"status must be 'esa', got '{inf.status}'")
        )

    new_symbols_info = next((item for item in inf.info if isinstance(item, NewSymbolsInfo)), None)
    if (
        new_symbols_info is None
        or new_symbols_info.kind != "skolem"
        or len(new_symbols_info.symbols) != 1
    ):
        issues.append(
            SkolemizationIssue(
                skolem_step.name,
                "skolemize must introduce exactly one new Skolem symbol via new_symbols(skolem, [...])",
            )
        )

    skolemize_info = next((item for item in inf.info if isinstance(item, SkolemizeInfo)), None)
    if skolemize_info is None or not skolemize_info.variable:
        issues.append(
            SkolemizationIssue(
                skolem_step.name,
                "skolemize info must indicate the existential variable being eliminated",
            )
        )
        return issues
    if skolemize_info.term is None:
        issues.append(
            SkolemizationIssue(
                skolem_step.name, "skolemize info must include the resulting Skolem term"
            )
        )
        return issues

    introduced = new_symbols_info.symbols[0] if new_symbols_info else None
    sk_term = skolemize_info.term
    if not isinstance(sk_term, FunctionTerm):
        issues.append(
            SkolemizationIssue(
                skolem_step.name, "Skolem term must be a function term with the introduced functor"
            )
        )
        return issues

    if introduced and sk_term.functor != introduced:
        issues.append(
            SkolemizationIssue(
                skolem_step.name,
                f"Skolem term functor '{sk_term.functor}' does not match introduced symbol '{introduced}'",
            )
        )

    capture = {"found": False, "universals": None}
    expected, found = _skolemize_formula(
        parent_step.formula,
        skolemize_info.variable,
        sk_term,
        [],
        False,
        {},
        set(),
        count(0),
        capture,
    )
    universals_at_elim = capture["universals"]

    if not found or universals_at_elim is None:
        issues.append(
            SkolemizationIssue(
                skolem_step.name,
                f"existential variable '{skolemize_info.variable}' not found in parent formula",
            )
        )
        return issues

    scope_rename_map = capture.get("rename_map", {})
    normalized_sk_term = _rename_node(sk_term, scope_rename_map)
    arg_vars = _skolem_term_argument_names(normalized_sk_term)
    if arg_vars is None:
        issues.append(
            SkolemizationIssue(
                skolem_step.name,
                "Skolem term must be a function applied to the universally scoped variables",
            )
        )
    elif arg_vars != universals_at_elim:
        issues.append(
            SkolemizationIssue(
                skolem_step.name,
                f"Skolem term arguments {arg_vars} do not match universal variables in scope {universals_at_elim}",
            )
        )

    normalized_expected = _clone_with_fresh_bound_vars(expected)
    normalized_actual = _clone_with_fresh_bound_vars(skolem_step.formula)
    if not is_alpha_equivalent(normalized_expected, normalized_actual):
        issues.append(
            SkolemizationIssue(
                skolem_step.name,
                "The resulting formula is not a correct Skolemization of the parent formula",
            )
        )

    return issues
