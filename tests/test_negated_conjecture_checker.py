"""Tests for negated_conjecture checker."""

import pytest
from src.parser.ast_nodes import (
    AnnotatedFormula, InferenceRecord, Atom, Constant, Variable,
    QuantifiedFormula, Negation, BinaryFormula, JunctionFormula
)
from src.checker.negated_conjecture_checker import (
    check_negated_conjecture, NegatedConjectureIssue, _negate_formula
)


def make_annotated(name, role, formula, inference=None):
    """Helper to create AnnotatedFormula."""
    return AnnotatedFormula(name=name, role=role, formula=formula, inference=inference)


def make_inference(rule, status, parents):
    """Helper to create InferenceRecord."""
    return InferenceRecord(rule=rule, status=status, parents=parents)


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
        quantified = QuantifiedFormula("!", ["X"], inner)
        negated = _negate_formula(quantified)

        assert isinstance(negated, QuantifiedFormula)
        assert negated.quantifier == "?"
        assert negated.variables == ["X"]
        assert isinstance(negated.formula, Negation)

    def test_negate_existentially_quantified_becomes_universal(self):
        """?[X]: p(X) becomes ![X]: ~p(X)"""
        inner = Atom("p", args=[Variable("X")])
        quantified = QuantifiedFormula("?", ["X"], inner)
        negated = _negate_formula(quantified)

        assert isinstance(negated, QuantifiedFormula)
        assert negated.quantifier == "!"
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
        inner_quantified = QuantifiedFormula("?", ["Y"], inner_atom)
        outer_quantified = QuantifiedFormula("!", ["X"], inner_quantified)

        negated = _negate_formula(outer_quantified)

        assert isinstance(negated, QuantifiedFormula)
        assert negated.quantifier == "?"
        assert negated.variables == ["X"]
        assert isinstance(negated.formula, QuantifiedFormula)
        assert negated.formula.quantifier == "!"
        assert negated.formula.variables == ["Y"]


class TestNegatedConjectureChecker:
    """Tests for the negated_conjecture checker."""

    def test_valid_negated_conjecture_simple(self):
        """Valid negated_conjecture: negates a simple conjecture."""
        conj = make_annotated("c", "conjecture", Atom("p", args=[]))
        neg_conj = make_annotated(
            "nc",
            "negated_conjecture",
            Negation(Atom("p", args=[])),
            make_inference("negated_conjecture", "cth", ["c"])
        )
        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []

    def test_valid_negated_conjecture_quantified(self):
        """Valid negated_conjecture: negates a quantified conjecture."""
        # Conjecture: ![X]: p(X)
        conj = make_annotated(
            "c",
            "conjecture",
            QuantifiedFormula("!", ["X"], Atom("p", args=[Variable("X")]))
        )
        # Negated: ?[X]: ~p(X)
        neg_conj = make_annotated(
            "nc",
            "negated_conjecture",
            QuantifiedFormula("?", ["X"], Negation(Atom("p", args=[Variable("X")]))),
            make_inference("negated_conjecture", "cth", ["c"])
        )
        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []

    def test_valid_negated_conjecture_with_negation_in_conjecture(self):
        """Valid negated_conjecture: ?[X]: ~P(X) becomes ![X]: P(X) with negation elimination."""
        # Conjecture: ?[X]: ~(p(X) => q(X))
        inner_formula = BinaryFormula("=>", 
                                     Atom("p", args=[Variable("X")]),
                                     Atom("q", args=[Variable("X")]))
        conj = make_annotated(
            "c",
            "conjecture",
            QuantifiedFormula("?", ["X"], Negation(inner_formula))
        )
        # Negated: ![X]: (p(X) => q(X))  (negation of negation is eliminated)
        neg_conj = make_annotated(
            "nc",
            "negated_conjecture",
            QuantifiedFormula("!", ["X"], inner_formula),
            make_inference("negated_conjecture", "cth", ["c"])
        )
        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []

    def test_missing_inference_record(self):
        """Negated_conjecture without inference record should fail."""
        conj = make_annotated("c", "conjecture", Atom("p", args=[]))
        neg_conj = make_annotated("nc", "negated_conjecture", Negation(Atom("p", args=[])))

        issues = check_negated_conjecture(neg_conj, conj)
        assert len(issues) == 1
        assert "must have an inference record" in issues[0].reason

    def test_wrong_rule_name(self):
        """Negated_conjecture with wrong rule name should fail."""
        conj = make_annotated("c", "conjecture", Atom("p", args=[]))
        neg_conj = make_annotated(
            "nc",
            "negated_conjecture",
            Negation(Atom("p", args=[])),
            make_inference("resolution", "cth", ["c"])  # Wrong rule
        )
        issues = check_negated_conjecture(neg_conj, conj)
        assert any("rule must be 'negated_conjecture'" in it.reason for it in issues)

    def test_wrong_status(self):
        """Negated_conjecture with wrong status should fail."""
        conj = make_annotated("c", "conjecture", Atom("p", args=[]))
        neg_conj = make_annotated(
            "nc",
            "negated_conjecture",
            Negation(Atom("p", args=[])),
            make_inference("negated_conjecture", "thm", ["c"])  # Wrong status
        )
        issues = check_negated_conjecture(neg_conj, conj)
        assert any("status must be 'cth'" in it.reason for it in issues)

    def test_incorrect_formula_not_negation(self):
        """Negated_conjecture with incorrect formula (not a negation)."""
        conj = make_annotated("c", "conjecture", Atom("p", args=[]))
        neg_conj = make_annotated(
            "nc",
            "negated_conjecture",
            Atom("q", args=[]),  # Wrong: should be ~p
            make_inference("negated_conjecture", "cth", ["c"])
        )
        issues = check_negated_conjecture(neg_conj, conj)
        assert any("not the correct negation" in it.reason for it in issues)

    def test_incorrect_quantifier_flip(self):
        """Negated_conjecture with incorrect quantifier flip."""
        conj = make_annotated(
            "c",
            "conjecture",
            QuantifiedFormula("!", ["X"], Atom("p", args=[Variable("X")]))
        )
        # Wrong: should flip ! to ?
        neg_conj = make_annotated(
            "nc",
            "negated_conjecture",
            QuantifiedFormula("!", ["X"], Negation(Atom("p", args=[Variable("X")]))),
            make_inference("negated_conjecture", "cth", ["c"])
        )
        issues = check_negated_conjecture(neg_conj, conj)
        assert any("not the correct negation" in it.reason for it in issues)

    def test_variable_renaming_is_handled(self):
        """Negated_conjecture with renamed variables should still pass via alpha-equivalence."""
        conj = make_annotated(
            "c",
            "conjecture",
            QuantifiedFormula("!", ["X"], Atom("p", args=[Variable("X")]))
        )
        # Same negation but with renamed variable Y (should be alpha-equivalent)
        neg_conj = make_annotated(
            "nc",
            "negated_conjecture",
            QuantifiedFormula("?", ["Y"], Negation(Atom("p", args=[Variable("Y")]))),
            make_inference("negated_conjecture", "cth", ["c"])
        )
        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []

    def test_complex_formula_conjunction(self):
        """Negated_conjecture for complex formula: p(a) & q(b) becomes ~(p(a) & q(b))"""
        conj_formula = JunctionFormula("&", [
            Atom("p", args=[Constant("a")]),
            Atom("q", args=[Constant("b")])
        ])
        conj = make_annotated("c", "conjecture", conj_formula)

        neg_conj = make_annotated(
            "nc",
            "negated_conjecture",
            Negation(conj_formula),
            make_inference("negated_conjecture", "cth", ["c"])
        )
        issues = check_negated_conjecture(neg_conj, conj)
        assert issues == []

    def test_multiple_issues_reported(self):
        """Multiple issues (wrong rule, wrong status, wrong formula) are all reported."""
        conj = make_annotated("c", "conjecture", Atom("p", args=[]))
        neg_conj = make_annotated(
            "nc",
            "negated_conjecture",
            Atom("q", args=[]),  # Wrong formula
            make_inference("resolution", "thm", ["c"])  # Wrong rule and status
        )
        issues = check_negated_conjecture(neg_conj, conj)
        # Should have 3 issues: wrong rule, wrong status, wrong formula
        assert len(issues) >= 2
        reasons = {it.reason for it in issues}
        assert any("rule" in r for r in reasons)
        assert any("status" in r for r in reasons)
        assert any("negation" in r for r in reasons)

