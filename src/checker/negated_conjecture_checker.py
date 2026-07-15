"""Checker for negated_conjecture steps in proofs."""

from dataclasses import dataclass
from src.parser.ast_nodes import (
    AnnotatedFormula, QuantifiedFormula, Negation, Variable, InferenceRecord
)
from src.checker.alpha_eq import is_alpha_equivalent


@dataclass
class NegatedConjectureIssue:
    step_name: str
    reason: str


def _negate_formula(formula):
    """Negate a formula according to logical rules.
    
    - Negating a negation: ~(~P) = P (double negation elimination)
    - ![X]: P(X) becomes ?[X]: ~P(X)
    - ?[X]: P(X) becomes ![X]: ~P(X)
    - ~(![X]: P(X)) becomes ?[X]: ~P(X)
    - ~(?[X]: P(X)) becomes ![X]: ~P(X)
    - Other formulas become ~(formula)
    """
    if isinstance(formula, Negation):
        inner = formula.formula
        # Double negation: ~(~P) = P
        if isinstance(inner, Negation):
            return inner.formula
        # De Morgan's law: ~(![X]: P) becomes ?[X]: ~P
        # and ~(?[X]: P) becomes ![X]: ~P
        elif isinstance(inner, QuantifiedFormula):
            new_quantifier = "?" if inner.quantifier == "!" else "!"
            negated_inner = _negate_formula(inner.formula)
            return QuantifiedFormula(
                quantifier=new_quantifier,
                variables=inner.variables,
                formula=negated_inner
            )
        else:
            # ~(non-quantified, non-negation) = remove the negation
            return inner
    elif isinstance(formula, QuantifiedFormula):
        # Flip the quantifier and negate the inner formula
        new_quantifier = "?" if formula.quantifier == "!" else "!"
        negated_inner = _negate_formula(formula.formula)
        return QuantifiedFormula(
            quantifier=new_quantifier,
            variables=formula.variables,
            formula=negated_inner
        )
    else:
        # For non-quantified formulas, wrap in negation
        return Negation(formula)


def check_negated_conjecture(
    neg_conj_step: AnnotatedFormula,
    parent_conj_step: AnnotatedFormula
) -> list[NegatedConjectureIssue]:
    """Verify that a negated_conjecture step is correctly derived from its parent conjecture.

    Checks:
    1. The step has rule "negated_conjecture"
    2. The step has status "cth" in its inference record
    3. The formula is the exact negation of the parent conjecture formula
       (with quantifiers transformed and variables properly handled)
    """
    issues: list[NegatedConjectureIssue] = []
    name = neg_conj_step.name

    # Check that step has an inference record (negated_conjecture must be derived)
    if neg_conj_step.inference is None:
        issues.append(NegatedConjectureIssue(
            name, "negated_conjecture step must have an inference record"
        ))
        return issues

    # Check rule is "negated_conjecture"
    if neg_conj_step.inference.rule != "negated_conjecture":
        issues.append(NegatedConjectureIssue(
            name,
            f"rule must be 'negated_conjecture', got '{neg_conj_step.inference.rule}'"
        ))

    # Check status is "cth" (Conjecture THeorem negation)
    if neg_conj_step.inference.status != "cth":
        issues.append(NegatedConjectureIssue(
            name,
            f"status must be 'cth', got '{neg_conj_step.inference.status}'"
        ))

    # Check that the formula is the correct negation
    # Two acceptable forms:
    # 1. Expected form: parent negated with De Morgan's laws applied
    #    e.g., ![X]: p(X) becomes ?[X]: ~p(X)
    # 2. Direct form: parent wrapped in simple negation (not simplified)
    #    e.g., ![X]: p(X) becomes ~(![X]: p(X))
    
    expected_negation = _negate_formula(parent_conj_step.formula)
    direct_negation = Negation(parent_conj_step.formula)
    
    form1_match = is_alpha_equivalent(neg_conj_step.formula, expected_negation)
    form2_match = is_alpha_equivalent(neg_conj_step.formula, direct_negation)
    
    if not (form1_match or form2_match):
        issues.append(NegatedConjectureIssue(
            name,
            f"formula is not the correct negation of parent conjecture; "
            f"expected: {expected_negation!r}, got: {neg_conj_step.formula!r}"
        ))

    return issues

