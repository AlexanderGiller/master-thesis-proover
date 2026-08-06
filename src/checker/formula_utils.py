"""Shared helpers for proof-step formula checks."""

from __future__ import annotations

from copy import deepcopy

from src.parser.ast_nodes import (
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


_MISSING = object()


def flatten_prefix(formula: object, quantifier: object) -> tuple[list[str], object]:
    """Flatten a leading chain of the same quantifier."""
    vars_: list[str] = []
    current = formula
    while isinstance(current, QuantifiedFormula) and current.quantifier == quantifier:
        vars_.extend(str(v) for v in current.variables)
        current = current.formula
    return vars_, current


def substitute_node(node: object, replacements: dict[str, object]) -> object:
    """Substitute variables in a node, respecting quantifier shadowing."""
    if isinstance(node, Variable):
        return replacements.get(node.name, node)
    if isinstance(node, Constant):
        return Constant(node.name)
    if isinstance(node, FunctionTerm):
        return FunctionTerm(
            functor=node.functor,
            args=[substitute_node(arg, replacements) for arg in node.args],
        )
    if isinstance(node, Atom):
        return Atom(predicate=node.predicate, args=[substitute_node(arg, replacements) for arg in node.args])
    if isinstance(node, Equality):
        return Equality(
            left=substitute_node(node.left, replacements),
            right=substitute_node(node.right, replacements),
            negated=node.negated,
        )
    if isinstance(node, Negation):
        return Negation(substitute_node(node.formula, replacements))
    if isinstance(node, BinaryFormula):
        return BinaryFormula(
            connective=node.connective,
            left=substitute_node(node.left, replacements),
            right=substitute_node(node.right, replacements),
        )
    if isinstance(node, JunctionFormula):
        return JunctionFormula(
            connective=node.connective,
            operands=[substitute_node(op, replacements) for op in node.operands],
        )
    if isinstance(node, QuantifiedFormula):
        inner_replacements = {
            name: value for name, value in replacements.items() if name not in set(node.variables)
        }
        return QuantifiedFormula(
            quantifier=node.quantifier,
            variables=list(node.variables),
            formula=substitute_node(node.formula, inner_replacements),
        )
    return deepcopy(node)


def _node_equal(left: object, right: object, bound_map: dict[str, str]) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, Variable):
        mapped = bound_map.get(left.name)
        if mapped is not None:
            return right.name == mapped
        return left.name == right.name
    if isinstance(left, Constant):
        return left.name == right.name
    if isinstance(left, FunctionTerm):
        return left.functor == right.functor and len(left.args) == len(right.args) and all(
            _node_equal(l_arg, r_arg, bound_map) for l_arg, r_arg in zip(left.args, right.args)
        )
    if isinstance(left, Atom):
        return left.predicate == right.predicate and len(left.args) == len(right.args) and all(
            _node_equal(l_arg, r_arg, bound_map) for l_arg, r_arg in zip(left.args, right.args)
        )
    if isinstance(left, Equality):
        return (
            left.negated == right.negated
            and _node_equal(left.left, right.left, bound_map)
            and _node_equal(left.right, right.right, bound_map)
        )
    if isinstance(left, Negation):
        return _node_equal(left.formula, right.formula, bound_map)
    if isinstance(left, BinaryFormula):
        return (
            left.connective == right.connective
            and _node_equal(left.left, right.left, bound_map)
            and _node_equal(left.right, right.right, bound_map)
        )
    if isinstance(left, JunctionFormula):
        return (
            left.connective == right.connective
            and len(left.operands) == len(right.operands)
            and all(_node_equal(l_op, r_op, bound_map) for l_op, r_op in zip(left.operands, right.operands))
        )
    if isinstance(left, QuantifiedFormula):
        if left.quantifier != right.quantifier or len(left.variables) != len(right.variables):
            return False
        new_bound = dict(bound_map)
        for l_var, r_var in zip(left.variables, right.variables):
            new_bound[str(l_var)] = str(r_var)
        return _node_equal(left.formula, right.formula, new_bound)
    return left == right


def match_template_to_instance(
    template: object, instance: object, abstract_vars: set[str], bound_map: dict[str, str] | None = None,
    substitutions: dict[str, object] | None = None,
) -> bool:
    """Check whether template matches instance with some abstract variables allowed."""
    if bound_map is None:
        bound_map = {}
    if substitutions is None:
        substitutions = {}

    if isinstance(template, Variable):
        mapped = bound_map.get(template.name)
        if mapped is not None:
            if not isinstance(instance, Variable):
                return False
            return instance.name == mapped
        if template.name in abstract_vars:
            existing = substitutions.get(template.name)
            if existing is None:
                substitutions[template.name] = instance
                return True
            return _node_equal(existing, instance, bound_map)
        if not isinstance(instance, Variable):
            return False
        return template.name == instance.name

    if type(template) is not type(instance):
        return False

    if isinstance(template, Constant):
        return template.name == instance.name

    if isinstance(template, FunctionTerm):
        return template.functor == instance.functor and len(template.args) == len(instance.args) and all(
            match_template_to_instance(t_arg, i_arg, abstract_vars, bound_map, substitutions)
            for t_arg, i_arg in zip(template.args, instance.args)
        )

    if isinstance(template, Atom):
        return template.predicate == instance.predicate and len(template.args) == len(instance.args) and all(
            match_template_to_instance(t_arg, i_arg, abstract_vars, bound_map, substitutions)
            for t_arg, i_arg in zip(template.args, instance.args)
        )

    if isinstance(template, Equality):
        return (
            template.negated == instance.negated
            and match_template_to_instance(template.left, instance.left, abstract_vars, bound_map, substitutions)
            and match_template_to_instance(template.right, instance.right, abstract_vars, bound_map, substitutions)
        )

    if isinstance(template, Negation):
        return match_template_to_instance(
            template.formula, instance.formula, abstract_vars, bound_map, substitutions
        )

    if isinstance(template, BinaryFormula):
        return (
            template.connective == instance.connective
            and match_template_to_instance(template.left, instance.left, abstract_vars, bound_map, substitutions)
            and match_template_to_instance(template.right, instance.right, abstract_vars, bound_map, substitutions)
        )

    if isinstance(template, JunctionFormula):
        return (
            template.connective == instance.connective
            and len(template.operands) == len(instance.operands)
            and all(
                match_template_to_instance(t_op, i_op, abstract_vars, bound_map, substitutions)
                for t_op, i_op in zip(template.operands, instance.operands)
            )
        )

    if isinstance(template, QuantifiedFormula):
        if template.quantifier != instance.quantifier or len(template.variables) != len(instance.variables):
            return False
        new_bound = dict(bound_map)
        for t_var, i_var in zip(template.variables, instance.variables):
            new_bound[str(t_var)] = str(i_var)
        return match_template_to_instance(
            template.formula, instance.formula, abstract_vars, new_bound, substitutions
        )

    return template == instance
