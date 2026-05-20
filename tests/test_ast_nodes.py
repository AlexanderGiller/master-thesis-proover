# tests/test_ast_nodes.py
from src.parser.ast_nodes import AnnotatedFormula, InferenceRecord, ProofFile


class TestAnnotatedFormula:

    def test_creation(self):
        f = AnnotatedFormula(name="ax1", role="axiom", formula=None)
        assert f.name == "ax1"
        assert f.role == "axiom"
        assert f.inference is None

    def test_with_inference(self):
        inf = InferenceRecord(rule="resolution", status="thm", parents=["ax1"])
        f = AnnotatedFormula(name="step1", role="plain", formula=None, inference=inf)
        assert f.inference.rule == "resolution"


class TestInferenceRecord:

    def test_basic_fields(self):
        inf = InferenceRecord(rule="resolution", status="thm", parents=["a", "b"])
        assert inf.rule == "resolution"
        assert inf.status == "thm"
        assert inf.parents == ["a", "b"]

    def test_skolem_fields_default_none(self):
        inf = InferenceRecord(rule="resolution", status="thm", parents=[])
        assert inf.new_symbols is None
        assert inf.skolem_var is None
        assert inf.skolem_term is None

    def test_skolem_fields_populated(self):
        inf = InferenceRecord(
            rule="skolemize",
            status="esa",
            parents=["ax1"],
            new_symbols=["sK0"],
            skolem_var="X",
            skolem_term="sK0",
        )
        assert inf.new_symbols == ["sK0"]
        assert inf.skolem_var == "X"


class TestProofFile:

    def test_empty_steps(self):
        pf = ProofFile(problem_ref="test.p")
        assert pf.steps == []

    def test_with_steps(self):
        steps = [
            AnnotatedFormula(name="ax1", role="axiom", formula=None),
            AnnotatedFormula(name="con", role="conjecture", formula=None),
        ]
        pf = ProofFile(problem_ref="test.p", steps=steps)
        assert len(pf.steps) == 2
        assert pf.problem_ref == "test.p"
