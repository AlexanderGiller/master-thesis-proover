import re
from pathlib import Path

from lark import Lark, Transformer

from .ast_nodes import AnnotatedFormula, InferenceRecord, ProofFile

GRAMMAR_PATH = Path(__file__).parent / "tptp_grammar.lark"


class TPTPTransformer(Transformer):

    # ── Formula role ────────────────────────────────────────────────
    def axiom(self, _):
        return "axiom"

    def conjecture(self, _):
        return "conjecture"

    def negated_conjecture(self, _):
        return "negated_conjecture"

    def plain(self, _):
        return "plain"

    # ── Status ──────────────────────────────────────────────────────
    def status_info(self, items):
        return ("status", str(items[0]))

    def status_value(self, items):
        return str(items[0]) if items else None

    def new_symbols_info(self, items):
        # new_symbols(skolem, [sK0, sK1, ...])
        kind = str(items[0])
        symbols = [str(s) for s in items[1:]]
        return ("new_symbols", kind, symbols)

    def skolemize_info(self, items):
        var = str(items[0])
        term = items[1]  # keep as tree node or stringify
        return ("skolemize", var, term)

    # ── Inference record ─────────────────────────────────────────────
    def parent_list(self, items):
        return [str(i) for i in items]

    def parent_info(self, items):
        return str(items[0])

    def source(self, items):
        return items[0] if items else None

    def dag_source(self, items):
        return items[0]  # either an InferenceRecord or a name string

    def external_source(self, items):
        path = str(items[0])
        ref = str(items[1]) if len(items) > 1 else None
        return ("file", path, ref)

    def internal_source(self, items):
        return ("introduced", str(items[0]))

    def introduction_type(self, items):
        return str(items[0])

    def general_function(self, items):
        return ("general", str(items[0]))

    def inference_info(self, items):
        return list(items)

    def inference_info_item(self, items):
        return items[0]  # unwrap the single child

    def inference_rule(self, items):
        return str(items[0])

    def inference_record(self, items):
        rule = str(items[0])
        info = items[1]  # list from inference_info
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
        # items[0] is the source, items[1] (if present) is useful_info — ignore it
        return items[0] if items else None

    def fof_annotated(self, items):
        name = str(items[0])
        role = items[1]
        formula = items[2]
        source = items[3] if len(items) > 3 else None

        # Only store as inference if it's an actual InferenceRecord
        inference = source if isinstance(source, InferenceRecord) else None
        raw_source = source if not isinstance(source, InferenceRecord) else None

        return AnnotatedFormula(
            name=name, role=role, formula=formula,
            inference=inference, raw_source=raw_source
        )

    def tptp_input(self, items):
        return items[0] if items else None

    def annotated_formula(self, items):
        return items[0]

    def start(self, items):
        return [i for i in items if i is not None]

    def name(self, items):
        return str(items[0])


def parse_file(path: str) -> list[AnnotatedFormula]:
    grammar = GRAMMAR_PATH.read_text()
    parser = Lark(grammar, parser="earley", ambiguity="resolve")
    source = Path(path).read_text()
    tree = parser.parse(source)

    return TPTPTransformer().transform(tree)


def extract_problem_ref(path: str) -> str:
    """Read the 'Proof: <file>' header comment from a proof file."""
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
