from pathlib import Path

from main import check_proof_file
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
            str(ROOT / "tests" / "fixtures" / "examples" / "correct" / "COR003+1.s"),
            str(ROOT / "tests" / "fixtures" / "examples" / "correct" / "Problems" / "COR003+1.p"),
        )

        assert result["skolem_issues"] == {}

    def test_evl003_reports_duplicate_skolem_symbol(self):
        result = check_proof_file(
            str(ROOT / "tests" / "fixtures" / "examples" / "incorrect" / "EVL003+1.s"),
            str(ROOT / "tests" / "fixtures" / "examples" / "incorrect" / "Problems" / "EVL003+1.p"),
        )

        assert "groom" in result["skolem_issues"]
        assert any(
            "already introduced earlier" in reason for reason in result["skolem_issues"]["groom"]
        )

    def test_evl004_reports_incorrect_resulting_formula(self):
        result = check_proof_file(
            str(ROOT / "tests" / "fixtures" / "examples" / "incorrect" / "EVL004+1.s"),
            str(ROOT / "tests" / "fixtures" / "examples" / "incorrect" / "Problems" / "EVL004+1.p"),
        )

        assert "groom" in result["skolem_issues"]
        assert any(
            "not a correct Skolemization" in reason for reason in result["skolem_issues"]["groom"]
        )

    def test_prv085_reports_no_skolem_issues(self):
        result = check_proof_file(
            str(ROOT / "ProoVer2026" / "PRV" / "PRV085+1.s"),
            str(ROOT / "ProoVer2026" / "PRV" / "Problems" / "PRV085+1.p"),
        )

        assert result["skolem_issues"] == {}

    def test_prv083_reports_universal_only_skolem_target(self):
        result = check_proof_file(
            str(ROOT / "ProoVer2026" / "PRV" / "PRV083+1.s"),
            str(ROOT / "ProoVer2026" / "PRV" / "Problems" / "PRV083+1.p"),
        )

        assert "sk" in result["skolem_issues"]
        assert any(
            "quantified only universally" in reason
            for reason in result["skolem_issues"]["sk"]
        )

    def test_prv084_reports_negative_polarity_existential(self):
        result = check_proof_file(
            str(ROOT / "ProoVer2026" / "PRV" / "PRV084+1.s"),
            str(ROOT / "ProoVer2026" / "PRV" / "Problems" / "PRV084+1.p"),
        )

        assert "sk" in result["skolem_issues"]
        assert any(
            "negative polarity" in reason
            for reason in result["skolem_issues"]["sk"]
        )



def _bin(conn, left, right):
    from src.parser.ast_nodes import BinaryFormula

    return BinaryFormula(connective=conn, left=left, right=right)


def _sk_step(formula, var="X", term=None):
    term = term or FunctionTerm("sK0", [])
    return make_annotated(
        "sk",
        FormulaRole.PLAIN,
        formula,
        make_inference(
            InferenceRule.SKOLEMIZE,
            InferenceStatus.ESA,
            ["par"],
            new_symbols=["sK0"],
            skolem_var=var,
            skolem_term=term,
        ),
    )


def _p(t):
    return Atom("p", [t])


def _r():
    return Atom("r", [])


class TestSkolemPolarityBelowConnectives:
    """Polarity of quantifiers in the antecedent of an implication and below equivalences."""

    def test_existential_in_antecedent_cannot_be_eliminated(self):
        # (?[X]: p(X)) => r  is  ![X]: (p(X) => r); X is effectively universal.
        parent = make_annotated(
            "par",
            FormulaRole.AXIOM,
            _bin(
                BinaryConnective.IMPLIES,
                QuantifiedFormula(Quantifier.EXISTENTIAL, ["X"], _p(Variable("X"))),
                _r(),
            ),
        )
        child = _sk_step(_bin(BinaryConnective.IMPLIES, _p(FunctionTerm("sK0", [])), _r()))
        issues = check_skolemization(child, parent)
        assert issues
        assert any("negative polarity" in str(i) for i in issues)

    def test_universal_in_antecedent_is_effectively_existential(self):
        # (![X]: p(X)) => r  is  ?[X]: (p(X) => r); sK0 is a valid Skolem constant.
        parent = make_annotated(
            "par",
            FormulaRole.AXIOM,
            _bin(
                BinaryConnective.IMPLIES,
                QuantifiedFormula(Quantifier.UNIVERSAL, ["X"], _p(Variable("X"))),
                _r(),
            ),
        )
        child = _sk_step(_bin(BinaryConnective.IMPLIES, _p(FunctionTerm("sK0", [])), _r()))
        assert check_skolemization(child, parent) == []

    def test_existential_in_consequent_still_works(self):
        parent = make_annotated(
            "par",
            FormulaRole.AXIOM,
            _bin(
                BinaryConnective.IMPLIES,
                _r(),
                QuantifiedFormula(Quantifier.EXISTENTIAL, ["X"], _p(Variable("X"))),
            ),
        )
        child = _sk_step(_bin(BinaryConnective.IMPLIES, _r(), _p(FunctionTerm("sK0", []))))
        assert check_skolemization(child, parent) == []

    def test_quantifier_below_equivalence_is_rejected(self):
        parent = make_annotated(
            "par",
            FormulaRole.AXIOM,
            _bin(
                BinaryConnective.IFF,
                QuantifiedFormula(Quantifier.EXISTENTIAL, ["X"], _p(Variable("X"))),
                _r(),
            ),
        )
        child = _sk_step(_bin(BinaryConnective.IFF, _p(FunctionTerm("sK0", [])), _r()))
        assert check_skolemization(child, parent)
