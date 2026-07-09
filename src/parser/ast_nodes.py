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
    problem_ref: str
    steps: list[AnnotatedFormula] = field(default_factory=list)


@dataclass
class Variable:
    name: str

    def __repr__(self):
        return self.name


@dataclass
class Constant:
    name: str

    def __repr__(self):
        return self.name


@dataclass
class FunctionTerm:
    functor: str
    args: list

    def __repr__(self):
        return f"{self.functor}({', '.join(map(repr, self.args))})"


@dataclass
class Atom:
    predicate: str
    args: list = field(default_factory=list)

    def __repr__(self):
        if not self.args:
            return self.predicate
        return f"{self.predicate}({', '.join(map(repr, self.args))})"


@dataclass
class Equality:
    left: object
    right: object
    negated: bool = False

    def __repr__(self):
        op = "!=" if self.negated else "="
        return f"{self.left!r} {op} {self.right!r}"


@dataclass
class Negation:
    formula: object

    def __repr__(self):
        return f"~{self.formula!r}"


@dataclass
class BinaryFormula:
    connective: str  # "=>", "<=>", "<~>", "~|", "~&", "<="
    left: object
    right: object

    def __repr__(self):
        return f"({self.left!r} {self.connective} {self.right!r})"


@dataclass
class JunctionFormula:
    connective: str  # "&" or "|"
    operands: list

    def __repr__(self):
        sep = f" {self.connective} "
        return f"({sep.join(map(repr, self.operands))})"


@dataclass
class QuantifiedFormula:
    quantifier: str  # "!" or "?"
    variables: list
    formula: object

    def __repr__(self):
        vars_str = ", ".join(self.variables)
        return f"{self.quantifier}[{vars_str}]: {self.formula!r}"