# tests/test_ast_nodes.py
from src.parser.ast_nodes import (
    AnnotatedFormula,
    InferenceRecord,
    NewSymbolsInfo,
    ProofFile,
    SkolemizeInfo,
    StatusInfo,
)
from src.var_mapping import (
    BinaryConnective,
    FormulaRole,
    InferenceRule,
    InferenceStatus,
    Quantifier,
)


class TestAnnotatedFormula:

    def test_creation(self):
        f = AnnotatedFormula(name="ax1", role=FormulaRole.AXIOM, formula=None)
        assert f.name == "ax1"
        assert f.role == FormulaRole.AXIOM
        assert f.inference is None

    def test_with_inference(self):
        info = [StatusInfo(status=InferenceStatus.THM)]
        inf = InferenceRecord(rule=InferenceRule.RESOLUTION, info=info, parents=["ax1"])
        f = AnnotatedFormula(name="step1", role=FormulaRole.PLAIN, formula=None, inference=inf)
        assert f.inference.rule == InferenceRule.RESOLUTION
        assert f.inference.status == InferenceStatus.THM


class TestInferenceRecord:

    def test_basic_fields(self):
        info = [StatusInfo(status=InferenceStatus.THM)]
        inf = InferenceRecord(rule=InferenceRule.RESOLUTION, info=info, parents=["a", "b"])
        assert inf.rule == InferenceRule.RESOLUTION
        assert inf.status == InferenceStatus.THM  # Via property
        assert inf.parents == ["a", "b"]

    def test_skolem_fields_default_none(self):
        inf = InferenceRecord(rule=InferenceRule.RESOLUTION, info=[], parents=[])
        assert inf.new_symbols is None
        assert inf.skolem_var is None
        assert inf.skolem_term is None

    def test_skolem_fields_populated(self):
        info = [
            StatusInfo(status=InferenceStatus.ESA),
            NewSymbolsInfo(kind="skolem", symbols=["sK0"]),
            SkolemizeInfo(variable="X", term="sK0"),
        ]
        inf = InferenceRecord(
            rule=InferenceRule.SKOLEMIZE,
            info=info,
            parents=["ax1"],
        )
        assert inf.new_symbols == ["sK0"]  # Via property
        assert inf.skolem_var == "X"  # Via property


class TestProofFile:

    def test_empty_steps(self):
        pf = ProofFile(problem_ref="test.p")
        assert pf.steps == []

    def test_with_steps(self):
        steps = [
            AnnotatedFormula(name="ax1", role=FormulaRole.AXIOM, formula=None),
            AnnotatedFormula(name="con", role=FormulaRole.CONJECTURE, formula=None),
        ]
        pf = ProofFile(problem_ref="test.p", steps=steps)
        assert len(pf.steps) == 2
        assert pf.problem_ref == "test.p"
