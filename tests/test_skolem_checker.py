from pathlib import Path

from proof_checker_demo import check_proof_file
from src.checker.skolem_checker import check_skolemization
from src.parser.ast_nodes import (
    AnnotatedFormula,
    Atom,
    FunctionTerm,
    InferenceRecord,
    NewSymbolsInfo,
    QuantifiedFormula,
    SkolemizeInfo,
    StatusInfo,
    Variable,
)
from src.var_mapping import (
    BinaryConnective,
    FormulaRole,
    InferenceRule,
    InferenceStatus,
    Quantifier,
)

ROOT = Path(__file__).resolve().parents[1]


def make_annotated(name, role, formula, inference=None):
    return AnnotatedFormula(name=name, role=role, formula=formula, inference=inference)


def make_inference(rule, status, parents, *, new_symbols=None, skolem_var=None, skolem_term=None):
    """Helper to create InferenceRecord with new info structure."""
    info = []
    if status is not None:
        info.append(StatusInfo(status=status))
    if new_symbols is not None:
        info.append(NewSymbolsInfo(kind="skolem", symbols=new_symbols))
    if skolem_var is not None and skolem_term is not None:
        info.append(SkolemizeInfo(variable=skolem_var, term=skolem_term))

    return InferenceRecord(rule=rule, info=info, parents=parents)


class TestSkolemCheckerUnit:
    def test_valid_first_skolemization(self):
        parent = make_annotated(
            "marriage",
            FormulaRole.AXIOM,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["Marriage"],
                QuantifiedFormula(
                    Quantifier.EXISTENTIAL,
                    ["Bride"],
                    QuantifiedFormula(
                        Quantifier.EXISTENTIAL,
                        ["Groom"],
                        Atom("in_love", [Variable("Groom"), Variable("Bride")]),
                    ),
                ),
            ),
        )
        child = make_annotated(
            "bride",
            FormulaRole.PLAIN,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["Marriage"],
                QuantifiedFormula(
                    Quantifier.EXISTENTIAL,
                    ["Groom"],
                    Atom(
                        "in_love",
                        [
                            Variable("Groom"),
                            FunctionTerm("sK0", [Variable("Marriage")]),
                        ],
                    ),
                ),
            ),
            make_inference(
                InferenceRule.SKOLEMIZE,
                InferenceStatus.ESA,
                ["marriage"],
                new_symbols=["sK0"],
                skolem_var="Bride",
                skolem_term=FunctionTerm("sK0", [Variable("Marriage")]),
            ),
        )

        issues = check_skolemization(child, parent)
        assert issues == []

    def test_valid_second_skolemization(self):
        parent = make_annotated(
            "bride",
            FormulaRole.PLAIN,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["Marriage"],
                QuantifiedFormula(
                    Quantifier.EXISTENTIAL,
                    ["Groom"],
                    Atom(
                        "in_love",
                        [
                            Variable("Groom"),
                            FunctionTerm("sK0", [Variable("Marriage")]),
                        ],
                    ),
                ),
            ),
        )
        child = make_annotated(
            "groom",
            FormulaRole.PLAIN,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["Marriage"],
                Atom(
                    "in_love",
                    [
                        FunctionTerm("sK1", [Variable("Marriage")]),
                        FunctionTerm("sK0", [Variable("Marriage")]),
                    ],
                ),
            ),
            make_inference(
                InferenceRule.SKOLEMIZE,
                InferenceStatus.ESA,
                ["bride"],
                new_symbols=["sK1"],
                skolem_var="Groom",
                skolem_term=FunctionTerm("sK1", [Variable("Marriage")]),
            ),
        )

        issues = check_skolemization(child, parent)
        assert issues == []

    def test_wrong_skolem_arguments_are_reported(self):
        parent = make_annotated(
            "marriage",
            FormulaRole.AXIOM,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["Marriage"],
                QuantifiedFormula(
                    Quantifier.EXISTENTIAL,
                    ["Bride"],
                    Atom("p", [Variable("Bride"), Variable("Marriage")]),
                ),
            ),
        )
        child = make_annotated(
            "bride",
            FormulaRole.PLAIN,
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["Marriage"],
                Atom("p", [FunctionTerm("sK0", []), Variable("Marriage")]),
            ),
            make_inference(
                InferenceRule.SKOLEMIZE,
                InferenceStatus.ESA,
                ["marriage"],
                new_symbols=["sK0"],
                skolem_var="Bride",
                skolem_term=FunctionTerm("sK0", []),
            ),
        )

        issues = check_skolemization(child, parent)
        assert any("arguments" in issue.reason for issue in issues)


class TestSkolemCheckerExamples:
    def test_cor003_reports_no_skolem_issues(self):
        result = check_proof_file(
            str(ROOT / "examples" / "correct" / "COR003+1.s"),
            str(ROOT / "examples" / "correct" / "Problems" / "COR003+1.p"),
        )

        assert result["skolem_issues"] == {}

    def test_evl003_reports_duplicate_skolem_symbol(self):
        result = check_proof_file(
            str(ROOT / "examples" / "incorrect" / "EVL003+1.s"),
            str(ROOT / "examples" / "incorrect" / "Problems" / "EVL003+1.p"),
        )

        assert "groom" in result["skolem_issues"]
        assert any(
            "already introduced earlier" in reason for reason in result["skolem_issues"]["groom"]
        )

    def test_evl004_reports_incorrect_resulting_formula(self):
        result = check_proof_file(
            str(ROOT / "examples" / "incorrect" / "EVL004+1.s"),
            str(ROOT / "examples" / "incorrect" / "Problems" / "EVL004+1.p"),
        )

        assert "groom" in result["skolem_issues"]
        assert any(
            "not a correct Skolemization" in reason for reason in result["skolem_issues"]["groom"]
        )
