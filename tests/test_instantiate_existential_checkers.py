from pathlib import Path

from proof_checker_demo import check_proof_file
from src.checker.existential_gen_checker import check_existential_gen
from src.checker.instantiate_checker import check_instantiate
from src.parser.ast_nodes import (
    AnnotatedFormula,
    Atom,
    Constant,
    InferenceRecord,
    QuantifiedFormula,
    StatusInfo,
    Variable,
)
from src.var_mapping import FormulaRole, InferenceRule, InferenceStatus, Quantifier


ROOT = Path(__file__).resolve().parents[1]


def make_annotated(name, role, formula, inference=None):
    return AnnotatedFormula(name=name, role=role, formula=formula, inference=inference)


def make_inference(rule, status, parents):
    return InferenceRecord(rule=rule, info=[StatusInfo(status=status)], parents=parents)


class TestInstantiateChecker:
    def test_valid_simple_instantiation(self):
        parent = make_annotated(
            "p",
            FormulaRole.PLAIN,
            QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], Atom("q", [Variable("X")])),
        )
        child = make_annotated("c", FormulaRole.PLAIN, Atom("q", [Constant("a")]), make_inference(
            InferenceRule.INSTANTIATE, InferenceStatus.THM, ["p"]
        ))

        assert check_instantiate(child, parent) == []

    def test_valid_instantiation_with_shadowed_inner_quantifier(self):
        parent = make_annotated(
            "p",
            FormulaRole.PLAIN,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                QuantifiedFormula(
                    Quantifier.EXISTENTIAL,
                    ["Y"],
                    Atom("r", [Variable("X"), Variable("Y")]),
                ),
            ),
        )
        child = make_annotated(
            "c",
            FormulaRole.PLAIN,
            QuantifiedFormula(
                Quantifier.EXISTENTIAL,
                ["Y"],
                Atom("r", [Constant("a"), Variable("Y")]),
            ),
            make_inference(InferenceRule.INSTANTIATE, InferenceStatus.THM, ["p"]),
        )

        assert check_instantiate(child, parent) == []

    def test_invalid_instantiation(self):
        parent = make_annotated(
            "p",
            FormulaRole.PLAIN,
            QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], Atom("q", [Variable("X")])),
        )
        child = make_annotated(
            "c",
            FormulaRole.PLAIN,
            Atom("r", [Constant("a")]),
            make_inference(InferenceRule.INSTANTIATE, InferenceStatus.THM, ["p"]),
        )

        issues = check_instantiate(child, parent)
        assert issues


class TestExistentialGenChecker:
    def test_valid_simple_existential_generalization(self):
        parent = make_annotated(
            "p",
            FormulaRole.PLAIN,
            Atom("q", [Constant("a")]),
        )
        child = make_annotated(
            "c",
            FormulaRole.PLAIN,
            QuantifiedFormula(
                Quantifier.EXISTENTIAL,
                ["X"],
                Atom("q", [Variable("X")]),
            ),
            make_inference(InferenceRule.EXISTENTIAL_GEN, InferenceStatus.THM, ["p"]),
        )

        assert check_existential_gen(child, parent) == []

    def test_valid_existential_generalization_with_repeated_witness(self):
        parent = make_annotated(
            "p",
            FormulaRole.PLAIN,
            Atom("r", [Constant("a"), Constant("a")]),
        )
        child = make_annotated(
            "c",
            FormulaRole.PLAIN,
            QuantifiedFormula(
                Quantifier.EXISTENTIAL,
                ["X"],
                Atom("r", [Variable("X"), Variable("X")]),
            ),
            make_inference(InferenceRule.EXISTENTIAL_GEN, InferenceStatus.THM, ["p"]),
        )

        assert check_existential_gen(child, parent) == []

    def test_invalid_existential_generalization(self):
        parent = make_annotated("p", FormulaRole.PLAIN, Atom("q", [Constant("a")]))
        child = make_annotated(
            "c",
            FormulaRole.PLAIN,
            QuantifiedFormula(
                Quantifier.EXISTENTIAL,
                ["X"],
                Atom("r", [Variable("X")]),
            ),
            make_inference(InferenceRule.EXISTENTIAL_GEN, InferenceStatus.THM, ["p"]),
        )

        issues = check_existential_gen(child, parent)
        assert issues


class TestCheckerIntegrationExamples:
    def test_prv008_example_contains_new_steps(self):
        result = check_proof_file(
            str(ROOT / "ProoVer2026" / "PRV008+1.s"),
            str(ROOT / "ProoVer2026" / "Problems" / "PRV008+1.p"),
        )

        assert result["instantiate_issues"] == {}
        assert result["existential_gen_issues"] == {}
