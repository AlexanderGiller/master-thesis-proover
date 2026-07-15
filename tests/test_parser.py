# tests/test_parser.py
from src.parser.ast_nodes import AnnotatedFormula, FileSource, InferenceRecord, ProofFile
from src.var_mapping import FormulaRole, InferenceRule, InferenceStatus


class TestProblemParsing:

    def test_returns_list(self, simple_problem):
        assert isinstance(simple_problem, list)

    def test_correct_step_count(self, simple_problem):
        assert len(simple_problem) == 3

    def test_step_names(self, simple_problem):
        names = [s.name for s in simple_problem]
        assert names == ["ax1", "ax2", "con"]

    def test_step_roles(self, simple_problem):
        roles = [s.role for s in simple_problem]
        assert roles == [FormulaRole.AXIOM, FormulaRole.AXIOM, FormulaRole.CONJECTURE]

    def test_steps_are_annotated_formulas(self, simple_problem):
        for step in simple_problem:
            assert isinstance(step, AnnotatedFormula)

    def test_problem_steps_have_no_inference(self, simple_problem):
        # Raw problem axioms have no inference annotation
        for step in simple_problem:
            assert step.inference is None

    def test_conjecture_role(self, simple_problem):
        con = next(s for s in simple_problem if s.name == "con")
        assert con.role == FormulaRole.CONJECTURE


class TestProofParsing:

    def test_returns_proof_file(self, simple_proof):
        assert isinstance(simple_proof, ProofFile)

    def test_problem_ref_extracted(self, simple_proof):
        assert simple_proof.problem_ref == "simple.p"

    def test_correct_step_count(self, simple_proof):
        assert len(simple_proof.steps) == 7

    def test_step_names_present(self, simple_proof):
        names = [s.name for s in simple_proof.steps]
        assert "ax1" in names
        assert "neg_con" in names
        assert "contra" in names

    def test_negated_conjecture_step(self, simple_proof):
        step = next(s for s in simple_proof.steps if s.name == "neg_con")
        assert step.role == FormulaRole.NEGATED_CONJECTURE

    def test_inference_on_derived_steps(self, simple_proof):
        step = next(s for s in simple_proof.steps if s.name == "contra")
        assert step.inference is not None

    def test_final_step_rule(self, simple_proof):
        contra = next(s for s in simple_proof.steps if s.name == "contra")
        assert contra.inference.rule == InferenceRule.RESOLUTION

    def test_final_step_status(self, simple_proof):
        contra = next(s for s in simple_proof.steps if s.name == "contra")
        assert contra.inference.status == InferenceStatus.THM

    def test_final_step_parents(self, simple_proof):
        contra = next(s for s in simple_proof.steps if s.name == "contra")
        assert set(contra.inference.parents) == {"mp1", "neg_con"}

    def test_axiom_steps_have_file_source(self, simple_proof):
        ax1 = next(s for s in simple_proof.steps if s.name == "ax1")
        assert isinstance(ax1.raw_source, FileSource)
        assert ax1.inference is None


class TestInferenceRecord:

    def test_inference_record_fields(self, simple_proof):
        inst1 = next(s for s in simple_proof.steps if s.name == "inst1")
        inf = inst1.inference
        assert isinstance(inf, InferenceRecord)
        assert inf.rule == InferenceRule.RESOLUTION
        assert inf.status == InferenceStatus.THM
        assert inf.parents == ["ax1"]


class TestSkolemParsing:

    def test_skolem_step_present(self, skolem_proof):
        names = [s.name for s in skolem_proof.steps]
        assert "ax1_sk" in names

    def test_skolem_rule_name(self, skolem_proof):
        sk = next(s for s in skolem_proof.steps if s.name == "ax1_sk")
        assert sk.inference.rule == InferenceRule.SKOLEMIZE

    def test_skolem_status_is_esa(self, skolem_proof):
        sk = next(s for s in skolem_proof.steps if s.name == "ax1_sk")
        assert sk.inference.status == InferenceStatus.ESA

    def test_skolem_new_symbol(self, skolem_proof):
        sk = next(s for s in skolem_proof.steps if s.name == "ax1_sk")
        assert sk.inference.new_symbols == ["sK0"]

    def test_skolem_variable(self, skolem_proof):
        sk = next(s for s in skolem_proof.steps if s.name == "ax1_sk")
        assert sk.inference.skolem_var == "X"

    def test_skolem_parent(self, skolem_proof):
        sk = next(s for s in skolem_proof.steps if s.name == "ax1_sk")
        assert sk.inference.parents == ["ax1"]
