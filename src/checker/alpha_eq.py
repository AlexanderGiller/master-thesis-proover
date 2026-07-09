# alpha_equivalence.py
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


def _alpha_eq(a, b, map1: dict, map2: dict) -> bool:
    if type(a) is not type(b):
        return False

    if isinstance(a, Variable):
        n1, n2 = a.name, b.name
        mapped_to_2 = map1.get(n1)
        mapped_to_1 = map2.get(n2)
        if mapped_to_2 is not None or mapped_to_1 is not None:
            # already bound on at least one side: must agree both ways
            return mapped_to_2 == n2 and mapped_to_1 == n1
        # If neither variable is bound, they must have the same name (for free variables)
        # We only establish new bindings when inside a quantified formula
        if n1 == n2:
            return True
        # Different names, neither bound: not equivalent
        return False

    if isinstance(a, Constant):
        return a.name == b.name

    if isinstance(a, FunctionTerm):
        return (
            a.functor == b.functor
            and len(a.args) == len(b.args)
            and all(_alpha_eq(x, y, map1, map2) for x, y in zip(a.args, b.args))
        )

    if isinstance(a, Atom):
        return (
            a.predicate == b.predicate
            and len(a.args) == len(b.args)
            and all(_alpha_eq(x, y, map1, map2) for x, y in zip(a.args, b.args))
        )

    if isinstance(a, Equality):
        if a.negated != b.negated:
            return False
        return _alpha_eq(a.left, b.left, map1, map2) and _alpha_eq(a.right, b.right, map1, map2)

    if isinstance(a, Negation):
        return _alpha_eq(a.formula, b.formula, map1, map2)

    if isinstance(a, BinaryFormula):
        return (
            a.connective == b.connective
            and _alpha_eq(a.left, b.left, map1, map2)
            and _alpha_eq(a.right, b.right, map1, map2)
        )

    if isinstance(a, JunctionFormula):
        if a.connective != b.connective or len(a.operands) != len(b.operands):
            return False
        # NOTE: order-sensitive. See caveat below.
        return all(_alpha_eq(x, y, map1, map2) for x, y in zip(a.operands, b.operands))

    if isinstance(a, QuantifiedFormula):
        if a.quantifier != b.quantifier or len(a.variables) != len(b.variables):
            return False
        saved = []
        for v1, v2 in zip(a.variables, b.variables):
            saved.append((v1, map1.get(v1, _MISSING), v2, map2.get(v2, _MISSING)))
            map1[v1] = v2
            map2[v2] = v1
        result = _alpha_eq(a.formula, b.formula, map1, map2)
        for v1, old1, v2, old2 in saved:
            if old1 is _MISSING:
                map1.pop(v1, None)
            else:
                map1[v1] = old1
            if old2 is _MISSING:
                map2.pop(v2, None)
            else:
                map2[v2] = old2
        return result

    # numbers, or anything not covered above
    return a == b


def is_alpha_equivalent(f1, f2) -> bool:
    """True if f1 and f2 are identical up to consistent renaming of bound variables.

    Important: This checks true alpha-equivalence according to the standard definition:
    - Bound variables can be renamed consistently (e.g., ![X]: p(X) ≡ ![Y]: p(Y))
    - Constants must be identical (e.g., p(a) ≠ p(b))
    - Free variables must have the same name (e.g., p(X) ≠ p(Y) if neither is bound)

    Example:
    - ![A, B]: (p(A) & ~p(B)) is alpha-equivalent to ![X, Y]: (p(X) & ~p(Y))  ✓
    - p(a) & ~p(b) is NOT alpha-equivalent to p(d) & ~p(e)  ✗
    """
    return _alpha_eq(f1, f2, {}, {})