"""Checker for negated_conjecture steps in proofs."""

from dataclasses import dataclass
from itertools import count

from src.checker.alpha_eq import is_alpha_equivalent
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
from src.var_mapping import BinaryConnective, FormulaRole, InferenceRule, InferenceStatus, Quantifier


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
        if isinstance(inner, Negation):
            return inner.formula
        if isinstance(inner, QuantifiedFormula):
            new_quantifier = (
                Quantifier.EXISTENTIAL
                if inner.quantifier == Quantifier.UNIVERSAL
                else Quantifier.UNIVERSAL
            )
            negated_inner = _negate_formula(inner.formula)
            return QuantifiedFormula(
                quantifier=new_quantifier, variables=inner.variables, formula=negated_inner
            )
        return inner
    if isinstance(formula, QuantifiedFormula):
        new_quantifier = (
            Quantifier.EXISTENTIAL
            if formula.quantifier == Quantifier.UNIVERSAL
            else Quantifier.UNIVERSAL
        )
        negated_inner = _negate_formula(formula.formula)
        return QuantifiedFormula(
            quantifier=new_quantifier, variables=formula.variables, formula=negated_inner
        )
    if isinstance(formula, JunctionFormula):
        return _negate_junction(formula)
    if isinstance(formula, BinaryFormula):
        return _negate_binary_formula(formula)
    if isinstance(formula, Equality):
        return _negate_equality(formula)
    return Negation(formula)


def _negate_junction(formula: JunctionFormula) -> JunctionFormula:
    if formula.connective == BinaryConnective.AND:
        flipped_connective = BinaryConnective.OR
    elif formula.connective == BinaryConnective.OR:
        flipped_connective = BinaryConnective.AND
    else:
        return Negation(formula)
    return JunctionFormula(
        connective=flipped_connective,
        operands=[_negate_formula(operand) for operand in formula.operands],
    )


def _negate_binary_formula(formula: BinaryFormula):
    connective = str(formula.connective)
    if connective == "=>":
        return JunctionFormula(BinaryConnective.AND, [formula.left, _negate_formula(formula.right)])
    if connective == "<=":
        return JunctionFormula(BinaryConnective.AND, [_negate_formula(formula.left), formula.right])
    if connective == "<=>":
        return JunctionFormula(
            BinaryConnective.OR,
            [
                JunctionFormula(BinaryConnective.AND, [formula.left, _negate_formula(formula.right)]),
                JunctionFormula(BinaryConnective.AND, [_negate_formula(formula.left), formula.right]),
            ],
        )
    if connective == "<~>":
        return JunctionFormula(
            BinaryConnective.OR,
            [
                JunctionFormula(BinaryConnective.AND, [formula.left, formula.right]),
                JunctionFormula(
                    BinaryConnective.AND,
                    [_negate_formula(formula.left), _negate_formula(formula.right)],
                ),
            ],
        )
    if connective == "~|":
        return JunctionFormula(BinaryConnective.OR, [formula.left, formula.right])
    if connective == "~&":
        return JunctionFormula(BinaryConnective.AND, [formula.left, formula.right])
    return Negation(formula)


def _negate_equality(formula: Equality) -> Equality:
    return Equality(left=formula.left, right=formula.right, negated=not formula.negated)


def _clone_with_fresh_bound_vars(formula, used_names=None, counter=None, env=None):
    """Rename every bound variable to a fresh name while preserving scope."""
    if used_names is None:
        used_names = set()
    if counter is None:
        counter = count(0)
    if env is None:
        env = {}

    def fresh_name() -> str:
        while True:
            candidate = f"V{next(counter)}"
            if candidate not in used_names:
                used_names.add(candidate)
                return candidate

    def walk(node, bound_env):
        if isinstance(node, Variable):
            return Variable(bound_env.get(node.name, node.name))
        if isinstance(node, Constant):
            return Constant(node.name)
        if isinstance(node, Atom):
            return Atom(node.predicate, [walk(arg, bound_env) for arg in node.args])
        if isinstance(node, Equality):
            return Equality(
                left=walk(node.left, bound_env),
                right=walk(node.right, bound_env),
                negated=node.negated,
            )
        if isinstance(node, FunctionTerm):
            return FunctionTerm(node.functor, [walk(arg, bound_env) for arg in node.args])
        if isinstance(node, Negation):
            return Negation(walk(node.formula, bound_env))
        if isinstance(node, BinaryFormula):
            return BinaryFormula(
                connective=node.connective,
                left=walk(node.left, bound_env),
                right=walk(node.right, bound_env),
            )
        if isinstance(node, JunctionFormula):
            return JunctionFormula(
                connective=node.connective,
                operands=[walk(op, bound_env) for op in node.operands],
            )
        if isinstance(node, QuantifiedFormula):
            local_env = dict(bound_env)
            renamed_vars = []
            for var in node.variables:
                new_name = fresh_name()
                local_env[str(var)] = new_name
                renamed_vars.append(new_name)
            return QuantifiedFormula(
                quantifier=node.quantifier,
                variables=renamed_vars,
                formula=walk(node.formula, local_env),
            )
        return node

    return walk(formula, env)


def check_negated_conjecture(
    neg_conj_step: AnnotatedFormula, parent_conj_step: AnnotatedFormula
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

    if neg_conj_step.role != FormulaRole.NEGATED_CONJECTURE:
        issues.append(
            NegatedConjectureIssue(
                name,
                f"step role must be 'negated_conjecture', got '{neg_conj_step.role}'",
            )
        )

    if parent_conj_step.role != FormulaRole.CONJECTURE:
        issues.append(
            NegatedConjectureIssue(
                name,
                f"parent role must be 'conjecture', got '{parent_conj_step.role}'",
            )
        )

    # Check that step has an inference record (negated_conjecture must be derived)
    if neg_conj_step.inference is None:
        issues.append(
            NegatedConjectureIssue(name, "negated_conjecture step must have an inference record")
        )
        return issues

    # Check rule is "negated_conjecture"
    if neg_conj_step.inference.rule != InferenceRule.NEGATED_CONJECTURE:
        issues.append(
            NegatedConjectureIssue(
                name, f"rule must be 'negated_conjecture', got '{neg_conj_step.inference.rule}'"
            )
        )

    # Check status is "cth" (Conjecture THeorem negation)
    if neg_conj_step.inference.status != InferenceStatus.CTH:
        issues.append(
            NegatedConjectureIssue(
                name, f"status must be 'cth', got '{neg_conj_step.inference.status}'"
            )
        )

    # Check that the formula is the correct negation.
    # Some conjectures already start with a leading negation, and their
    # negated_conjecture step is the body with bound variables renamed apart.
    parent_formula = parent_conj_step.formula
    if isinstance(parent_formula, Negation):
        expected_forms = [parent_formula.formula]
        if isinstance(parent_formula.formula, Negation):
            expected_forms.append(parent_formula.formula.formula)
    else:
        expected_forms = [
            _negate_formula(parent_formula),
            Negation(parent_formula),
        ]
        if isinstance(parent_formula, QuantifiedFormula):
            flipped_quantifier = (
                Quantifier.EXISTENTIAL
                if parent_formula.quantifier == Quantifier.UNIVERSAL
                else Quantifier.UNIVERSAL
            )
            expected_forms.append(
                QuantifiedFormula(
                    quantifier=flipped_quantifier,
                    variables=parent_formula.variables,
                    formula=Negation(parent_formula.formula),
                )
            )

    normalized_actual = _clone_with_fresh_bound_vars(neg_conj_step.formula)
    normalized_expected_forms = [_clone_with_fresh_bound_vars(form) for form in expected_forms]

    form_match = any(
        is_alpha_equivalent(normalized_actual, expected_expected)
        for expected_expected in normalized_expected_forms
    )

    if not form_match:
        issues.append(
            NegatedConjectureIssue(
                name,
                f"formula is not the correct negation of parent conjecture; "
                f"expected one of: {expected_forms!r}, got: {neg_conj_step.formula!r}",
            )
        )

    return issues
