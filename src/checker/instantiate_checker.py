"""Checker for instantiate steps in proofs."""

from dataclasses import dataclass
from itertools import combinations

from src.checker.formula_utils import flatten_prefix, match_template_to_instance, substitute_node
from src.parser.ast_nodes import AnnotatedFormula
from src.var_mapping import InferenceRule, InferenceStatus, Quantifier


@dataclass
class InstantiateIssue:
    step_name: str
    reason: str


def check_instantiate(step: AnnotatedFormula, parent_step: AnnotatedFormula) -> list[InstantiateIssue]:
    """Check whether a step is a valid instantiation of its parent."""
    issues: list[InstantiateIssue] = []

    if step.inference is None:
        issues.append(InstantiateIssue(step.name, "instantiate step must have an inference record"))
        return issues

    inf = step.inference
    if inf.rule != InferenceRule.INSTANTIATE:
        issues.append(
            InstantiateIssue(step.name, f"rule must be 'instantiate', got '{inf.rule}'")
        )

    if inf.status != InferenceStatus.THM:
        issues.append(InstantiateIssue(step.name, f"status must be 'thm', got '{inf.status}'"))

    parent_vars, parent_body = flatten_prefix(parent_step.formula, Quantifier.UNIVERSAL)
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
        if not match_template_to_instance(parent_step.formula, step.formula, set()):
            issues.append(
                InstantiateIssue(
                    step.name,
                    "formula is not an instance of the parent formula",
                )
            )
        return issues

    found = False
    for kept_indices in combinations(range(len(parent_vars)), len(child_vars)):
        kept_map = {
            parent_vars[parent_index]: step_var
            for step_var, parent_index in zip(child_vars, kept_indices)
        }
        removed_vars = set(parent_vars) - set(kept_map)
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
