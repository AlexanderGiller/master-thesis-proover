from enum import Enum

class FormulaRole(str, Enum):
    """TPTP formula roles (TPTP syntax BNF, %-comment role list)."""
    AXIOM = "axiom"
    CONJECTURE = "conjecture"
    NEGATED_CONJECTURE = "negated_conjecture"
    PLAIN = "plain"
    HYPOTHESIS = "hypothesis"
    DEFINITION = "definition"
    LEMMA = "lemma"

class InferenceStatus(str, Enum):
    """SZS-style status codes used inside inference(...) annotations."""
    THM = "thm"  # theorem
    CTH = "cth"  # co-theorem (used for negated_conjecture step)
    ESA = "esa"  # equisatisfiable
    SAT = "sat"
    UNSAT = "unsat"
    WTH = "wth"  # with theorem

class InferenceRule(str, Enum):
    """Common inference rule names seen in TSTP proofs."""
    NEGATED_CONJECTURE = "negated_conjecture"
    DEDUCTION = "deduction"
    RESOLUTION = "resolution"
    PARAMODULATION = "paramodulation"
    SKOLEMIZE = "skolemize"   # NB: TPTP spells it with an 's'
    CNF_TRANSFORMATION = "cnf_transformation"
    RECTIFY = "rectify"
    FLATTENING = "flattening"


class SZSStatus(str, Enum):
    """SZS ontology status values (top-level problem verdict)."""
    THEOREM = "Theorem"
    COUNTERSATISFIABLE = "CounterSatisfiable"
    UNSATISFIABLE = "Unsatisfiable"
    SATISFIABLE = "Satisfiable"
    UNKNOWN = "Unknown"


class FileExt(str, Enum):
    PROBLEM = ".p"
    SOLUTION = ".s"

class Score:
    CORRECT_REJECT: int = 2
    CORRECT_ACCEPT: int = 1
    GIVING_UP: int = 0
    WRONG_REJECT: int = -1
    WRONG_ACCEPT: int = -10