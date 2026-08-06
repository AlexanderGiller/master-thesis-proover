"""Tests for negated_conjecture checker."""

import pytest

from src.checker.negated_conjecture_checker import (
    NegatedConjectureIssue,
    _negate_formula,
    check_negated_conjecture,
)
from src.parser.ast_nodes import (
    AnnotatedFormula,
    Atom,
    BinaryFormula,
    Constant,
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


def make_annotated(name, role, formula, inference=None):
    """Helper to create AnnotatedFormula."""
    return AnnotatedFormula(name=name, role=role, formula=formula, inference=inference)


def make_inference(rule, status, parents):
    """Helper to create InferenceRecord."""
    from src.parser.ast_nodes import StatusInfo

    info = [StatusInfo(status=status)] if status is not None else []
    return InferenceRecord(rule=rule, info=info, parents=parents)


class TestNegateFormula:
    """Tests for the _negate_formula helper function."""

    def test_negate_simple_atom(self):
        """Negate a simple atom."""
        atom = Atom("p", args=[])
        negated = _negate_formula(atom)
        assert isinstance(negated, Negation)
        assert negated.formula == atom

    def test_negate_atom_with_args(self):
        """Negate an atom with arguments."""
        atom = Atom("p", args=[Constant("a"), Variable("X")])
        negated = _negate_formula(atom)
        assert isinstance(negated, Negation)

    def test_negate_universally_quantified_becomes_existential(self):
        """![X]: p(X) becomes ?[X]: ~p(X)"""
        inner = Atom("p", args=[Variable("X")])
        quantified = QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], inner)
        negated = _negate_formula(quantified)

        assert isinstance(negated, QuantifiedFormula)
        assert negated.quantifier == Quantifier.EXISTENTIAL
        assert negated.variables == ["X"]
        assert isinstance(negated.formula, Negation)

    def test_negate_existentially_quantified_becomes_universal(self):
        """?[X]: p(X) becomes ![X]: ~p(X)"""
        inner = Atom("p", args=[Variable("X")])
        quantified = QuantifiedFormula(Quantifier.EXISTENTIAL, ["X"], inner)
        negated = _negate_formula(quantified)

        assert isinstance(negated, QuantifiedFormula)
        assert negated.quantifier == Quantifier.UNIVERSAL
        assert negated.variables == ["X"]
        assert isinstance(negated.formula, Negation)

    def test_negate_negation_eliminates_double_negation(self):
        """Negating ~(~P) should eliminate the double negation and return P"""
        atom = Atom("p", args=[Variable("X")])
        single_negation = Negation(atom)
        # Negate the single negation
        negated = _negate_formula(single_negation)

        # Should eliminate negation and return the original atom
        assert negated == atom

    def test_negate_nested_quantifiers(self):
        """![X]: ?[Y]: p(X,Y) becomes ?[X]: ![Y]: ~p(X,Y)"""
        inner_atom = Atom("p", args=[Variable("X"), Variable("Y")])
        inner_quantified = QuantifiedFormula(Quantifier.EXISTENTIAL, ["Y"], inner_atom)
        outer_quantified = QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], inner_quantified)

        negated = _negate_formula(outer_quantified)

        assert isinstance(negated, QuantifiedFormula)
        assert negated.quantifier == Quantifier.EXISTENTIAL
        assert negated.variables == ["X"]
        assert isinstance(negated.formula, QuantifiedFormula)
        assert negated.formula.quantifier == Quantifier.UNIVERSAL
        assert negated.formula.variables == ["Y"]


class TestNegatedConjectureChecker:
    """Tests for the negated_conjecture checker."""

    def test_valid_negated_conjecture_simple(self):
        """Valid negated_conjecture: negates a simple conjecture."""
        conj = make_annotated("c", FormulaRole.CONJECTURE, Atom("p", args=[]))
        neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            Negation(Atom("p", args=[])),
            make_inference(InferenceRule.NEGATED_CONJECTURE, InferenceStatus.CTH, ["c"]),
        )
        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []

    def test_valid_negated_conjecture_quantified(self):
        """Valid negated_conjecture: negates a quantified conjecture."""
        # Conjecture: ![X]: p(X)
        conj = make_annotated(
            "c",
            FormulaRole.CONJECTURE,
            QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], Atom("p", args=[Variable("X")])),
        )
        # Negated: ?[X]: ~p(X)
        neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            QuantifiedFormula(
                Quantifier.EXISTENTIAL, ["X"], Negation(Atom("p", args=[Variable("X")]))
            ),
            make_inference(InferenceRule.NEGATED_CONJECTURE, InferenceStatus.CTH, ["c"]),
        )
        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []

    def test_valid_negated_conjecture_with_negation_in_conjecture(self):
        """Valid negated_conjecture: ?[X]: ~P(X) becomes ![X]: P(X) with negation elimination."""
        # Conjecture: ?[X]: ~(p(X) => q(X))
        inner_formula = BinaryFormula(
            BinaryConnective.IMPLIES,
            Atom("p", args=[Variable("X")]),
            Atom("q", args=[Variable("X")]),
        )
        conj = make_annotated(
            "c",
            FormulaRole.CONJECTURE,
            QuantifiedFormula(Quantifier.EXISTENTIAL, ["X"], Negation(inner_formula)),
        )
        # Negated: ![X]: (p(X) => q(X))  (negation of negation is eliminated)
        neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], inner_formula),
            make_inference(InferenceRule.NEGATED_CONJECTURE, InferenceStatus.CTH, ["c"]),
        )
        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []

    def test_missing_inference_record(self):
        """Negated_conjecture without inference record should fail."""
        conj = make_annotated("c", FormulaRole.CONJECTURE, Atom("p", args=[]))
        neg_conj = make_annotated(
            "nc", FormulaRole.NEGATED_CONJECTURE, Negation(Atom("p", args=[]))
        )

        issues = check_negated_conjecture(neg_conj, conj)
        assert len(issues) == 1
        assert "must have an inference record" in issues[0].reason

    def test_wrong_rule_name(self):
        """Negated_conjecture with wrong rule name should fail."""
        conj = make_annotated("c", FormulaRole.CONJECTURE, Atom("p", args=[]))
        neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            Negation(Atom("p", args=[])),
            make_inference(InferenceRule.RESOLUTION, InferenceStatus.CTH, ["c"]),  # Wrong rule
        )
        issues = check_negated_conjecture(neg_conj, conj)
        assert any("rule must be 'negated_conjecture'" in it.reason for it in issues)

    def test_wrong_status(self):
        """Negated_conjecture with wrong status should fail."""
        conj = make_annotated("c", FormulaRole.CONJECTURE, Atom("p", args=[]))
        neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            Negation(Atom("p", args=[])),
            make_inference(
                InferenceRule.NEGATED_CONJECTURE, InferenceStatus.THM, ["c"]
            ),  # Wrong status
        )
        issues = check_negated_conjecture(neg_conj, conj)
        assert any("status must be 'cth'" in it.reason for it in issues)

    def test_incorrect_formula_not_negation(self):
        """Negated_conjecture with incorrect formula (not a negation)."""
        conj = make_annotated("c", FormulaRole.CONJECTURE, Atom("p", args=[]))
        neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            Atom("q", args=[]),  # Wrong: should be ~p
            make_inference(InferenceRule.NEGATED_CONJECTURE, InferenceStatus.CTH, ["c"]),
        )
        issues = check_negated_conjecture(neg_conj, conj)
        assert any("not the correct negation" in it.reason for it in issues)

    def test_incorrect_quantifier_flip(self):
        """Negated_conjecture with incorrect quantifier flip."""
        conj = make_annotated(
            "c",
            FormulaRole.CONJECTURE,
            QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], Atom("p", args=[Variable("X")])),
        )
        # Wrong: should flip ! to ?
        neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            QuantifiedFormula(
                Quantifier.UNIVERSAL, ["X"], Negation(Atom("p", args=[Variable("X")]))
            ),
            make_inference(InferenceRule.NEGATED_CONJECTURE, InferenceStatus.CTH, ["c"]),
        )
        issues = check_negated_conjecture(neg_conj, conj)
        assert any("not the correct negation" in it.reason for it in issues)

    def test_variable_renaming_is_handled(self):
        """Negated_conjecture with renamed variables should still pass via alpha-equivalence."""
        conj = make_annotated(
            "c",
            FormulaRole.CONJECTURE,
            QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], Atom("p", args=[Variable("X")])),
        )
        # Same negation but with renamed variable Y (should be alpha-equivalent)
        neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            QuantifiedFormula(
                Quantifier.EXISTENTIAL, ["Y"], Negation(Atom("p", args=[Variable("Y")]))
            ),
            make_inference(InferenceRule.NEGATED_CONJECTURE, InferenceStatus.CTH, ["c"]),
        )
        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []

    def test_complex_formula_conjunction(self):
        """Negated_conjecture for complex formula: p(a) & q(b) becomes ~(p(a) & q(b))"""
        conj_formula = JunctionFormula(
            "&", [Atom("p", args=[Constant("a")]), Atom("q", args=[Constant("b")])]
        )
        conj = make_annotated("c", "conjecture", conj_formula)

        neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            Negation(conj_formula),
            make_inference(InferenceRule.NEGATED_CONJECTURE, InferenceStatus.CTH, ["c"]),
        )
        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []

    def test_multiple_issues_reported(self):
        """Multiple issues (wrong rule, wrong status, wrong formula) are all reported."""
        conj = make_annotated("c", "conjecture", Atom("p", args=[]))
        neg_conj = make_annotated(
            "nc",
            FormulaRole.NEGATED_CONJECTURE,
            Atom("q", args=[]),  # Wrong formula
            make_inference(
                InferenceRule.RESOLUTION, InferenceStatus.THM, ["c"]
            ),  # Wrong rule and status
        )
        issues = check_negated_conjecture(neg_conj, conj)
        # Should have 3 issues: wrong rule, wrong status, wrong formula
        assert len(issues) >= 2
        reasons = {it.reason for it in issues}
        assert any("rule" in r for r in reasons)
        assert any("status" in r for r in reasons)
        assert any("negation" in r for r in reasons)

    def test_prv001_scoped_variables(self):
        """PRV001-style conjectures should compare correctly despite reused variable names."""
        conj = make_annotated(
            "c",
            FormulaRole.CONJECTURE,
            Negation(
                QuantifiedFormula(
                    Quantifier.UNIVERSAL,
                    ["X"],
                    QuantifiedFormula(
                        Quantifier.EXISTENTIAL,
                        ["Y"],
                        QuantifiedFormula(
                            Quantifier.UNIVERSAL,
                            ["Z"],
                            Atom("p", args=[Variable("X"), Variable("Y"), Variable("Z")]),
                        ),
                    ),
                )
            ),
        )
        neg_conj = make_annotated(
            "neg",
            FormulaRole.NEGATED_CONJECTURE,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["A"],
                QuantifiedFormula(
                    Quantifier.EXISTENTIAL,
                    ["B"],
                    QuantifiedFormula(
                        Quantifier.UNIVERSAL,
                        ["C"],
                        Atom("p", args=[Variable("A"), Variable("B"), Variable("C")]),
                    ),
                ),
            ),
            make_inference(InferenceRule.NEGATED_CONJECTURE, InferenceStatus.CTH, ["c"]),
        )

        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []
