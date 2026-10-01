"""Check simple propositional inference steps."""

from dataclasses import dataclass

from src.checker.alpha_eq import is_alpha_equivalent
from src.checker.formula_utils import flatten_prefix, match_template_to_instance
from src.parser.ast_nodes import AnnotatedFormula, BinaryFormula, JunctionFormula
from src.var_mapping import BinaryConnective, InferenceRule, InferenceStatus, Quantifier


@dataclass
class PropositionalIssue:
    step_name: str
    reason: str


def _check_inference_metadata(step: AnnotatedFormula, rule: InferenceRule) -> list[PropositionalIssue]:
    issues: list[PropositionalIssue] = []
    if step.inference is None:
        return [PropositionalIssue(step.name, f"{rule} step must have an inference record")]
    if step.inference.rule != rule:
        issues.append(
            PropositionalIssue(step.name, f"rule must be '{rule}', got '{step.inference.rule}'")
        )
    if step.inference.status != InferenceStatus.THM:
        issues.append(
            PropositionalIssue(step.name, f"status must be 'thm', got '{step.inference.status}'")
        )
    return issues


def _flatten_conjuncts(formula: object) -> list:
    """Flatten a (possibly n-ary) AND-junction into its list of conjuncts.

    Non-conjunction formulas are returned as a single-element list so callers
    can uniformly concatenate parent conjuncts regardless of whether a parent
    is itself already a conjunction.
    """
    if isinstance(formula, JunctionFormula) and formula.connective == BinaryConnective.AND:
        return list(formula.operands)
    return [formula]


def check_conjunction(
    step: AnnotatedFormula, left_parent: AnnotatedFormula, right_parent: AnnotatedFormula
) -> list[PropositionalIssue]:
    """Check conjunction introduction from exactly two parent formulas.

    The parser represents "&" as an n-ary ``JunctionFormula``, so combining
    two parents that are themselves conjunctions produces a single flattened
    conjunction rather than a nested binary tree (e.g. combining ``A & B``
    with ``C`` yields ``A & B & C``, not ``(A & B) & C``). Both parents are
    therefore flattened before comparing against the conclusion's operands.
    """
    issues = _check_inference_metadata(step, InferenceRule.CONJUNCTION)
    if not isinstance(step.formula, JunctionFormula) or step.formula.connective != BinaryConnective.AND:
        issues.append(PropositionalIssue(step.name, "formula must be a conjunction"))
        return issues

    expected_operands = _flatten_conjuncts(left_parent.formula) + _flatten_conjuncts(right_parent.formula)
    actual_operands = step.formula.operands

    if len(actual_operands) != len(expected_operands):
        issues.append(
            PropositionalIssue(
                step.name,
                f"conjunction must have exactly {len(expected_operands)} operand(s) "
                f"(from flattening both parents), got {len(actual_operands)}",
            )
        )
        return issues

    for index, (expected, actual) in enumerate(zip(expected_operands, actual_operands)):
        if not is_alpha_equivalent(expected, actual):
            issues.append(
                PropositionalIssue(step.name, f"conjunction operand {index + 1} does not match its parent")
            )
    return issues


def check_split_conjunct(
    step: AnnotatedFormula, parent: AnnotatedFormula
) -> list[PropositionalIssue]:
    """Check extraction of one operand from a conjunction."""
    issues = _check_inference_metadata(step, InferenceRule.SPLIT_CONJUNCT)
    if not isinstance(parent.formula, JunctionFormula) or parent.formula.connective != BinaryConnective.AND:
        issues.append(PropositionalIssue(step.name, "parent formula must be a conjunction"))
        return issues
    if not any(is_alpha_equivalent(step.formula, operand) for operand in parent.formula.operands):
        issues.append(PropositionalIssue(step.name, "formula is not a conjunct of its parent"))
    return issues


def check_modus_ponens(
    step: AnnotatedFormula, first_parent: AnnotatedFormula, second_parent: AnnotatedFormula
) -> list[PropositionalIssue]:
    """Check modus ponens, allowing either parent order and universal instantiation."""
    issues = _check_inference_metadata(step, InferenceRule.MODUS_PONENS)
    parents = (first_parent.formula, second_parent.formula)

    for implication, premise in (parents, (parents[1], parents[0])):
        variables, body = flatten_prefix(implication, Quantifier.UNIVERSAL)
        if not isinstance(body, BinaryFormula) or body.connective != BinaryConnective.IMPLIES:
            continue
        substitutions: dict[str, object] = {}
        if match_template_to_instance(body.left, premise, set(variables), substitutions) and match_template_to_instance(
            body.right, step.formula, set(variables), substitutions
        ):
            return issues

    issues.append(
        PropositionalIssue(
            step.name,
            "parents and conclusion do not form a valid modus ponens step",
        )
    )
    return issues
