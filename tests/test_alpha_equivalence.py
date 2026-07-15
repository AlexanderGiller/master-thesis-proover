# tests/test_alpha_equivalence.py
"""Tests for alpha-equivalence checking."""

from src.checker.alpha_eq import is_alpha_equivalent
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
from src.var_mapping import (
    BinaryConnective,
    FormulaRole,
    InferenceRule,
    InferenceStatus,
    Quantifier,
)


class TestAlphaEquivalenceBasics:
    """Test basic alpha-equivalence cases."""

    def test_same_variable_is_equivalent(self):
        """Two identical variables should be equivalent."""
        v1 = Variable("X")
        v2 = Variable("X")
        assert is_alpha_equivalent(v1, v2)

    def test_different_variables_not_equivalent(self):
        """Different variables should not be equivalent."""
        v1 = Variable("X")
        v2 = Variable("Y")
        assert not is_alpha_equivalent(v1, v2)

    def test_same_constant_is_equivalent(self):
        """Two identical constants should be equivalent."""
        c1 = Constant("a")
        c2 = Constant("a")
        assert is_alpha_equivalent(c1, c2)

    def test_different_constants_not_equivalent(self):
        """Different constants should not be equivalent."""
        c1 = Constant("a")
        c2 = Constant("b")
        assert not is_alpha_equivalent(c1, c2)

    def test_type_mismatch_not_equivalent(self):
        """Different types should not be equivalent."""
        v = Variable("X")
        c = Constant("X")
        assert not is_alpha_equivalent(v, c)


class TestAlphaEquivalenceAtoms:
    """Test alpha-equivalence for atomic formulas."""

    def test_same_atom_is_equivalent(self):
        """Two identical atoms should be equivalent."""
        a1 = Atom("p", args=[])
        a2 = Atom("p", args=[])
        assert is_alpha_equivalent(a1, a2)

    def test_different_predicates_not_equivalent(self):
        """Atoms with different predicates should not be equivalent."""
        a1 = Atom("p", args=[])
        a2 = Atom("q", args=[])
        assert not is_alpha_equivalent(a1, a2)

    def test_atom_with_constant_arg(self):
        """Atoms with constant arguments."""
        a1 = Atom("p", args=[Constant("a")])
        a2 = Atom("p", args=[Constant("a")])
        assert is_alpha_equivalent(a1, a2)

    def test_atom_with_variable_args_same_names(self):
        """Atoms with variables of same name should be equivalent."""
        a1 = Atom("p", args=[Variable("X"), Variable("Y")])
        a2 = Atom("p", args=[Variable("X"), Variable("Y")])
        assert is_alpha_equivalent(a1, a2)

    def test_atom_with_variable_args_different_names(self):
        """Atoms with different variable names should not be equivalent
        (when comparing free variables)."""
        a1 = Atom("p", args=[Variable("X")])
        a2 = Atom("p", args=[Variable("Y")])
        # Free variables with different names are NOT equivalent
        assert not is_alpha_equivalent(a1, a2)

    def test_atom_with_multiple_args(self):
        """Atoms with multiple arguments."""
        a1 = Atom("p", args=[Constant("a"), Variable("X"), Constant("b")])
        a2 = Atom("p", args=[Constant("a"), Variable("X"), Constant("b")])
        assert is_alpha_equivalent(a1, a2)

    def test_atom_different_arg_count(self):
        """Atoms with different argument counts should not be equivalent."""
        a1 = Atom("p", args=[Constant("a")])
        a2 = Atom("p", args=[Constant("a"), Constant("b")])
        assert not is_alpha_equivalent(a1, a2)


class TestAlphaEquivalenceFunctionTerms:
    """Test alpha-equivalence for function terms."""

    def test_same_function_term_is_equivalent(self):
        """Two identical function terms should be equivalent."""
        f1 = FunctionTerm("f", [Constant("a")])
        f2 = FunctionTerm("f", [Constant("a")])
        assert is_alpha_equivalent(f1, f2)

    def test_different_functors_not_equivalent(self):
        """Function terms with different functors should not be equivalent."""
        f1 = FunctionTerm("f", [Constant("a")])
        f2 = FunctionTerm("g", [Constant("a")])
        assert not is_alpha_equivalent(f1, f2)

    def test_nested_function_terms(self):
        """Nested function terms should be compared recursively."""
        f1 = FunctionTerm("f", [FunctionTerm("g", [Constant("a")])])
        f2 = FunctionTerm("f", [FunctionTerm("g", [Constant("a")])])
        assert is_alpha_equivalent(f1, f2)

    def test_nested_function_different_inner(self):
        """Nested function terms with different inner values."""
        f1 = FunctionTerm("f", [FunctionTerm("g", [Constant("a")])])
        f2 = FunctionTerm("f", [FunctionTerm("g", [Constant("b")])])
        assert not is_alpha_equivalent(f1, f2)


class TestAlphaEquivalenceEquality:
    """Test alpha-equivalence for equality formulas."""

    def test_same_equality_is_equivalent(self):
        """Two identical equalities should be equivalent."""
        e1 = Equality(Constant("a"), Constant("b"))
        e2 = Equality(Constant("a"), Constant("b"))
        assert is_alpha_equivalent(e1, e2)

    def test_negated_equality_equivalence(self):
        """Negated equalities should match on negation flag."""
        e1 = Equality(Constant("a"), Constant("b"), negated=True)
        e2 = Equality(Constant("a"), Constant("b"), negated=True)
        assert is_alpha_equivalent(e1, e2)

    def test_negated_vs_non_negated_not_equivalent(self):
        """Negated and non-negated equalities should not be equivalent."""
        e1 = Equality(Constant("a"), Constant("b"), negated=False)
        e2 = Equality(Constant("a"), Constant("b"), negated=True)
        assert not is_alpha_equivalent(e1, e2)

    def test_swapped_equality_not_equivalent(self):
        """Equalities with swapped sides should not be equivalent."""
        e1 = Equality(Constant("a"), Constant("b"))
        e2 = Equality(Constant("b"), Constant("a"))
        assert not is_alpha_equivalent(e1, e2)


class TestAlphaEquivalenceNegation:
    """Test alpha-equivalence for negation."""

    def test_same_negation_is_equivalent(self):
        """Two identical negations should be equivalent."""
        n1 = Negation(Atom("p", args=[]))
        n2 = Negation(Atom("p", args=[]))
        assert is_alpha_equivalent(n1, n2)

    def test_different_negated_formulas_not_equivalent(self):
        """Negations of different formulas should not be equivalent."""
        n1 = Negation(Atom("p", args=[]))
        n2 = Negation(Atom("q", args=[]))
        assert not is_alpha_equivalent(n1, n2)


class TestAlphaEquivalenceBinaryFormulas:
    """Test alpha-equivalence for binary formulas."""

    def test_same_binary_formula_is_equivalent(self):
        """Two identical binary formulas should be equivalent."""
        b1 = BinaryFormula(BinaryConnective.IMPLIES, Atom("p", args=[]), Atom("q", args=[]))
        b2 = BinaryFormula(BinaryConnective.IMPLIES, Atom("p", args=[]), Atom("q", args=[]))
        assert is_alpha_equivalent(b1, b2)

    def test_different_connectives_not_equivalent(self):
        """Binary formulas with different connectives should not be equivalent."""
        b1 = BinaryFormula(BinaryConnective.IMPLIES, Atom("p", args=[]), Atom("q", args=[]))
        b2 = BinaryFormula(BinaryConnective.IFF, Atom("p", args=[]), Atom("q", args=[]))
        assert not is_alpha_equivalent(b1, b2)

    def test_swapped_binary_operands_not_equivalent(self):
        """Binary formulas with swapped operands should not be equivalent."""
        b1 = BinaryFormula(BinaryConnective.IMPLIES, Atom("p", args=[]), Atom("q", args=[]))
        b2 = BinaryFormula(BinaryConnective.IMPLIES, Atom("q", args=[]), Atom("p", args=[]))
        assert not is_alpha_equivalent(b1, b2)


class TestAlphaEquivalenceJunctionFormulas:
    """Test alpha-equivalence for junction formulas (AND/OR)."""

    def test_same_and_formula_is_equivalent(self):
        """Two identical AND formulas should be equivalent."""
        j1 = JunctionFormula(BinaryConnective.AND, [Atom("p", args=[]), Atom("q", args=[])])
        j2 = JunctionFormula(BinaryConnective.AND, [Atom("p", args=[]), Atom("q", args=[])])
        assert is_alpha_equivalent(j1, j2)

    def test_or_formula_equivalence(self):
        """Two identical OR formulas should be equivalent."""
        j1 = JunctionFormula(BinaryConnective.OR, [Atom("p", args=[]), Atom("q", args=[])])
        j2 = JunctionFormula(BinaryConnective.OR, [Atom("p", args=[]), Atom("q", args=[])])
        assert is_alpha_equivalent(j1, j2)

    def test_different_connectives_not_equivalent(self):
        """Junction formulas with different connectives should not be equivalent."""
        j1 = JunctionFormula(BinaryConnective.AND, [Atom("p", args=[]), Atom("q", args=[])])
        j2 = JunctionFormula(BinaryConnective.OR, [Atom("p", args=[]), Atom("q", args=[])])
        assert not is_alpha_equivalent(j1, j2)

    def test_swapped_operands_not_equivalent(self):
        """Junction formulas with swapped operands should not be equivalent
        (order is significant)."""
        j1 = JunctionFormula(BinaryConnective.AND, [Atom("p", args=[]), Atom("q", args=[])])
        j2 = JunctionFormula(BinaryConnective.AND, [Atom("q", args=[]), Atom("p", args=[])])
        assert not is_alpha_equivalent(j1, j2)

    def test_different_operand_count_not_equivalent(self):
        """Junction formulas with different number of operands should not be equivalent."""
        j1 = JunctionFormula(BinaryConnective.AND, [Atom("p", args=[]), Atom("q", args=[])])
        j2 = JunctionFormula(
            BinaryConnective.AND, [Atom("p", args=[]), Atom("q", args=[]), Atom("r", args=[])]
        )
        assert not is_alpha_equivalent(j1, j2)


class TestAlphaEquivalenceQuantifiedFormulas:
    """Test alpha-equivalence for quantified formulas."""

    def test_same_quantified_formula_is_equivalent(self):
        """Two identical quantified formulas should be equivalent."""
        q1 = QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], Atom("p", args=[Variable("X")]))
        q2 = QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], Atom("p", args=[Variable("X")]))
        assert is_alpha_equivalent(q1, q2)

    def test_different_quantifiers_not_equivalent(self):
        """Quantified formulas with different quantifiers should not be equivalent."""
        q1 = QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], Atom("p", args=[Variable("X")]))
        q2 = QuantifiedFormula(Quantifier.EXISTENTIAL, ["X"], Atom("p", args=[Variable("X")]))
        assert not is_alpha_equivalent(q1, q2)

    def test_renamed_bound_variable_is_equivalent(self):
        """Renamed bound variables should be considered equivalent (alpha-equivalence)."""
        # ![X]: p(X) should be equivalent to ![Y]: p(Y)
        q1 = QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], Atom("p", args=[Variable("X")]))
        q2 = QuantifiedFormula(Quantifier.UNIVERSAL, ["Y"], Atom("p", args=[Variable("Y")]))
        assert is_alpha_equivalent(q1, q2)

    def test_renamed_multiple_bound_variables_is_equivalent(self):
        """Multiple renamed bound variables should be equivalent."""
        # ![X,Y]: p(X,Y) should be equivalent to ![A,B]: p(A,B)
        q1 = QuantifiedFormula(
            Quantifier.UNIVERSAL, ["X", "Y"], Atom("p", args=[Variable("X"), Variable("Y")])
        )
        q2 = QuantifiedFormula(
            Quantifier.UNIVERSAL, ["A", "B"], Atom("p", args=[Variable("A"), Variable("B")])
        )
        assert is_alpha_equivalent(q1, q2)

    def test_reordered_bound_variables_is_equivalent(self):
        """Reordered bound variables of the same quantifier type are equivalent.
        ![X, Y]: p(X, Y) is alpha-equivalent to ![Y, X]: p(Y, X) because
        we can rename X->Y, Y->X to get from one to the other."""
        q1 = QuantifiedFormula(
            Quantifier.UNIVERSAL, ["X", "Y"], Atom("p", args=[Variable("X"), Variable("Y")])
        )
        q2 = QuantifiedFormula(
            Quantifier.UNIVERSAL, ["Y", "X"], Atom("p", args=[Variable("Y"), Variable("X")])
        )
        assert is_alpha_equivalent(q1, q2)

    def test_partial_renaming_different_body(self):
        """Partial renaming with different body should not be equivalent."""
        q1 = QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], Atom("p", args=[Variable("X")]))
        q2 = QuantifiedFormula(Quantifier.UNIVERSAL, ["Y"], Atom("q", args=[Variable("Y")]))
        assert not is_alpha_equivalent(q1, q2)

    def test_nested_quantifiers_with_renaming(self):
        """Nested quantifiers with renaming should be equivalent."""
        # ![X]: ?[Y]: p(X,Y) equivalent to ![A]: ?[B]: p(A,B)
        inner1 = QuantifiedFormula(
            Quantifier.EXISTENTIAL, ["Y"], Atom("p", args=[Variable("X"), Variable("Y")])
        )
        outer1 = QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], inner1)

        inner2 = QuantifiedFormula(
            Quantifier.EXISTENTIAL, ["B"], Atom("p", args=[Variable("A"), Variable("B")])
        )
        outer2 = QuantifiedFormula(Quantifier.UNIVERSAL, ["A"], inner2)

        assert is_alpha_equivalent(outer1, outer2)

    def test_nested_quantifiers_different_nesting_not_equivalent(self):
        """Nested quantifiers with different nesting order should not be equivalent."""
        # ![X]: ?[Y]: p(X,Y) NOT equivalent to ?[X]: ![Y]: p(X,Y)
        inner1 = QuantifiedFormula(
            Quantifier.EXISTENTIAL, ["Y"], Atom("p", args=[Variable("X"), Variable("Y")])
        )
        outer1 = QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], inner1)

        inner2 = QuantifiedFormula(
            Quantifier.UNIVERSAL, ["Y"], Atom("p", args=[Variable("X"), Variable("Y")])
        )
        outer2 = QuantifiedFormula(Quantifier.EXISTENTIAL, ["X"], inner2)

        assert not is_alpha_equivalent(outer1, outer2)


class TestAlphaEquivalenceComplex:
    """Test alpha-equivalence for complex formulas."""

    def test_from_axiom_checker_example(self):
        """Test with the formula from axiom_checker: p(a) & ~p(b)"""
        # p(a) & ~p(b)
        formula1 = JunctionFormula(
            BinaryConnective.AND,
            [Atom("p", args=[Constant("a")]), Negation(Atom("p", args=[Constant("b")]))],
        )

        # Same formula
        formula2 = JunctionFormula(
            BinaryConnective.AND,
            [Atom("p", args=[Constant("a")]), Negation(Atom("p", args=[Constant("b")]))],
        )

        assert is_alpha_equivalent(formula1, formula2)

    def test_complex_quantified_with_implications(self):
        """Complex formula: ?[X]: (p(X) => q(X))"""
        inner = BinaryFormula(
            BinaryConnective.IMPLIES,
            Atom("p", args=[Variable("X")]),
            Atom("q", args=[Variable("X")]),
        )
        q1 = QuantifiedFormula(Quantifier.EXISTENTIAL, ["X"], inner)

        inner2 = BinaryFormula(
            BinaryConnective.IMPLIES,
            Atom("p", args=[Variable("Y")]),
            Atom("q", args=[Variable("Y")]),
        )
        q2 = QuantifiedFormula(Quantifier.EXISTENTIAL, ["Y"], inner2)

        assert is_alpha_equivalent(q1, q2)

    def test_shadowing_variables_correctly_handled(self):
        """Test that shadowing of variables is correctly handled.
        ![X]: (p(X) | ?[X]: q(X)) should be equivalent to ![A]: (p(A) | ?[B]: q(B))
        """
        inner_q = QuantifiedFormula(Quantifier.EXISTENTIAL, ["X"], Atom("q", args=[Variable("X")]))
        outer1 = QuantifiedFormula(
            Quantifier.UNIVERSAL,
            ["X"],
            JunctionFormula(BinaryConnective.OR, [Atom("p", args=[Variable("X")]), inner_q]),
        )

        inner_q2 = QuantifiedFormula(Quantifier.EXISTENTIAL, ["B"], Atom("q", args=[Variable("B")]))
        outer2 = QuantifiedFormula(
            Quantifier.UNIVERSAL,
            ["A"],
            JunctionFormula(BinaryConnective.OR, [Atom("p", args=[Variable("A")]), inner_q2]),
        )

        assert is_alpha_equivalent(outer1, outer2)
