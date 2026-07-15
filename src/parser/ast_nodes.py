from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StatusInfo:
    """Represents status(...) in inference info."""
    status: str  # "thm", "esa", "cth", etc.


@dataclass
class NewSymbolsInfo:
    """Represents new_symbols(kind, [...]) in inference info."""
    kind: str  # e.g., "skolem", "general"
    symbols: list[str]


@dataclass
class SkolemizeInfo:
    """Represents skolemize(Var, Term) in inference info."""
    variable: str
    term: object  # Parsed term node


@dataclass
class GeneralFunctionInfo:
    """Represents general_function(...) in inference info."""
    name: str
    args: Optional[list] = None


@dataclass
class InferenceRecord:
    rule: str  # e.g. "skolemize", "resolution"
    info: list  # List of StatusInfo, NewSymbolsInfo, SkolemizeInfo, GeneralFunctionInfo
    parents: list[str]

    # Convenience properties for backward compatibility
    @property
    def status(self) -> Optional[str]:
        """Extract status from info list."""
        for item in self.info:
            if isinstance(item, StatusInfo):
                return item.status
        return None

    @property
    def new_symbols(self) -> Optional[list[str]]:
        """Extract new_symbols from info list."""
        for item in self.info:
            if isinstance(item, NewSymbolsInfo):
                return item.symbols
        return None

    @property
    def skolem_var(self) -> Optional[str]:
        """Extract skolemize variable from info list."""
        for item in self.info:
            if isinstance(item, SkolemizeInfo):
                return item.variable
        return None

    @property
    def skolem_term(self) -> Optional[object]:
        """Extract skolemize term from info list."""
        for item in self.info:
            if isinstance(item, SkolemizeInfo):
                return item.term
        return None


@dataclass
class AnnotatedFormula:
    name: str
    role: str  # "axiom", "plain", etc.
    formula: object  # parse tree node
    inference: Optional[InferenceRecord] = None
    raw_source: Optional[str] = None


@dataclass
class IncludeDirective:
    """Represents an include(...) directive in TPTP files."""
    path: str
    selected_formulas: Optional[list[str]] = None  # Optional filter list


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