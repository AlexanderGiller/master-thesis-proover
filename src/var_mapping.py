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
    CTH = "cth"  # counter-theorem (used for negated_conjecture step)
    ESA = "esa"  # equisatisfiable
    SAT = "sat"  # satisfiable
    UNSAT = "unsat"  # unsatisfiable
    WTH = "wth"  # with theorem
    # sat, unsat and wtf not part of 2026ProoVer benchmark, but included due to completeness of SZS ontology


class InferenceRule(StrEnum):
    """Common inference rule names seen in TSTP proofs."""

    NEGATED_CONJECTURE = "negated_conjecture"
    DEDUCTION = "deduction"
    INSTANTIATE = "instantiate"
    EXISTENTIAL_GEN = "existential_gen"
    RESOLUTION = "resolution"
    PARAMODULATION = "paramodulation"
    REFLEXIVITY = "reflexivity"
    TRANSITIVITY = "transitivity"
    REWRITE = "rewrite"
    SKOLEMIZE = "skolemize"
    CNF_TRANSFORMATION = "cnf_transformation"
    RECTIFY = "rectify"
    FLATTENING = "flattening"
    MODUS_PONENS = "modus_ponens"
    CONJUNCTION = "conjunction"
    SPLIT_CONJUNCT = "split_conjunct"
    COPY = "copy"
    DUPLICATE = "duplicate"
    RENAME_VARIABLE = "rename_variable"
    DOUBLE_NEGATION = "double_negation"
    REMOVE_DOUBLE_NEGATION = "remove_double_negation"
    WEAKEN = "weaken"
    COMMUTE = "commute"
    EXCLUDED_MIDDLE = "excluded_middle"


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
