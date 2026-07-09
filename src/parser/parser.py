import re
from pathlib import Path

from lark import Lark, Transformer

from .ast_nodes import (
    AnnotatedFormula,
    Atom,
    BinaryFormula,
    Constant,
    Equality,
    FunctionTerm,
    InferenceRecord,
    JunctionFormula,
    Negation,
    ProofFile,
    QuantifiedFormula,
    Variable,
)

GRAMMAR_PATH = Path(__file__).parent / "tptp_grammar.lark"


def _strip_quotes(token_str: str) -> str:
    """Strip single quotes from SINGLE_QUOTED tokens."""
    s = str(token_str)
    if s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    return s


class TPTPTransformer(Transformer):

    def __default_token__(self, token):
        return str(token)

    def token(self, token):
        return str(token)

    # ── Formula role ─────────────────────────────────────────────────
    def axiom(self, _):
        return "axiom"

    def conjecture(self, _):
        return "conjecture"

    def negated_conjecture(self, _):
        return "negated_conjecture"

    def plain(self, _):
        return "plain"

    def hypothesis(self, _):
        return "hypothesis"

    def definition(self, _):
        return "definition"

    def lemma(self, _):
        return "lemma"

    # ── Status / introduction type ────────────────────────────────────
    def thm(self, _):   return "thm"
    def esa(self, _):   return "esa"
    def cth(self, _):   return "cth"
    def sat(self, _):   return "sat"
    def unsat(self, _): return "unsat"
    def wth(self, _):   return "wth"

    def status_info(self, items):
        return ("status", items[0])

    def introduction_type(self, items):
        return str(items[0])

    def new_symbols_info(self, items):
        kind = str(items[0])
        symbols = [str(s) for s in items[1:]]
        return ("new_symbols", kind, symbols)

    def skolemize_info(self, items):
        var = str(items[0])
        term = items[1]
        return ("skolemize", var, term)

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
        functor = items[0]
        # items = [functor, arg1, arg2, ...] because fof_arguments is inlined
        args = list(items[1:])
        return FunctionTerm(functor=functor, args=args)

    def number_term(self, items):
        return items[0]

    def fof_arguments(self, items):
        return list(items)

    # ── Atomic formulas ─────────────────────────────────────────────────
    def fof_plain_atomic_formula(self, items):
        if len(items) >= 2:
            # items = [predicate, arg1, arg2, ...] because fof_arguments is inlined
            predicate = items[0]
            args = list(items[1:])
            return Atom(predicate=predicate, args=args)
        return Atom(predicate=items[0], args=[])

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
        return "?"

    def forall(self, _):
        return "!"

    def fof_variable_list(self, items):
        return [str(v) for v in items]

    def fof_quantified_formula(self, items):
        quantifier, variables, formula = items
        return QuantifiedFormula(quantifier=quantifier, variables=variables, formula=formula)

    # ── Binary connectives ────────────────────────────────────────────────
    def implies(self, _):    return "=>"
    def implied_by(self, _): return "<="
    def iff(self, _):        return "<=>"
    def xor(self, _):        return "<~>"
    def nor(self, _):        return "~|"
    def nand(self, _):       return "~&"

    def fof_binary_nonassoc(self, items):
        left, connective, right = items
        return BinaryFormula(connective=connective, left=left, right=right)

    def fof_and_formula(self, items):
        return JunctionFormula(connective="&", operands=list(items))

    def fof_or_formula(self, items):
        return JunctionFormula(connective="|", operands=list(items))

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
        return ("general", str(items[0]))

    def inference_info(self, items):
        return list(items)

    def inference_info_item(self, items):
        return items[0]

    def inference_rule(self, items):
        return _strip_quotes(items[0])

    def inference_record(self, items):
        rule = str(items[0])
        info = items[1]
        parents = items[2] if len(items) > 2 else []

        status, new_syms, sk_var, sk_term = None, None, None, None
        for item in info:
            if not isinstance(item, tuple):
                continue
            if item[0] == "status":
                status = item[1]
            elif item[0] == "new_symbols":
                new_syms = item[2]
            elif item[0] == "skolemize":
                sk_var, sk_term = item[1], item[2]

        return InferenceRecord(
            rule=rule,
            status=status,
            parents=parents,
            new_symbols=new_syms,
            skolem_var=sk_var,
            skolem_term=sk_term,
        )

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
        # First item is the included filename, second (if present) is the
        # optional formula-selection list. Not resolved here — just flagged
        # so callers can decide whether to inline it themselves.
        return None

    def tptp_input(self, items):
        return items[0] if items else None

    def annotated_formula(self, items):
        return items[0]

    def start(self, items):
        return [i for i in items if i is not None]

    def name(self, items):
        return _strip_quotes(items[0])


def parse_file(path: str) -> list[AnnotatedFormula]:
    grammar = GRAMMAR_PATH.read_text()
    parser = Lark(grammar, parser="earley", ambiguity="resolve")
    source = Path(path).read_text()
    tree = parser.parse(source)

    return TPTPTransformer().transform(tree)

def parse_file_pretty(path: str):
    grammar = GRAMMAR_PATH.read_text()
    parser = Lark(grammar, parser="earley", ambiguity="resolve")
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
