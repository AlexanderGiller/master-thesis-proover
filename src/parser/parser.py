import re
from functools import lru_cache
from pathlib import Path

from lark import Lark, Transformer

from src.var_mapping import (
    BinaryConnective,
    FormulaRole,
    InferenceStatus,
    Quantifier,
)

from .ast_nodes import (
    AnnotatedFormula,
    Atom,
    BinaryFormula,
    Constant,
    Equality,
    FunctionTerm,
    GeneralFunctionInfo,
    IncludeDirective,
    InferenceRecord,
    JunctionFormula,
    Negation,
    NewSymbolsInfo,
    ProofFile,
    QuantifiedFormula,
    SkolemizeInfo,
    StatusInfo,
    Variable,
)

GRAMMAR_PATH = Path(__file__).parent / "tptp_grammar.lark"


def _strip_quotes(token_str: str) -> str:
    """Strip single quotes from SINGLE_QUOTED tokens."""
    s = str(token_str)
    if s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    return s


def _unwrap_single_list(items):
    """Flatten parser items when an inlined rule still arrives as a single nested list.

    Lark may hand transformer methods either:
    - [a, b, c]
    - [[a, b, c]]
    - a single scalar for inlined single-item productions
    This helper normalizes the first two shapes.
    """
    if len(items) == 1 and isinstance(items[0], list):
        return items[0]
    return items


def _extract_functor_and_args(items: list) -> tuple[str, list]:
    """Extract functor and arguments from parser items.
    
    Handles both direct item sequences and nested lists from inlined rules.
    Returns (functor, args).
    """
    items = _unwrap_single_list(items)
    functor = items[0]
    args = list(items[1:])
    # Handle case where arguments arrive as a single nested list
    if len(args) == 1 and isinstance(args[0], list):
        args = args[0]
    return functor, args


@lru_cache(maxsize=1)
def _get_parser():
    """Get or create the Lark parser (cached)."""
    grammar = GRAMMAR_PATH.read_text()
    return Lark(grammar, parser="earley", ambiguity="resolve")


class TPTPTransformer(Transformer):

    def __default_token__(self, token):
        return str(token)

    def token(self, token):
        return str(token)

    # ── Formula role ─────────────────────────────────────────────────
    def axiom(self, _):
        return FormulaRole.AXIOM

    def conjecture(self, _):
        return FormulaRole.CONJECTURE

    def negated_conjecture(self, _):
        return FormulaRole.NEGATED_CONJECTURE

    def plain(self, _):
        return FormulaRole.PLAIN

    def hypothesis(self, _):
        return FormulaRole.HYPOTHESIS

    def definition(self, _):
        return FormulaRole.DEFINITION

    def lemma(self, _):
        return FormulaRole.LEMMA

    # ── Status / introduction type ────────────────────────────────────
    def thm(self, _):   return InferenceStatus.THM
    def esa(self, _):   return InferenceStatus.ESA
    def cth(self, _):   return InferenceStatus.CTH
    def sat(self, _):   return InferenceStatus.SAT
    def unsat(self, _): return InferenceStatus.UNSAT
    def wth(self, _):   return InferenceStatus.WTH

    def status_info(self, items):
        return StatusInfo(status=items[0])

    def introduction_type(self, items):
        return str(items[0])

    def new_symbols_info(self, items):
        kind = str(items[0])
        symbols = [str(s) for s in items[1:]]
        return NewSymbolsInfo(kind=kind, symbols=symbols)

    def skolemize_info(self, items):
        var = str(items[0])
        term = items[1]
        return SkolemizeInfo(variable=var, term=term)

    # ── Terms ──────────────────────────────────────────────────────────
    def functor(self, items):
        return _strip_quotes(items[0])

    def number(self, items):
        return items[0]

    def variable_term(self, items):
        return Variable(str(items[0]))

    def constant_term(self, items):
        return Constant(items[0])

    def compound_term(self, items):
        functor, args = _extract_functor_and_args(items)
        return FunctionTerm(functor=functor, args=args)

    def number_term(self, items):
        return items[0]

    def fof_arguments(self, items):
        return list(items)

    # ── Atomic formulas ─────────────────────────────────────────────────
    def fof_plain_atomic_formula(self, items):
        if len(_unwrap_single_list(items)) >= 2:
            predicate, args = _extract_functor_and_args(items)
            return Atom(predicate=predicate, args=args)
        # Single item: proposition without arguments
        return Atom(predicate=_unwrap_single_list(items)[0], args=[])

    def proposition(self, items):
        return Atom(predicate=items[0], args=[])

    def true_atom(self, _):
        return Atom(predicate="$true", args=[])

    def false_atom(self, _):
        return Atom(predicate="$false", args=[])

    def equality(self, items):
        return Equality(left=items[0], right=items[1])

    def not_equal(self, items):
        return Equality(left=items[0], right=items[1], negated=True)

    # ── Negation, quantifiers ────────────────────────────────────────────
    def negation(self, items):
        return Negation(items[0])

    def exists(self, _):
        return Quantifier.EXISTENTIAL

    def forall(self, _):
        return Quantifier.UNIVERSAL

    def fof_variable_list(self, items):
        return [str(v) for v in items]

    def fof_quantified_formula(self, items):
        quantifier, variables, formula = items
        if not isinstance(variables, list):
            variables = [str(variables)]
        return QuantifiedFormula(quantifier=quantifier, variables=variables, formula=formula)

    # ── Binary connectives ────────────────────────────────────────────────
    def implies(self, _):    return BinaryConnective.IMPLIES
    def implied_by(self, _): return BinaryConnective.IMPLIED
    def iff(self, _):        return BinaryConnective.IFF
    def xor(self, _):        return BinaryConnective.XOR
    def nor(self, _):        return BinaryConnective.NOR
    def nand(self, _):       return BinaryConnective.NAND

    def fof_binary_nonassoc(self, items):
        left, connective, right = items
        if connective == BinaryConnective.IMPLIED:
            # normalize to a single canonical direction
            return BinaryFormula(connective=BinaryConnective.IMPLIES, left=right, right=left)
        return BinaryFormula(connective=connective, left=left, right=right)

    def fof_and_formula(self, items):
        return JunctionFormula(connective=BinaryConnective.AND, operands=list(items))

    def fof_or_formula(self, items):
        return JunctionFormula(connective=BinaryConnective.OR, operands=list(items))

    # ── Inference record ──────────────────────────────────────────────────
    def parent_list(self, items):
        return [str(i) for i in items]

    def parent_info(self, items):
        return str(items[0])

    def source(self, items):
        return items[0] if items else None

    def dag_source(self, items):
        return items[0]

    def external_source(self, items):
        path = _strip_quotes(items[0])
        ref = _strip_quotes(items[1]) if len(items) > 1 else None
        return ("file", path, ref)

    def internal_source(self, items):
        return ("introduced", items[0])

    def general_function(self, items):
        return GeneralFunctionInfo(name=str(items[0]), args=items[1:] if len(items) > 1 else None)

    def inference_info(self, items):
        return list(items)

    def inference_info_item(self, items):
        return items[0]

    def inference_rule(self, items):
        return _strip_quotes(items[0])

    def inference_record(self, items):
        rule = str(items[0])
        info = items[1]  # List of info objects (StatusInfo, NewSymbolsInfo, etc.)
        parents = items[2] if len(items) > 2 else []

        return InferenceRecord(rule=rule, info=info, parents=parents)

    def annotations(self, items):
        return items[0] if items else None

    # ── Top level ─────────────────────────────────────────────────────────
    def fof_annotated(self, items):
        name = str(items[0])
        role = items[1]
        formula = items[2]
        source = items[3] if len(items) > 3 else None

        inference = source if isinstance(source, InferenceRecord) else None
        raw_source = source if not isinstance(source, InferenceRecord) else None

        return AnnotatedFormula(
            name=name, role=role, formula=formula,
            inference=inference, raw_source=raw_source
        )

    def include(self, items):
        """Parse include directive and return IncludeDirective object."""
        path = _strip_quotes(items[0])
        selected = [_strip_quotes(str(s)) for s in items[1:]] if len(items) > 1 else None
        return IncludeDirective(path=path, selected_formulas=selected)

    def tptp_input(self, items):
        return items[0] if items else None

    def annotated_formula(self, items):
        return items[0]

    def start(self, items):
        # Filter out None values, but keep IncludeDirective and AnnotatedFormula
        return [i for i in items if i is not None]

    def name(self, items):
        return _strip_quotes(items[0])


def parse_file(path: str) -> list[AnnotatedFormula | IncludeDirective]:
    parser = _get_parser()
    source = Path(path).read_text()
    tree = parser.parse(source)
    return TPTPTransformer().transform(tree)

def parse_file_pretty(path: str):
    parser = _get_parser()
    source = Path(path).read_text()
    tree = parser.parse(source)
    print(tree.pretty())

def extract_problem_ref(path: str) -> str:
    with open(path) as f:
        for line in f:
            m = re.match(r"%\s*Proof:\s*(\S+)", line)
            if m:
                return m.group(1)
    return ""


def load_proof(proof_path: str) -> ProofFile:
    steps = parse_file(proof_path)
    problem_ref = extract_problem_ref(proof_path)
    return ProofFile(problem_ref=problem_ref, steps=steps)
