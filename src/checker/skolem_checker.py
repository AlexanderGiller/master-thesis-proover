"""Checker for Skolemization in logical formulas."""

from dataclasses import dataclass

from src.checker.alpha_eq import is_alpha_equivalent
from src.parser.ast_nodes import (
    AnnotatedFormula,
    Atom,
    BinaryFormula,
    Equality,
    FunctionTerm,
    InferenceRecord,
    JunctionFormula,
    Negation,
    QuantifiedFormula,
    Variable,
)
from src.var_mapping import FormulaRole, InferenceRule, InferenceStatus, Quantifier


@dataclass
class SkolemizationIssue:
    step_name: str
    reason: str

def _skolem_formula(formula: object, bound_vars: set[str] = None) -> object:
    """Skolemize a formula by replacing a specific existential variable with a provided
    Skolem term. This helper is a generic transformer used by the checker when verifying
    a given skolemization. It does not invent names but performs replacement when the
    existential variable to eliminate is encountered (see `_apply_skolemization`)."""
    # This function is not used in the new checker; leave as passthrough for compatibility
    return formula

def check_skolemization(
    skolem_step: AnnotatedFormula,
    parent_step: AnnotatedFormula
) -> list[SkolemizationIssue]:
    """Check if the skolem_step is a valid Skolemization of the parent_step."""
    issues = []

    # Basic inference record checks
    if skolem_step.inference is None:
        issues.append(SkolemizationIssue(skolem_step.name, "skolemize step must have an inference record"))
        return issues

    inf = skolem_step.inference
    if inf.rule != InferenceRule.SKOLEMIZE:
        issues.append(SkolemizationIssue(skolem_step.name, f"rule must be 'skolemize', got '{inf.rule}'"))

    if inf.status != InferenceStatus.ESA:
        issues.append(SkolemizationIssue(skolem_step.name, f"status must be 'esa', got '{inf.status}'"))

    # new_symbols must be present and introduce exactly one new Skolem symbol
    if not inf.new_symbols or not isinstance(inf.new_symbols, list) or len(inf.new_symbols) != 1:
        issues.append(SkolemizationIssue(skolem_step.name, "skolemize must introduce exactly one new Skolem symbol via new_symbols(skolem, [...])"))
        # Continue checking other issues

    # skolemize information must indicate which variable and the Skolem term
    if not inf.skolem_var:
        issues.append(SkolemizationIssue(skolem_step.name, "skolemize info must indicate the existential variable being eliminated"))
        return issues
    if not inf.skolem_term:
        issues.append(SkolemizationIssue(skolem_step.name, "skolemize info must include the resulting Skolem term"))
        return issues

    # Ensure the introduced skolem symbol matches the skolem term functor
    introduced = inf.new_symbols[0] if inf.new_symbols else None
    sk_term = inf.skolem_term
    if isinstance(sk_term, FunctionTerm):
        sk_functor = sk_term.functor
        if introduced and sk_functor != introduced:
            issues.append(SkolemizationIssue(skolem_step.name, f"Skolem term functor '{sk_functor}' does not match introduced symbol '{introduced}'"))
    else:
        # If skolem term is not a function term, it's invalid
        issues.append(SkolemizationIssue(skolem_step.name, "Skolem term must be a function term with the introduced functor"))

    def replace_vars(node, var_name, skolem_term_obj, bound_universals):
        """Recursively replace occurrences of Variable(var_name) with skolem_term_obj.
        Also track where the existential quantifier was removed to validate dependency."""
        # Atoms
        if isinstance(node, Atom):
            new_args = [replace_vars(a, var_name, skolem_term_obj, bound_universals) for a in node.args]
            return Atom(predicate=node.predicate, args=new_args)
        if isinstance(node, FunctionTerm):
            new_args = [replace_vars(a, var_name, skolem_term_obj, bound_universals) for a in node.args]
            return FunctionTerm(functor=node.functor, args=new_args)
        if isinstance(node, Variable):
            if node.name == var_name:
                return skolem_term_obj
            return Variable(node.name)
        if isinstance(node, Negation):
            return Negation(replace_vars(node.formula, var_name, skolem_term_obj, bound_universals))
        if isinstance(node, BinaryFormula):
            return BinaryFormula(connective=node.connective,
                                 left=replace_vars(node.left, var_name, skolem_term_obj, bound_universals),
                                 right=replace_vars(node.right, var_name, skolem_term_obj, bound_universals))
        if isinstance(node, JunctionFormula):
            return JunctionFormula(connective=node.connective,
                                   operands=[replace_vars(o, var_name, skolem_term_obj, bound_universals) for o in node.operands])
        if isinstance(node, Equality):
            return Equality(left=replace_vars(node.left, var_name, skolem_term_obj, bound_universals),
                            right=replace_vars(node.right, var_name, skolem_term_obj, bound_universals),
                            negated=node.negated)
        if isinstance(node, QuantifiedFormula):
            # Normalize variables to a list (node.variables might be a single string)
            vars_iter = node.variables if isinstance(node.variables, (list, tuple)) else [node.variables]
            # If this quantifier binds the variable we're eliminating, remove that binding
            if node.quantifier == Quantifier.EXISTENTIAL and var_name in vars_iter:
                # The Skolem term must depend exactly on the current bound_universals
                return replace_vars(node.formula, var_name, skolem_term_obj, bound_universals)
            # For universal quantifiers, add bound variables to scope
            if node.quantifier == Quantifier.UNIVERSAL:
                names = {v.name if hasattr(v, 'name') else v for v in vars_iter}
                new_bound = bound_universals.union(names)
                inner = replace_vars(node.formula, var_name, skolem_term_obj, new_bound)
                return QuantifiedFormula(quantifier=Quantifier.UNIVERSAL, variables=list(vars_iter), formula=inner)
            # Existential quantifier not binding the skolem var: keep it
            inner = replace_vars(node.formula, var_name, skolem_term_obj, bound_universals)
            return QuantifiedFormula(quantifier=node.quantifier, variables=list(vars_iter), formula=inner)
        # Unknown node types: return as is
        return node

    # Perform replacement and also capture the universals in scope at the elimination point
    # To validate argument dependency, we need to find the existential quantifier location
    universals_at_elim = None

    def skolemize_and_capture(node, var_name, bound_universals):
        nonlocal universals_at_elim
        if isinstance(node, QuantifiedFormula):
            vars_iter = node.variables if isinstance(node.variables, (list, tuple)) else [node.variables]
            if node.quantifier == "?" and var_name in vars_iter:
                # Capture universals currently in scope
                universals_at_elim = set(bound_universals)
                # Remove var_name from the variables list
                remaining = [v for v in vars_iter if v != var_name]
                inner = replace_vars(node.formula, var_name, sk_term, bound_universals)
                if remaining:
                    return QuantifiedFormula(quantifier="?", variables=list(remaining), formula=inner)
                return inner
            if node.quantifier == Quantifier.UNIVERSAL:
                names = {v.name if hasattr(v, 'name') else v for v in vars_iter}
                new_bound = bound_universals.union(names)
                inner = skolemize_and_capture(node.formula, var_name, new_bound)
                return QuantifiedFormula(quantifier=Quantifier.UNIVERSAL, variables=list(vars_iter), formula=inner)
            # other quantifiers: recurse
            inner = skolemize_and_capture(node.formula, var_name, bound_universals)
            return QuantifiedFormula(quantifier=node.quantifier, variables=list(vars_iter), formula=inner)
        # For other nodes, just replace occurrences
        return replace_vars(node, var_name, sk_term, bound_universals)

    expected = skolemize_and_capture(parent_step.formula, inf.skolem_var, set())

    # If we didn't find the existential in the parent, that's an error
    if universals_at_elim is None:
        issues.append(SkolemizationIssue(skolem_step.name, f"existential variable '{inf.skolem_var}' not found in parent formula"))
        return issues

    # Check that skolem_term depends exactly on universals_at_elim
    if isinstance(sk_term, FunctionTerm):
        arg_vars = [a.name for a in sk_term.args if isinstance(a, Variable)]
        if set(arg_vars) != set(universals_at_elim):
            issues.append(SkolemizationIssue(skolem_step.name, f"Skolem term arguments {arg_vars} do not match universal variables in scope {sorted(universals_at_elim)}"))
    else:
        issues.append(SkolemizationIssue(skolem_step.name, "Skolem term must be a function applied to the universally scoped variables"))

    # Finally, check alpha-equivalence of expected and actual
    if not is_alpha_equivalent(expected, skolem_step.formula):
        issues.append(SkolemizationIssue(skolem_step.name, "The resulting formula is not a correct Skolemization of the parent formula"))

    return issues

