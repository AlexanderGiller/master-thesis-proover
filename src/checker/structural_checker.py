"""Checkers for structural proof steps that reshape a formula without changing
its logical content: copy, duplicate, rename_variable, double_negation, and
remove_double_negation."""

from dataclasses import dataclass

from src.checker.alpha_eq import is_alpha_equivalent
from src.parser.ast_nodes import AnnotatedFormula, Negation
from src.var_mapping import InferenceRule, InferenceStatus


@dataclass
class StructuralIssue:
    step_name: str
    reason: str


def _check_inference_metadata(step: AnnotatedFormula, rule: InferenceRule) -> list[StructuralIssue]:
    issues: list[StructuralIssue] = []
    if step.inference is None:
        return [StructuralIssue(step.name, f"{rule} step must have an inference record")]
    if step.inference.rule != rule:
        issues.append(
            StructuralIssue(step.name, f"rule must be '{rule}', got '{step.inference.rule}'")
        )
    if step.inference.status != InferenceStatus.THM:
        issues.append(
            StructuralIssue(step.name, f"status must be 'thm', got '{step.inference.status}'")
        )
    return issues


def check_copy(step: AnnotatedFormula, parent: AnnotatedFormula) -> list[StructuralIssue]:
    """Check that a copy step reproduces its parent formula unchanged
    (up to alpha-equivalence)."""
    issues = _check_inference_metadata(step, InferenceRule.COPY)
    if not is_alpha_equivalent(step.formula, parent.formula):
        issues.append(StructuralIssue(step.name, "copied formula does not match its parent"))
    return issues


def check_duplicate(
    step: AnnotatedFormula, first_parent: AnnotatedFormula, second_parent: AnnotatedFormula
) -> list[StructuralIssue]:
    """Check duplicate: two (usually identical) parent references that must be
    alpha-equivalent to each other, with the conclusion matching both."""
    issues = _check_inference_metadata(step, InferenceRule.DUPLICATE)
    if not is_alpha_equivalent(first_parent.formula, second_parent.formula):
        issues.append(StructuralIssue(step.name, "the two parent formulas are not alpha-equivalent"))
        return issues
    if not is_alpha_equivalent(step.formula, first_parent.formula):
        issues.append(StructuralIssue(step.name, "duplicated formula does not match its parents"))
    return issues


def check_rename_variable(step: AnnotatedFormula, parent: AnnotatedFormula) -> list[StructuralIssue]:
    """Check that a rename_variable step only renames (bound) variables,
    i.e. the resulting formula must be alpha-equivalent to its parent."""
    issues = _check_inference_metadata(step, InferenceRule.RENAME_VARIABLE)
    if not is_alpha_equivalent(step.formula, parent.formula):
        issues.append(
            StructuralIssue(step.name, "formula is not a variable-renaming of its parent")
        )
    return issues


def check_double_negation(step: AnnotatedFormula, parent: AnnotatedFormula) -> list[StructuralIssue]:
    """Check that a double_negation step wraps the parent formula in ~~."""
    issues = _check_inference_metadata(step, InferenceRule.DOUBLE_NEGATION)
    if not isinstance(step.formula, Negation) or not isinstance(step.formula.formula, Negation):
        issues.append(StructuralIssue(step.name, "formula must be a double negation (~~...)"))
        return issues
    inner = step.formula.formula.formula
    if not is_alpha_equivalent(inner, parent.formula):
        issues.append(
            StructuralIssue(
                step.name, "double-negated formula does not match its parent once unwrapped"
            )
        )
    return issues


def check_remove_double_negation(
    step: AnnotatedFormula, parent: AnnotatedFormula
) -> list[StructuralIssue]:
    """Check that a remove_double_negation step strips a leading ~~ from the parent."""
    issues = _check_inference_metadata(step, InferenceRule.REMOVE_DOUBLE_NEGATION)
    if not isinstance(parent.formula, Negation) or not isinstance(parent.formula.formula, Negation):
        issues.append(StructuralIssue(step.name, "parent formula must be a double negation (~~...)"))
        return issues
    inner = parent.formula.formula.formula
    if not is_alpha_equivalent(step.formula, inner):
        issues.append(
            StructuralIssue(
                step.name, "formula does not match the parent with its double negation removed"
            )
        )
    return issues
