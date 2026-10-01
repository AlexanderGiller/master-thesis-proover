"""Checkers for junction-reshaping and tautology-introduction proof steps.

These cover ``weaken`` (OR-introduction), ``commute`` (swapping the two
operands of a top-level conjunction/disjunction), and ``excluded_middle``
(introducing a fresh ``phi | ~phi`` tautology). All three are purely
syntactic/structural rules that can be verified quickly without delegating
to an external ATP, which matters because these rules tend to appear many
times within a single proof.
"""

from dataclasses import dataclass

from src.checker.alpha_eq import is_alpha_equivalent
from src.parser.ast_nodes import AnnotatedFormula, JunctionFormula, Negation
from src.var_mapping import BinaryConnective, InferenceRule, InferenceStatus


@dataclass
class JunctionIssue:
    step_name: str
    reason: str


def _check_inference_metadata(step: AnnotatedFormula, rule: InferenceRule) -> list[JunctionIssue]:
    issues: list[JunctionIssue] = []
    if step.inference is None:
        return [JunctionIssue(step.name, f"{rule} step must have an inference record")]
    if step.inference.rule != rule:
        issues.append(
            JunctionIssue(step.name, f"rule must be '{rule}', got '{step.inference.rule}'")
        )
    if step.inference.status != InferenceStatus.THM:
        issues.append(
            JunctionIssue(step.name, f"status must be 'thm', got '{step.inference.status}'")
        )
    return issues


def _flatten(formula: object, connective: BinaryConnective) -> list:
    """Flatten a (possibly n-ary) junction into its list of operands.

    Non-matching formulas are returned as a single-element list so callers
    can uniformly compare a parent regardless of whether it is itself
    already a junction of the target connective.
    """
    if isinstance(formula, JunctionFormula) and formula.connective == connective:
        return list(formula.operands)
    return [formula]


def check_weaken(step: AnnotatedFormula, parent: AnnotatedFormula) -> list[JunctionIssue]:
    """Check weaken (OR-introduction/addition): from phi, infer phi | psi (or
    phi | psi_1 | ... | psi_n) for arbitrary new disjunct(s).

    The parser flattens ``|``-chains into a single n-ary ``JunctionFormula``,
    so both the parent and the conclusion are flattened the same way, and the
    parent's flattened disjuncts must appear, in order, as a prefix of the
    conclusion's flattened disjuncts, with at least one new disjunct added.
    """
    issues = _check_inference_metadata(step, InferenceRule.WEAKEN)
    if issues:
        return issues

    parent_operands = _flatten(parent.formula, BinaryConnective.OR)
    child_operands = _flatten(step.formula, BinaryConnective.OR)

    if len(child_operands) <= len(parent_operands):
        issues.append(
            JunctionIssue(
                step.name,
                "weaken must add at least one new disjunct on top of the parent formula",
            )
        )
        return issues

    for index, (expected, actual) in enumerate(zip(parent_operands, child_operands)):
        if not is_alpha_equivalent(expected, actual):
            issues.append(
                JunctionIssue(step.name, f"disjunct {index + 1} does not match the parent formula")
            )
            return issues

    return issues


def check_commute(step: AnnotatedFormula, parent: AnnotatedFormula) -> list[JunctionIssue]:
    """Check commute: swaps the two top-level operands of a conjunction or
    disjunction (e.g. ``A & B`` becomes ``B & A``)."""
    issues = _check_inference_metadata(step, InferenceRule.COMMUTE)
    if issues:
        return issues

    parent_formula = parent.formula
    child_formula = step.formula

    if (
        not isinstance(parent_formula, JunctionFormula)
        or not isinstance(child_formula, JunctionFormula)
        or parent_formula.connective != child_formula.connective
        or len(parent_formula.operands) != 2
        or len(child_formula.operands) != 2
    ):
        issues.append(
            JunctionIssue(
                step.name,
                "commute requires both formulas to be a 2-operand conjunction/disjunction "
                "of the same connective",
            )
        )
        return issues

    if not (
        is_alpha_equivalent(parent_formula.operands[0], child_formula.operands[1])
        and is_alpha_equivalent(parent_formula.operands[1], child_formula.operands[0])
    ):
        issues.append(JunctionIssue(step.name, "operands are not a swap of the parent's operands"))

    return issues


def check_excluded_middle(step: AnnotatedFormula) -> list[JunctionIssue]:
    """Check excluded_middle: the conclusion must be of the form ``phi | ~phi``.

    This is a zero-premise tautology-introduction rule (the law of excluded
    middle): the cited parent step is only used to link the step into the
    proof DAG for bookkeeping, and its content does not otherwise constrain
    the introduced ``phi``.

    Because the parser flattens ``|``-chains into a single n-ary
    ``JunctionFormula``, a case like ``A | B | ~(A | B)`` (i.e. ``phi | ~phi``
    with ``phi = A | B``) is represented with three top-level operands rather
    than two. To handle this, every operand that is a negation is tried as
    the ``~phi`` side, with the remaining (re-flattened) operands compared
    against its inner formula.
    """
    issues = _check_inference_metadata(step, InferenceRule.EXCLUDED_MIDDLE)
    if issues:
        return issues

    operands = _flatten(step.formula, BinaryConnective.OR)
    if len(operands) < 2:
        issues.append(JunctionIssue(step.name, "excluded_middle formula must be a disjunction"))
        return issues

    for index, operand in enumerate(operands):
        if not isinstance(operand, Negation):
            continue
        remaining = operands[:index] + operands[index + 1 :]
        phi = remaining[0] if len(remaining) == 1 else JunctionFormula(BinaryConnective.OR, remaining)
        if is_alpha_equivalent(phi, operand.formula):
            return issues

    issues.append(
        JunctionIssue(step.name, "excluded_middle formula must be of the form (phi | ~phi)")
    )
    return issues
