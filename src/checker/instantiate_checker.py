"""Checker for instantiate steps in proofs."""

from dataclasses import dataclass
from itertools import combinations

from src.checker.formula_utils import flatten_prefix, match_template_to_instance, substitute_node
from src.parser.ast_nodes import (
    AnnotatedFormula,
    Atom,
    BinaryFormula,
    Equality,
    JunctionFormula,
    Negation,
    QuantifiedFormula,
    Variable,
)
from src.var_mapping import InferenceRule, InferenceStatus, Quantifier


def _bound_names(node: object) -> set[str]:
    """Names of all variables bound by a quantifier somewhere inside ``node``."""
    if isinstance(node, QuantifiedFormula):
        return {str(v) for v in node.variables} | _bound_names(node.formula)
    if isinstance(node, Negation):
        return _bound_names(node.formula)
    if isinstance(node, BinaryFormula):
        return _bound_names(node.left) | _bound_names(node.right)
    if isinstance(node, JunctionFormula):
        names: set[str] = set()
        for operand in node.operands:
            names |= _bound_names(operand)
        return names
    if isinstance(node, (Atom, Equality)):
        return set()
    return set()


@dataclass
class InstantiateIssue:
    step_name: str
    reason: str


def check_instantiate(
    step: AnnotatedFormula, parent_step: AnnotatedFormula
) -> list[InstantiateIssue]:
    """Check whether a step is a valid instantiation of its parent."""
    issues: list[InstantiateIssue] = []

    if step.inference is None:
        issues.append(InstantiateIssue(step.name, "instantiate step must have an inference record"))
        return issues

    inf = step.inference
    if inf.rule != InferenceRule.INSTANTIATE:
        issues.append(InstantiateIssue(step.name, f"rule must be 'instantiate', got '{inf.rule}'"))

    if inf.status != InferenceStatus.THM:
        issues.append(InstantiateIssue(step.name, f"status must be 'thm', got '{inf.status}'"))

    # Handle De Morgan's laws: ~∃X. P ≡ ∀X. ¬P
    # This generalizes to multiple existential quantifiers: ~∃X. ∃Y. P ≡ ∀X. ∀Y. ¬P
    parent_formula = parent_step.formula
    if isinstance(parent_formula, Negation) and isinstance(
        parent_formula.formula, QuantifiedFormula
    ):
        inner = parent_formula.formula
        if inner.quantifier == Quantifier.EXISTENTIAL:
            # Collect all leading existential quantifiers
            all_vars = []
            current = inner
            while (
                isinstance(current, QuantifiedFormula)
                and current.quantifier == Quantifier.EXISTENTIAL
            ):
                all_vars.extend(current.variables)
                current = current.formula
            # Convert ~∃X.∃Y.... P to ∀X.∀Y.... ¬P
            parent_formula = QuantifiedFormula(
                quantifier=Quantifier.UNIVERSAL,
                variables=all_vars,
                formula=Negation(current),
            )

    parent_vars, parent_body = flatten_prefix(parent_formula, Quantifier.UNIVERSAL)
    child_vars, child_body = flatten_prefix(step.formula, Quantifier.UNIVERSAL)

    if len(child_vars) > len(parent_vars):
        issues.append(
            InstantiateIssue(
                step.name,
                "child has more leading universal variables than the parent formula",
            )
        )
        return issues

    if not parent_vars and not child_vars:
        if not match_template_to_instance(parent_formula, step.formula, set()):
            issues.append(
                InstantiateIssue(
                    step.name,
                    "formula is not an instance of the parent formula",
                )
            )
        return issues

    inner_bound = _bound_names(parent_body)
    found = False
    for kept_indices in combinations(range(len(parent_vars)), len(child_vars)):
        kept_map = {
            parent_vars[parent_index]: Variable(step_var)
            for step_var, parent_index in zip(child_vars, kept_indices)
        }
        removed_vars = set(parent_vars) - set(kept_map)
        if any(v.name in inner_bound and v.name != old for old, v in kept_map.items()):
            continue
        transformed_parent_body = substitute_node(parent_body, kept_map)

        if match_template_to_instance(transformed_parent_body, child_body, removed_vars):
            found = True
            break

    if not found:
        issues.append(
            InstantiateIssue(
                step.name,
                "formula is not a valid instantiation of the parent formula",
            )
        )

    return issues
