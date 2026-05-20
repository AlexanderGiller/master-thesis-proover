from dataclasses import dataclass, field
from typing import Optional


@dataclass
class InferenceRecord:
    rule: str  # e.g. "skolemize", "resolution"
    status: str  # "thm", "esa", "cth"
    parents: list[str]
    new_symbols: Optional[list[str]] = None  # from new_symbols(...)
    skolem_var: Optional[str] = None  # from skolemize(Var, sk(...))
    skolem_term: Optional[str] = None


@dataclass
class AnnotatedFormula:
    name: str
    role: str  # "axiom", "plain", etc.
    formula: object  # parse tree node
    inference: Optional[InferenceRecord] = None
    raw_source: Optional[str] = None


@dataclass
class ProofFile:
    problem_ref: str  # from "Proof: problem.p" header
    steps: list[AnnotatedFormula] = field(default_factory=list)
