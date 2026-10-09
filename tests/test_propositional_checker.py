from main import check_proof_file
from src.checker.propositional_checker import (
    check_conjunction,
    check_modus_ponens,
    check_split_conjunct,
)
from src.parser.ast_nodes import (
    AnnotatedFormula,
    Atom,
    BinaryFormula,
    Constant,
    InferenceRecord,
    JunctionFormula,
    StatusInfo,
    Variable,
    QuantifiedFormula,
)
from src.var_mapping import BinaryConnective, FormulaRole, InferenceRule, InferenceStatus, Quantifier


def annotated(name, formula, inference=None):
    return AnnotatedFormula(name, FormulaRole.PLAIN, formula, inference)


def inference(rule, parents):
    return InferenceRecord(rule, [StatusInfo(InferenceStatus.THM)], parents)


def test_modus_ponens_accepts_universal_implication_and_reversed_parent_order():
    implication = annotated(
        "rule",
        QuantifiedFormula(
            Quantifier.UNIVERSAL,
            ["X"],
            BinaryFormula(BinaryConnective.IMPLIES, Atom("p", [Variable("X")]), Atom("q", [Variable("X")])),
        ),
    )
    premise = annotated("premise", Atom("p", [Constant("a")]))
    conclusion = annotated("result", Atom("q", [Constant("a")]), inference(InferenceRule.MODUS_PONENS, ["premise", "rule"]))

    assert check_modus_ponens(conclusion, premise, implication) == []


def test_modus_ponens_rejects_missing_or_wrong_premise():
    implication = annotated(
        "rule",
        BinaryFormula(BinaryConnective.IMPLIES, Atom("p"), Atom("q")),
    )
    premise = annotated("premise", Atom("r"))
    conclusion = annotated("result", Atom("q"), inference(InferenceRule.MODUS_PONENS, ["rule", "premise"]))

    assert check_modus_ponens(conclusion, implication, premise)


def test_conjunction_and_split_conjunct():
    left = annotated("left", Atom("p"))
    right = annotated("right", Atom("q"))
    both = annotated(
        "both",
        JunctionFormula(BinaryConnective.AND, [Atom("p"), Atom("q")]),
        inference(InferenceRule.CONJUNCTION, ["left", "right"]),
    )

    assert check_conjunction(both, left, right) == []
    part = annotated("part", Atom("q"), inference(InferenceRule.SPLIT_CONJUNCT, ["both"]))
    assert check_split_conjunct(part, both) == []


def test_conjunction_flattens_nary_parent_conjunctions():
    # Combining a parent that is already "A & B" with a plain parent "C"
    # must flatten to "A & B & C", not "(A & B) & C" (the parser
    # represents "&" as an n-ary junction rather than a binary tree).
    left = annotated("left", JunctionFormula(BinaryConnective.AND, [Atom("a"), Atom("b")]))
    right = annotated("right", Atom("c"))
    combined = annotated(
        "combined",
        JunctionFormula(BinaryConnective.AND, [Atom("a"), Atom("b"), Atom("c")]),
        inference(InferenceRule.CONJUNCTION, ["left", "right"]),
    )

    assert check_conjunction(combined, left, right) == []


def test_conjunction_flattens_both_nary_parents():
    left = annotated("left", JunctionFormula(BinaryConnective.AND, [Atom("a"), Atom("b")]))
    right = annotated("right", JunctionFormula(BinaryConnective.AND, [Atom("c"), Atom("d")]))
    combined = annotated(
        "combined",
        JunctionFormula(BinaryConnective.AND, [Atom("a"), Atom("b"), Atom("c"), Atom("d")]),
        inference(InferenceRule.CONJUNCTION, ["left", "right"]),
    )

    assert check_conjunction(combined, left, right) == []


def test_conjunction_rejects_wrong_operand_count():
    left = annotated("left", JunctionFormula(BinaryConnective.AND, [Atom("a"), Atom("b")]))
    right = annotated("right", Atom("c"))
    combined = annotated(
        "combined",
        JunctionFormula(BinaryConnective.AND, [Atom("a"), Atom("b")]),
        inference(InferenceRule.CONJUNCTION, ["left", "right"]),
    )

    issues = check_conjunction(combined, left, right)
    assert any("operand" in it.reason for it in issues)


def test_integration_uses_rule_specific_checkers():
    result = check_proof_file(
        "ProoVer2026/PRV011+1.s",
        "ProoVer2026/Problems/PRV011+1.p",
    )

    assert result["conjunction_issues"] == {}
    assert result["split_conjunct_issues"] == {}


def test_integration_prv014_nary_conjunction_flattening():
    result = check_proof_file(
        "ProoVer2026/PRV014+1.s",
        "ProoVer2026/Problems/PRV014+1.p",
    )

    assert result["conjunction_issues"] == {}
