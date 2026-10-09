from main import check_proof_file
from src.checker.structural_checker import (
    check_copy,
    check_double_negation,
    check_duplicate,
    check_remove_double_negation,
    check_rename_variable,
)
from src.parser.ast_nodes import (
    AnnotatedFormula,
    Atom,
    Constant,
    InferenceRecord,
    Negation,
    StatusInfo,
    Variable,
    QuantifiedFormula,
)
from src.var_mapping import FormulaRole, InferenceRule, InferenceStatus, Quantifier


def annotated(name, formula, inference=None):
    return AnnotatedFormula(name, FormulaRole.PLAIN, formula, inference)


def inference(rule, parents):
    return InferenceRecord(rule, [StatusInfo(InferenceStatus.THM)], parents)


class TestCopy:
    def test_valid_copy(self):
        parent = annotated("p", Atom("p", [Constant("a")]))
        step = annotated(
            "c", Atom("p", [Constant("a")]), inference(InferenceRule.COPY, ["p"])
        )
        assert check_copy(step, parent) == []

    def test_copy_with_different_formula_is_rejected(self):
        parent = annotated("p", Atom("p", [Constant("a")]))
        step = annotated(
            "c", Atom("q", [Constant("a")]), inference(InferenceRule.COPY, ["p"])
        )
        issues = check_copy(step, parent)
        assert any("does not match" in it.reason for it in issues)

    def test_copy_allows_alpha_renaming(self):
        parent = annotated(
            "p",
            QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], Atom("p", [Variable("X")])),
        )
        step = annotated(
            "c",
            QuantifiedFormula(Quantifier.UNIVERSAL, ["Y"], Atom("p", [Variable("Y")])),
            inference(InferenceRule.COPY, ["p"]),
        )
        assert check_copy(step, parent) == []


class TestDuplicate:
    def test_valid_duplicate_from_same_parent_twice(self):
        parent = annotated("p", Atom("p", [Constant("a")]))
        step = annotated(
            "c",
            Atom("p", [Constant("a")]),
            inference(InferenceRule.DUPLICATE, ["p", "p"]),
        )
        assert check_duplicate(step, parent, parent) == []

    def test_duplicate_rejects_mismatched_parents(self):
        left = annotated("l", Atom("p", [Constant("a")]))
        right = annotated("r", Atom("q", [Constant("a")]))
        step = annotated(
            "c", Atom("p", [Constant("a")]), inference(InferenceRule.DUPLICATE, ["l", "r"])
        )
        issues = check_duplicate(step, left, right)
        assert any("not alpha-equivalent" in it.reason for it in issues)

    def test_duplicate_rejects_conclusion_mismatch(self):
        parent = annotated("p", Atom("p", [Constant("a")]))
        step = annotated(
            "c", Atom("q", [Constant("a")]), inference(InferenceRule.DUPLICATE, ["p", "p"])
        )
        issues = check_duplicate(step, parent, parent)
        assert any("does not match" in it.reason for it in issues)


class TestRenameVariable:
    def test_valid_rename(self):
        parent = annotated(
            "p",
            QuantifiedFormula(Quantifier.UNIVERSAL, ["Z"], Atom("q", [Variable("Z")])),
        )
        step = annotated(
            "c",
            QuantifiedFormula(Quantifier.UNIVERSAL, ["W"], Atom("q", [Variable("W")])),
            inference(InferenceRule.RENAME_VARIABLE, ["p"]),
        )
        assert check_rename_variable(step, parent) == []

    def test_rename_rejects_structural_change(self):
        parent = annotated(
            "p",
            QuantifiedFormula(Quantifier.UNIVERSAL, ["Z"], Atom("q", [Variable("Z")])),
        )
        step = annotated(
            "c",
            Atom("q", [Constant("a")]),
            inference(InferenceRule.RENAME_VARIABLE, ["p"]),
        )
        issues = check_rename_variable(step, parent)
        assert any("not a variable-renaming" in it.reason for it in issues)


class TestDoubleNegation:
    def test_valid_double_negation(self):
        parent = annotated("p", Atom("p", [Constant("a")]))
        step = annotated(
            "c",
            Negation(Negation(Atom("p", [Constant("a")]))),
            inference(InferenceRule.DOUBLE_NEGATION, ["p"]),
        )
        assert check_double_negation(step, parent) == []

    def test_double_negation_requires_two_negations(self):
        parent = annotated("p", Atom("p", [Constant("a")]))
        step = annotated(
            "c",
            Negation(Atom("p", [Constant("a")])),
            inference(InferenceRule.DOUBLE_NEGATION, ["p"]),
        )
        issues = check_double_negation(step, parent)
        assert any("double negation" in it.reason for it in issues)

    def test_double_negation_rejects_changed_inner_formula(self):
        parent = annotated("p", Atom("p", [Constant("a")]))
        step = annotated(
            "c",
            Negation(Negation(Atom("q", [Constant("a")]))),
            inference(InferenceRule.DOUBLE_NEGATION, ["p"]),
        )
        issues = check_double_negation(step, parent)
        assert any("does not match" in it.reason for it in issues)


class TestRemoveDoubleNegation:
    def test_valid_removal(self):
        parent = annotated("p", Negation(Negation(Atom("p", [Constant("a")]))))
        step = annotated(
            "c",
            Atom("p", [Constant("a")]),
            inference(InferenceRule.REMOVE_DOUBLE_NEGATION, ["p"]),
        )
        assert check_remove_double_negation(step, parent) == []

    def test_removal_requires_parent_double_negation(self):
        parent = annotated("p", Atom("p", [Constant("a")]))
        step = annotated(
            "c",
            Atom("p", [Constant("a")]),
            inference(InferenceRule.REMOVE_DOUBLE_NEGATION, ["p"]),
        )
        issues = check_remove_double_negation(step, parent)
        assert any("must be a double negation" in it.reason for it in issues)


class TestIntegrationAgainstRealProofs:
    def test_prv009_rename_variable(self):
        result = check_proof_file(
            "ProoVer2026/PRV009+1.s", "ProoVer2026/Problems/PRV009+1.p"
        )
        assert result["rename_variable_issues"] == {}

    def test_prv026_copy(self):
        result = check_proof_file(
            "ProoVer2026/PRV026+1.s", "ProoVer2026/Problems/PRV026+1.p"
        )
        assert result["copy_issues"] == {}

    def test_prv098_copy_and_duplicate_chain(self):
        result = check_proof_file(
            "ProoVer2026/PRV098+1.s", "ProoVer2026/Problems/PRV098+1.p"
        )
        assert result["copy_issues"] == {}
        assert result["duplicate_issues"] == {}

    def test_prv010_double_negation_and_removal(self):
        result = check_proof_file(
            "ProoVer2026/PRV010+1.s", "ProoVer2026/Problems/PRV010+1.p"
        )
        assert result["double_negation_issues"] == {}
        assert result["remove_double_negation_issues"] == {}
