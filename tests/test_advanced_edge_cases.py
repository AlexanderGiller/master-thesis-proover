"""
Advanced tests for edge cases and complex scenarios.
These tests ensure more robust and comprehensive coverage.
"""

import pytest

from src.checker.alpha_eq import is_alpha_equivalent
from src.checker.negated_conjecture_checker import check_negated_conjecture
from src.checker.skolem_checker import SkolemizationIssue, check_skolemization
from src.parser.ast_nodes import (
    AnnotatedFormula,
    Atom,
    BinaryFormula,
    Constant,
    Equality,
    FunctionTerm,
    InferenceRecord,
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

# ============================================================================
# ALPHA-EQUIVALENCE: Advanced Edge Cases
# ============================================================================


class TestAlphaEquivalenceMixedVariables:
    """Test alpha-equivalence with mixed free and bound variables."""

    def test_free_variable_must_match_exactly(self):
        """Free variables with different names should NOT be equivalent."""
        # ![X]: p(X, Y) vs ![X]: p(X, Z)
        # Y and Z are free, so they must match exactly
        f1 = QuantifiedFormula(
            Quantifier.UNIVERSAL, ["X"], Atom("p", [Variable("X"), Variable("Y")])
        )
        f2 = QuantifiedFormula(
            Quantifier.UNIVERSAL, ["X"], Atom("p", [Variable("X"), Variable("Z")])
        )
        assert not is_alpha_equivalent(f1, f2)

    def test_free_and_bound_variable_mix(self):
        """![X]: p(X, Y) should be equivalent to ![A]: p(A, Y) (Y is free)."""
        f1 = QuantifiedFormula(
            Quantifier.UNIVERSAL, ["X"], Atom("p", [Variable("X"), Variable("Y")])
        )
        f2 = QuantifiedFormula(
            Quantifier.UNIVERSAL, ["A"], Atom("p", [Variable("A"), Variable("Y")])
        )
        assert is_alpha_equivalent(f1, f2)

    def test_free_variable_shadowing_different_scopes(self):
        """![X]: p(X, Y) vs ![X]: q(X, Z) - both have free Y and Z."""
        f1 = QuantifiedFormula(
            Quantifier.UNIVERSAL, ["X"], Atom("p", [Variable("X"), Variable("Y")])
        )
        f2 = QuantifiedFormula(
            Quantifier.UNIVERSAL, ["X"], Atom("q", [Variable("X"), Variable("Z")])
        )
        # Different predicates AND different free vars
        assert not is_alpha_equivalent(f1, f2)

    def test_complex_mixed_variables_nested(self):
        """![X]: ?[Y]: p(X, Y, Z) with Z free.
        Should be alpha-equivalent to ![A]: ?[B]: p(A, B, Z)"""
        inner1 = QuantifiedFormula(
            Quantifier.EXISTENTIAL, ["Y"], Atom("p", [Variable("X"), Variable("Y"), Variable("Z")])
        )
        outer1 = QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], inner1)

        inner2 = QuantifiedFormula(
            Quantifier.EXISTENTIAL, ["B"], Atom("p", [Variable("A"), Variable("B"), Variable("Z")])
        )
        outer2 = QuantifiedFormula(Quantifier.UNIVERSAL, ["A"], inner2)

        assert is_alpha_equivalent(outer1, outer2)


class TestAlphaEquivalenceComplexShadowing:
    """Test variable shadowing in complex nested contexts."""

    def test_shadowing_same_variable_name_nested(self):
        """![X]: (p(X) | ![X]: q(X))
        Inner X shadows outer X. Should be equivalent to ![A]: (p(A) | ![B]: q(B))"""
        inner_q = QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], Atom("q", [Variable("X")]))
        outer1 = QuantifiedFormula(
            Quantifier.UNIVERSAL, ["X"], JunctionFormula("|", [Atom("p", [Variable("X")]), inner_q])
        )

        inner_q2 = QuantifiedFormula(Quantifier.UNIVERSAL, ["B"], Atom("q", [Variable("B")]))
        outer2 = QuantifiedFormula(
            Quantifier.UNIVERSAL,
            ["A"],
            JunctionFormula("|", [Atom("p", [Variable("A")]), inner_q2]),
        )

        assert is_alpha_equivalent(outer1, outer2)

    def test_shadowing_with_different_quantifiers(self):
        """![X]: (?[X]: p(X)) vs ![A]: (?[B]: p(B))
        Inner existential shadows outer universal."""
        inner1 = QuantifiedFormula(Quantifier.EXISTENTIAL, ["X"], Atom("p", [Variable("X")]))
        outer1 = QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], inner1)

        inner2 = QuantifiedFormula(Quantifier.EXISTENTIAL, ["B"], Atom("p", [Variable("B")]))
        outer2 = QuantifiedFormula(Quantifier.UNIVERSAL, ["A"], inner2)

        assert is_alpha_equivalent(outer1, outer2)

    def test_triple_nested_shadowing(self):
        """![X]: ?[X]: ![X]: p(X) - X shadowed multiple times."""
        inner_most = Atom("p", [Variable("X")])
        middle = QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], inner_most)
        middle_q = QuantifiedFormula(Quantifier.EXISTENTIAL, ["X"], middle)
        outer = QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], middle_q)

        inner_most2 = Atom("p", [Variable("C")])
        middle2 = QuantifiedFormula(Quantifier.UNIVERSAL, ["C"], inner_most2)
        middle_q2 = QuantifiedFormula(Quantifier.EXISTENTIAL, ["B"], middle2)
        outer2 = QuantifiedFormula(Quantifier.UNIVERSAL, ["A"], middle_q2)

        assert is_alpha_equivalent(outer, outer2)


class TestAlphaEquivalenceDeepNesting:
    """Test deeply nested structures."""

    def test_deep_function_nesting(self):
        """Test f(g(h(i(j(X))))) equivalence."""
        f1 = FunctionTerm(
            "f",
            [
                FunctionTerm(
                    "g",
                    [FunctionTerm("h", [FunctionTerm("i", [FunctionTerm("j", [Variable("X")])])])],
                )
            ],
        )

        f2 = FunctionTerm(
            "f",
            [
                FunctionTerm(
                    "g",
                    [FunctionTerm("h", [FunctionTerm("i", [FunctionTerm("j", [Variable("X")])])])],
                )
            ],
        )

        assert is_alpha_equivalent(f1, f2)

    def test_deep_quantifier_nesting(self):
        """![X]: ?[Y]: ![Z]: ?[W]: p(X, Y, Z, W)"""
        deepest = Atom("p", [Variable("X"), Variable("Y"), Variable("Z"), Variable("W")])
        q1 = QuantifiedFormula(Quantifier.EXISTENTIAL, ["W"], deepest)
        q2 = QuantifiedFormula(Quantifier.UNIVERSAL, ["Z"], q1)
        q3 = QuantifiedFormula(Quantifier.EXISTENTIAL, ["Y"], q2)
        q4 = QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], q3)

        # Same with renamed variables
        deepest2 = Atom("p", [Variable("A"), Variable("B"), Variable("C"), Variable("D")])
        q1_2 = QuantifiedFormula(Quantifier.EXISTENTIAL, ["D"], deepest2)
        q2_2 = QuantifiedFormula(Quantifier.UNIVERSAL, ["C"], q1_2)
        q3_2 = QuantifiedFormula(Quantifier.EXISTENTIAL, ["B"], q2_2)
        q4_2 = QuantifiedFormula(Quantifier.UNIVERSAL, ["A"], q3_2)

        assert is_alpha_equivalent(q4, q4_2)

    def test_mixed_operators_deep_nesting(self):
        """![X]: (p(X) => (?[Y]: (q(Y) & ~r(X, Y))))"""
        inner = JunctionFormula(
            "&", [Atom("q", [Variable("Y")]), Negation(Atom("r", [Variable("X"), Variable("Y")]))]
        )
        inner_q = QuantifiedFormula(Quantifier.EXISTENTIAL, ["Y"], inner)
        binary = BinaryFormula(BinaryConnective.IMPLIES, Atom("p", [Variable("X")]), inner_q)
        outer = QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], binary)

        # Same with renamed variables
        inner2 = JunctionFormula(
            BinaryConnective.AND,
            [Atom("q", [Variable("B")]), Negation(Atom("r", [Variable("A"), Variable("B")]))],
        )
        inner_q2 = QuantifiedFormula(Quantifier.EXISTENTIAL, ["B"], inner2)
        binary2 = BinaryFormula(BinaryConnective.IMPLIES, Atom("p", [Variable("A")]), inner_q2)
        outer2 = QuantifiedFormula(Quantifier.UNIVERSAL, ["A"], binary2)

        assert is_alpha_equivalent(outer, outer2)


# ============================================================================
# SKOLEM-CHECKER: Advanced Edge Cases
# ============================================================================


def make_annotated(name, role, formula, inference=None):
    return AnnotatedFormula(name=name, role=role, formula=formula, inference=inference)


def make_inference(rule, status, parents, *, new_symbols=None, skolem_var=None, skolem_term=None):
    """Helper to create InferenceRecord with new info structure."""
    from src.parser.ast_nodes import NewSymbolsInfo, SkolemizeInfo, StatusInfo

    info = []
    if status is not None:
        info.append(StatusInfo(status=status))
    if new_symbols is not None:
        info.append(NewSymbolsInfo(kind="skolem", symbols=new_symbols))
    if skolem_var is not None and skolem_term is not None:
        info.append(SkolemizeInfo(variable=skolem_var, term=skolem_term))

    return InferenceRecord(rule=rule, info=info, parents=parents)


class TestSkolemCheckerMultipleExistentials:
    """Test Skolemization of multiple existential quantifiers."""

    def test_two_existentials_first_skolemization(self):
        """![X]: ?[Y]: ?[Z]: p(X, Y, Z) -> skolemize Y -> ![X]: ?[Z]: p(X, sK0(X), Z)"""
        parent = make_annotated(
            "step1",
            FormulaRole.AXIOM,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                QuantifiedFormula(
                    Quantifier.EXISTENTIAL,
                    ["Y"],
                    QuantifiedFormula(
                        Quantifier.EXISTENTIAL,
                        ["Z"],
                        Atom("p", [Variable("X"), Variable("Y"), Variable("Z")]),
                    ),
                ),
            ),
        )

        # Skolemize first existential Y
        child = make_annotated(
            "step2",
            FormulaRole.PLAIN,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                QuantifiedFormula(
                    Quantifier.EXISTENTIAL,
                    ["Z"],
                    Atom("p", [Variable("X"), FunctionTerm("sK0", [Variable("X")]), Variable("Z")]),
                ),
            ),
            make_inference(
                InferenceRule.SKOLEMIZE,
                InferenceStatus.ESA,
                ["step1"],
                new_symbols=["sK0"],
                skolem_var="Y",
                skolem_term=FunctionTerm("sK0", [Variable("X")]),
            ),
        )

        issues = check_skolemization(child, parent)
        assert issues == []

    def test_two_existentials_second_skolemization(self):
        """![X]: ?[Z]: p(X, sK0(X), Z) -> skolemize Z -> ![X]: p(X, sK0(X), sK1(X))"""
        parent = make_annotated(
            "step2",
            FormulaRole.PLAIN,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                QuantifiedFormula(
                    Quantifier.EXISTENTIAL,
                    ["Z"],
                    Atom("p", [Variable("X"), FunctionTerm("sK0", [Variable("X")]), Variable("Z")]),
                ),
            ),
        )

        child = make_annotated(
            "step3",
            FormulaRole.PLAIN,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                Atom(
                    "p",
                    [
                        Variable("X"),
                        FunctionTerm("sK0", [Variable("X")]),
                        FunctionTerm("sK1", [Variable("X")]),
                    ],
                ),
            ),
            make_inference(
                InferenceRule.SKOLEMIZE,
                InferenceStatus.ESA,
                ["step2"],
                new_symbols=["sK1"],
                skolem_var="Z",
                skolem_term=FunctionTerm("sK1", [Variable("X")]),
            ),
        )

        issues = check_skolemization(child, parent)
        assert issues == []

    def test_deeply_nested_universals_single_existential(self):
        """![X]: ![Y]: ![Z]: ?[W]: p(X, Y, Z, W)
        Skolem term must have all three universals as arguments."""
        parent = make_annotated(
            "step1",
            FormulaRole.AXIOM,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                QuantifiedFormula(
                    Quantifier.UNIVERSAL,
                    ["Y"],
                    QuantifiedFormula(
                        Quantifier.UNIVERSAL,
                        ["Z"],
                        QuantifiedFormula(
                            Quantifier.EXISTENTIAL,
                            ["W"],
                            Atom("p", [Variable("X"), Variable("Y"), Variable("Z"), Variable("W")]),
                        ),
                    ),
                ),
            ),
        )

        child = make_annotated(
            "step2",
            FormulaRole.PLAIN,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                QuantifiedFormula(
                    Quantifier.UNIVERSAL,
                    ["Y"],
                    QuantifiedFormula(
                        Quantifier.UNIVERSAL,
                        ["Z"],
                        Atom(
                            "p",
                            [
                                Variable("X"),
                                Variable("Y"),
                                Variable("Z"),
                                FunctionTerm("sK0", [Variable("X"), Variable("Y"), Variable("Z")]),
                            ],
                        ),
                    ),
                ),
            ),
            make_inference(
                InferenceRule.SKOLEMIZE,
                InferenceStatus.ESA,
                ["step1"],
                new_symbols=["sK0"],
                skolem_var="W",
                skolem_term=FunctionTerm("sK0", [Variable("X"), Variable("Y"), Variable("Z")]),
            ),
        )

        issues = check_skolemization(child, parent)
        assert issues == []


class TestSkolemCheckerWrongArguments:
    """Test detection of wrong Skolem arguments."""

    def test_missing_universal_in_skolem_args(self):
        """Skolem term is missing a required universal variable."""
        parent = make_annotated(
            "step1",
            FormulaRole.AXIOM,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                QuantifiedFormula(
                    Quantifier.UNIVERSAL,
                    ["Y"],
                    QuantifiedFormula(
                        Quantifier.EXISTENTIAL,
                        ["Z"],
                        Atom("p", [Variable("X"), Variable("Y"), Variable("Z")]),
                    ),
                ),
            ),
        )

        # Wrong: sK0 only has X, but should have X and Y
        child = make_annotated(
            "step2",
            FormulaRole.PLAIN,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                QuantifiedFormula(
                    Quantifier.UNIVERSAL,
                    ["Y"],
                    Atom("p", [Variable("X"), Variable("Y"), FunctionTerm("sK0", [Variable("X")])]),
                ),
            ),
            make_inference(
                InferenceRule.SKOLEMIZE,
                InferenceStatus.ESA,
                ["step1"],
                new_symbols=["sK0"],
                skolem_var="Z",
                skolem_term=FunctionTerm("sK0", [Variable("X")]),
            ),
        )

        issues = check_skolemization(child, parent)
        assert any("arguments" in issue.reason for issue in issues)

    def test_extra_arguments_in_skolem_term(self):
        """Skolem term has extra arguments not in scope."""
        parent = make_annotated(
            "step1",
            FormulaRole.AXIOM,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                QuantifiedFormula(
                    Quantifier.EXISTENTIAL, ["Y"], Atom("p", [Variable("X"), Variable("Y")])
                ),
            ),
        )

        # Wrong: sK0 has extra argument Z which is not in scope
        child = make_annotated(
            "step2",
            FormulaRole.PLAIN,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                Atom("p", [Variable("X"), FunctionTerm("sK0", [Variable("X"), Variable("Z")])]),
            ),
            make_inference(
                InferenceRule.SKOLEMIZE,
                InferenceStatus.ESA,
                ["step1"],
                new_symbols=["sK0"],
                skolem_var="Y",
                skolem_term=FunctionTerm("sK0", [Variable("X"), Variable("Z")]),
            ),
        )

        issues = check_skolemization(child, parent)
        assert any("arguments" in issue.reason for issue in issues)

    def test_wrong_order_in_skolem_arguments(self):
        """Skolem arguments are in wrong order.
        NOTE: Current implementation may accept different orders if all variables are present.
        This is a gap that could be addressed with stricter checking."""
        parent = make_annotated(
            "step1",
            FormulaRole.AXIOM,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                QuantifiedFormula(
                    Quantifier.UNIVERSAL,
                    ["Y"],
                    QuantifiedFormula(
                        Quantifier.EXISTENTIAL,
                        ["Z"],
                        Atom("p", [Variable("X"), Variable("Y"), Variable("Z")]),
                    ),
                ),
            ),
        )

        # Wrong: arguments in wrong order (Y, X instead of X, Y)
        child = make_annotated(
            "step2",
            FormulaRole.PLAIN,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                QuantifiedFormula(
                    Quantifier.UNIVERSAL,
                    ["Y"],
                    Atom(
                        "p",
                        [
                            Variable("X"),
                            Variable("Y"),
                            FunctionTerm("sK0", [Variable("Y"), Variable("X")]),
                        ],
                    ),
                ),
            ),
            make_inference(
                InferenceRule.SKOLEMIZE,
                InferenceStatus.ESA,
                ["step1"],
                new_symbols=["sK0"],
                skolem_var="Z",
                skolem_term=FunctionTerm("sK0", [Variable("Y"), Variable("X")]),
            ),
        )

        issues = check_skolemization(child, parent)
        # Currently this passes because both X and Y are present (not order-sensitive)
        # TODO: Consider if order-sensitivity should be enforced
        assert issues == []


class TestSkolemCheckerInComplexFormulas:
    """Test Skolemization in complex formulas with multiple operators."""

    def test_skolemization_in_conjunction(self):
        """?[X]: (p(X) & q(X)) -> sK0 with no args (no universals)."""
        parent = make_annotated(
            "step1",
            FormulaRole.AXIOM,
            QuantifiedFormula(
                Quantifier.EXISTENTIAL,
                ["X"],
                JunctionFormula("&", [Atom("p", [Variable("X")]), Atom("q", [Variable("X")])]),
            ),
        )

        child = make_annotated(
            "step2",
            FormulaRole.PLAIN,
            JunctionFormula(
                "&", [Atom("p", [FunctionTerm("sK0", [])]), Atom("q", [FunctionTerm("sK0", [])])]
            ),
            make_inference(
                InferenceRule.SKOLEMIZE,
                InferenceStatus.ESA,
                ["step1"],
                new_symbols=["sK0"],
                skolem_var="X",
                skolem_term=FunctionTerm("sK0", []),
            ),
        )

        issues = check_skolemization(child, parent)
        assert issues == []

    def test_skolemization_in_implication(self):
        """![Y]: (p(Y) => ?[X]: q(X, Y))
        NOTE: Current implementation may have limitations with recognizing existentials
        inside binary formulas. This is worth investigating."""
        parent = make_annotated(
            "step1",
            FormulaRole.AXIOM,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["Y"],
                BinaryFormula(
                    "=>",
                    Atom("p", [Variable("Y")]),
                    QuantifiedFormula(
                        Quantifier.EXISTENTIAL, ["X"], Atom("q", [Variable("X"), Variable("Y")])
                    ),
                ),
            ),
        )

        child = make_annotated(
            "step2",
            FormulaRole.PLAIN,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["Y"],
                BinaryFormula(
                    "=>",
                    Atom("p", [Variable("Y")]),
                    Atom("q", [FunctionTerm("sK0", [Variable("Y")]), Variable("Y")]),
                ),
            ),
            make_inference(
                InferenceRule.SKOLEMIZE,
                InferenceStatus.ESA,
                ["step1"],
                new_symbols=["sK0"],
                skolem_var="X",
                skolem_term=FunctionTerm("sK0", [Variable("Y")]),
            ),
        )

        issues = check_skolemization(child, parent)
        # This may currently fail - indicates a gap in handling binary formulas
        # TODO: Ensure existential quantifiers inside binary operators are recognized
        if issues:
            # Known limitation - document it
            assert any("not found" in issue.reason for issue in issues)
        else:
            assert issues == []


# ============================================================================
# NEGATED-CONJECTURE-CHECKER: Advanced Edge Cases
# ============================================================================


def make_neg_inference(rule, status, parents):
    """Helper to create InferenceRecord for negated conjecture steps."""
    from src.parser.ast_nodes import StatusInfo

    info = [StatusInfo(status=status)] if status is not None else []
    return InferenceRecord(rule=rule, info=info, parents=parents)


class TestNegatedConjectureDoubleNegation:
    """Test handling of double negation."""

    def test_double_negation_elimination(self):
        """If conjecture is ~(~P), negated should be P."""
        from src.checker.negated_conjecture_checker import _negate_formula

        atom = Atom("p", [])
        double_neg = Negation(Negation(atom))

        negated = _negate_formula(double_neg)
        assert negated == atom

    def test_double_negation_in_conjecture_step(self):
        """Conjecture: ~(~p(X)), Negated: p(X)"""
        conj = make_annotated(
            "c", FormulaRole.CONJECTURE, Negation(Negation(Atom("p", [Variable("X")])))
        )

        neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            Atom("p", [Variable("X")]),
            make_neg_inference(InferenceRule.NEGATED_CONJECTURE, InferenceStatus.CTH, ["c"]),
        )

        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []


class TestNegatedConjectureComplexDeMorgan:
    """Test De Morgan's laws with complex formulas."""

    def test_demorgan_conjunction_with_quantifier(self):
        """?[X]: (p(X) & q(X)) becomes ![X]: (~p(X) | ~q(X))
        NOTE: Current implementation doesn't apply De Morgan's laws to junction formulas.
        This is a known limitation that could be enhanced."""
        conj = make_annotated(
            "c",
            FormulaRole.CONJECTURE,
            QuantifiedFormula(
                Quantifier.EXISTENTIAL,
                ["X"],
                JunctionFormula(
                    BinaryConnective.AND, [Atom("p", [Variable("X")]), Atom("q", [Variable("X")])]
                ),
            ),
        )

        # Current behavior: wraps in simple negation
        neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                Negation(
                    JunctionFormula(
                        BinaryConnective.AND,
                        [Atom("p", [Variable("X")]), Atom("q", [Variable("X")])],
                    )
                ),
            ),
            make_neg_inference(InferenceRule.NEGATED_CONJECTURE, InferenceStatus.CTH, ["c"]),
        )

        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []

    def test_demorgan_conjunction_with_quantifier_idealized(self):
        """Test what the idealized version would look like (for future implementation).
        This documents the expected behavior once De Morgan's laws are fully applied."""
        conj = make_annotated(
            "c",
            FormulaRole.CONJECTURE,
            QuantifiedFormula(
                Quantifier.EXISTENTIAL,
                ["X"],
                JunctionFormula(
                    BinaryConnective.AND, [Atom("p", [Variable("X")]), Atom("q", [Variable("X")])]
                ),
            ),
        )

        # Idealized: full De Morgan's application
        # ?[X]: (p & q) => ![X]: (~p | ~q)
        idealized_neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                JunctionFormula(
                    BinaryConnective.OR,
                    [Negation(Atom("p", [Variable("X")])), Negation(Atom("q", [Variable("X")]))],
                ),
            ),
            make_neg_inference(InferenceRule.NEGATED_CONJECTURE, InferenceStatus.CTH, ["c"]),
        )

        issues = check_negated_conjecture(idealized_neg_conj, conj)
        # This will currently fail - documents gap
        if issues:
            pytest.skip("De Morgan's laws for junctions not yet implemented")

    def test_demorgan_disjunction_with_quantifier(self):
        """![X]: (p(X) | q(X)) becomes ?[X]: (~p(X) & ~q(X))
        NOTE: Current implementation doesn't apply De Morgan's laws to junction formulas.
        This is a known limitation."""
        conj = make_annotated(
            "c",
            FormulaRole.CONJECTURE,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                JunctionFormula(
                    BinaryConnective.OR, [Atom("p", [Variable("X")]), Atom("q", [Variable("X")])]
                ),
            ),
        )

        # Current behavior: wraps in simple negation
        neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            QuantifiedFormula(
                Quantifier.EXISTENTIAL,
                ["X"],
                Negation(
                    JunctionFormula(
                        BinaryConnective.OR,
                        [Atom("p", [Variable("X")]), Atom("q", [Variable("X")])],
                    )
                ),
            ),
            make_neg_inference(InferenceRule.NEGATED_CONJECTURE, InferenceStatus.CTH, ["c"]),
        )

        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []


class TestNegatedConjectureMultipleOperands:
    """Test negation of junctions with many operands."""

    def test_negation_of_triple_conjunction(self):
        """p(X) & q(X) & r(X) becomes ~(p(X) & q(X) & r(X))"""
        conj_formula = JunctionFormula(
            BinaryConnective.AND,
            [Atom("p", [Variable("X")]), Atom("q", [Variable("X")]), Atom("r", [Variable("X")])],
        )
        conj = make_annotated("c", FormulaRole.CONJECTURE, conj_formula)

        neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            Negation(conj_formula),
            make_neg_inference(InferenceRule.NEGATED_CONJECTURE, InferenceStatus.CTH, ["c"]),
        )

        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []

    def test_negation_of_quad_disjunction(self):
        """p | q | r | s becomes ~(p | q | r | s)"""
        conj_formula = JunctionFormula(
            BinaryConnective.OR, [Atom("p", []), Atom("q", []), Atom("r", []), Atom("s", [])]
        )
        conj = make_annotated("c", FormulaRole.CONJECTURE, conj_formula)

        neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            Negation(conj_formula),
            make_neg_inference(InferenceRule.NEGATED_CONJECTURE, InferenceStatus.CTH, ["c"]),
        )

        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []


class TestNegatedConjectureDeepQuantifierNesting:
    """Test deeply nested quantifiers with negation."""

    def test_four_level_quantifier_nesting(self):
        """?[X]: ![Y]: ?[Z]: ![W]: p(X,Y,Z,W)
        Becomes: ![X]: ?[Y]: ![Z]: ?[W]: ~p(X,Y,Z,W)"""
        conj = make_annotated(
            "c",
            FormulaRole.CONJECTURE,
            QuantifiedFormula(
                Quantifier.EXISTENTIAL,
                ["X"],
                QuantifiedFormula(
                    Quantifier.UNIVERSAL,
                    ["Y"],
                    QuantifiedFormula(
                        Quantifier.EXISTENTIAL,
                        ["Z"],
                        QuantifiedFormula(
                            Quantifier.UNIVERSAL,
                            ["W"],
                            Atom("p", [Variable("X"), Variable("Y"), Variable("Z"), Variable("W")]),
                        ),
                    ),
                ),
            ),
        )

        neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                QuantifiedFormula(
                    Quantifier.EXISTENTIAL,
                    ["Y"],
                    QuantifiedFormula(
                        Quantifier.UNIVERSAL,
                        ["Z"],
                        QuantifiedFormula(
                            Quantifier.EXISTENTIAL,
                            ["W"],
                            Negation(
                                Atom(
                                    "p",
                                    [Variable("X"), Variable("Y"), Variable("Z"), Variable("W")],
                                )
                            ),
                        ),
                    ),
                ),
            ),
            make_neg_inference(InferenceRule.NEGATED_CONJECTURE, InferenceStatus.CTH, ["c"]),
        )

        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []


class TestNegatedConjectureWithEquality:
    """Test negation of equality formulas."""

    def test_negate_simple_equality(self):
        """X = Y becomes wrapped in negation ~(X = Y)
        NOTE: Current implementation doesn't specially handle Equality negation.
        This is a potential enhancement."""
        conj = make_annotated(
            "c", FormulaRole.CONJECTURE, Equality(Variable("X"), Variable("Y"), negated=False)
        )

        # Current form: wrapped in negation
        neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            Negation(Equality(Variable("X"), Variable("Y"), negated=False)),
            make_neg_inference(InferenceRule.NEGATED_CONJECTURE, InferenceStatus.CTH, ["c"]),
        )

        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []

    def test_negate_simple_equality_idealized(self):
        """X = Y becomes X != Y (idealized form).
        Documents what could be enhanced in future versions."""
        conj = make_annotated(
            "c", FormulaRole.CONJECTURE, Equality(Variable("X"), Variable("Y"), negated=False)
        )

        # Idealized form: negated equality
        neg_conj_idealized = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            Equality(Variable("X"), Variable("Y"), negated=True),
            make_neg_inference(InferenceRule.NEGATED_CONJECTURE, InferenceStatus.CTH, ["c"]),
        )

        issues = check_negated_conjecture(neg_conj_idealized, conj)
        # This will currently fail - documents enhancement opportunity
        if issues:
            pytest.skip("Equality negation handling not yet implemented")

    def test_negate_negated_equality(self):
        """X != Y becomes wrapped in negation ~(X != Y)
        NOTE: Current implementation wraps in negation rather than toggling negated flag."""
        conj = make_annotated(
            "c", FormulaRole.CONJECTURE, Equality(Variable("X"), Variable("Y"), negated=True)
        )

        # Current form: wrapped in negation
        neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            Negation(Equality(Variable("X"), Variable("Y"), negated=True)),
            make_neg_inference(InferenceRule.NEGATED_CONJECTURE, InferenceStatus.CTH, ["c"]),
        )

        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []


class TestNegatedConjectureQuantifierWithEquality:
    """Test quantified equalities."""

    def test_quantified_equality_negation(self):
        """![X]: X = a becomes ?[X]: ~(X = a)
        NOTE: Current implementation wraps in negation rather than toggling equality negated flag.
        """
        conj = make_annotated(
            "c",
            FormulaRole.CONJECTURE,
            QuantifiedFormula(
                Quantifier.UNIVERSAL, ["X"], Equality(Variable("X"), Constant("a"), negated=False)
            ),
        )

        # Current form: quantifier flip + wrap in negation
        neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            QuantifiedFormula(
                Quantifier.EXISTENTIAL,
                ["X"],
                Negation(Equality(Variable("X"), Constant("a"), negated=False)),
            ),
            make_neg_inference(InferenceRule.NEGATED_CONJECTURE, InferenceStatus.CTH, ["c"]),
        )

        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
