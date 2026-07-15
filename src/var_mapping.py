from enum import StrEnum


class FormulaRole(StrEnum):
    """TPTP formula roles (TPTP syntax BNF, %-comment role list)."""

    AXIOM = "axiom"
    CONJECTURE = "conjecture"
    NEGATED_CONJECTURE = "negated_conjecture"
    PLAIN = "plain"
    HYPOTHESIS = "hypothesis"
    DEFINITION = "definition"
    LEMMA = "lemma"


class InferenceStatus(StrEnum):
    """SZS-style status codes used inside inference(...) annotations."""

    THM = "thm"  # theorem
    CTH = "cth"  # co-theorem (used for negated_conjecture step)
    ESA = "esa"  # equisatisfiable
    SAT = "sat"
    UNSAT = "unsat"
    WTH = "wth"  # with theorem


class InferenceRule(StrEnum):
    """Common inference rule names seen in TSTP proofs."""

    NEGATED_CONJECTURE = "negated_conjecture"
    DEDUCTION = "deduction"
    RESOLUTION = "resolution"
    PARAMODULATION = "paramodulation"
    SKOLEMIZE = "skolemize"  # NB: TPTP spells it with an 's'
    CNF_TRANSFORMATION = "cnf_transformation"
    RECTIFY = "rectify"
    FLATTENING = "flattening"


class Quantifier(StrEnum):
    """Quantifier symbols used in TPTP formulas."""

    UNIVERSAL = "!"
    EXISTENTIAL = "?"


class BinaryConnective(StrEnum):
    """Binary connective symbols used in TPTP formulas."""

    AND = "&"
    OR = "|"
    IMPLIES = "=>"
    IMPLIED = "<="
    IFF = "<=>"
    XOR = "<~>"
    NOR = "~|"
    NAND = "~&"


class SZSStatus(StrEnum):
    """SZS ontology status values (top-level problem verdict)."""

    THEOREM = "Theorem"
    COUNTERSATISFIABLE = "CounterSatisfiable"
    UNSATISFIABLE = "Unsatisfiable"
    SATISFIABLE = "Satisfiable"
    UNKNOWN = "Unknown"


class FileExt(StrEnum):
    PROBLEM = ".p"
    SOLUTION = ".s"


class Score:
    CORRECT_REJECT: int = 2
    CORRECT_ACCEPT: int = 1
    GIVING_UP: int = 0
    WRONG_REJECT: int = -1
    WRONG_ACCEPT: int = -10
