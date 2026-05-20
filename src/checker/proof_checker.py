from atp_bridge import verify_with_atp
from skolem_checker import check_skolemization

from src.parser.ast_nodes import AnnotatedFormula, ProofFile


class ProofCheckError(Exception):
    pass


class ProofChecker:
    def __init__(self, proof: ProofFile):
        self.proof = proof
        self.steps = {s.name: s for s in proof.steps}

    def check(self):
        for step in self.proof.steps:
            self._check_step(step)
        self._check_ends_with_false()
        print("✓ Proof accepted")

    def _check_step(self, step: AnnotatedFormula):
        inf = step.inference
        if inf is None:
            return  # axiom or conjecture — no inference to check

        parents = [self._get_parent(p, step.name) for p in inf.parents]

        if inf.rule == "skolemize":
            check_skolemization(step, parents[0])

        elif inf.rule == "negate_conjecture":
            self._check_negated_conjecture(step, parents)

        elif inf.status in ("thm", "cth"):
            # Delegate to external ATP for unspecified rules
            verify_with_atp(step, parents)

        else:
            raise ProofCheckError(
                f"[{step.name}] Unknown rule '{inf.rule}' with status '{inf.status}'"
            )

    def _get_parent(self, name: str, step_name: str) -> AnnotatedFormula:
        if name not in self.steps:
            raise ProofCheckError(f"[{step_name}] Parent '{name}' not found in proof")
        return self.steps[name]

    def _check_negated_conjecture(self, step, parents):
        # Verify the step is the negation of a conjecture parent
        if not any(p.role == "conjecture" for p in parents):
            raise ProofCheckError(f"[{step.name}] negated_conjecture step has no conjecture parent")

    def _check_ends_with_false(self):
        last = self.proof.steps[-1]
        # The final step must derive $false
        formula_str = str(last.formula)
        if "$false" not in formula_str:
            raise ProofCheckError("Proof does not end with $false")
