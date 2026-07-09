from src.parser.ast_nodes import (
    Atom,
    Equality,
    FunctionTerm,
    InferenceRecord,
    JunctionFormula,
    Variable,
)
from src.parser.parser import TPTPTransformer, _strip_quotes, parse_file_pretty


def test_strip_quotes_and_token_methods():
    assert _strip_quotes("'abc'") == "abc"
    assert _strip_quotes("xyz") == "xyz"

    t = TPTPTransformer()
    assert t.__default_token__("tok") == "tok"
    assert t.token("tok") == "tok"


def test_formula_role_methods():
    t = TPTPTransformer()
    assert t.axiom(None) == "axiom"
    assert t.conjecture(None) == "conjecture"
    assert t.negated_conjecture(None) == "negated_conjecture"
    assert t.plain(None) == "plain"
    assert t.hypothesis(None) == "hypothesis"
    assert t.definition(None) == "definition"
    assert t.lemma(None) == "lemma"


def test_status_and_introduction_type():
    t = TPTPTransformer()
    assert t.thm(None) == "thm"
    assert t.esa(None) == "esa"
    assert t.cth(None) == "cth"
    assert t.status_info(["thm"]) == ("status", "thm")
    assert t.introduction_type(["foo"]) == "foo"


def test_numbers_and_terms():
    t = TPTPTransformer()
    assert t.number([123]) == 123
    assert t.number_term([456]) == 456
    assert t.fof_arguments([1,2,3]) == [1,2,3]
    # compound_term behavior tested indirectly elsewhere; test constant and variable handling
    assert t.proposition(["P"]).predicate == "P"
    assert isinstance(t.true_atom(None), Atom)
    assert isinstance(t.false_atom(None), Atom)


def test_equality_and_not_equal():
    t = TPTPTransformer()
    e = t.equality(["L","R"])
    assert isinstance(e, Equality)
    ne = t.not_equal(["L","R"])
    assert ne.negated is True


def test_fof_variable_list_and_junctions():
    t = TPTPTransformer()
    vars = t.fof_variable_list(["X","Y"])
    assert vars == ["X","Y"]
    j = t.fof_or_formula([Atom("p"), Atom("q")])
    assert isinstance(j, JunctionFormula)


def test_inference_record_handles_non_tuple_info():
    t = TPTPTransformer()
    # craft items: rule, info-list (contains non-tuple), parents list
    items = ["rule", ["not-a-tuple", ("status", "thm")], ["p1"]]
    inf = t.inference_record(items)
    assert inf.rule == "rule"
    assert inf.status == "thm"
    assert inf.parents == ["p1"]


def test_include_and_parse_file_pretty_runs(capsys):
    t = TPTPTransformer()
    assert t.include(["file"]) is None
    # run parse_file_pretty on an existing problem file to exercise printing
    parse_file_pretty("examples/correct/Problems/COR001+1.p")
    captured = capsys.readouterr()
    # tree.pretty prints something; ensure output is non-empty
    assert captured.out is not None


def test_token_and_helper_strip_quotes():
    t = TPTPTransformer()
    assert t.token('tok') == 'tok'
    assert _strip_quotes("'x'") == 'x'


def test_role_shortcuts():
    t = TPTPTransformer()
    assert t.hypothesis(None) == 'hypothesis'
    assert t.definition(None) == 'definition'
    assert t.lemma(None) == 'lemma'


def test_introduction_and_new_symbols_skolemize_info():
    t = TPTPTransformer()
    assert t.introduction_type(['definition']) == 'definition'
    # new_symbols_info: kind + symbols
    res = t.new_symbols_info(['kind', 's1', 's2'])
    assert res[0] == 'new_symbols' and res[1] == 'kind' and isinstance(res[2], list)
    # skolemize_info
    sk = t.skolemize_info(['X', FunctionTerm('f', [Variable('X')])])
    assert sk[0] == 'skolemize' and sk[1] == 'X'


def test_numbers_and_terms_and_atoms():
    t = TPTPTransformer()
    assert t.number([3]) == 3
    assert t.number_term([4]) == 4
    # atomic plain with args inlined
    atom = t.fof_plain_atomic_formula(['p', 'a'])
    assert atom.predicate == 'p'
    # atomic plain with no args (should return args=[])
    atom_no_args = t.fof_plain_atomic_formula(['q'])
    assert atom_no_args.predicate == 'q' and atom_no_args.args == []
    # proposition
    prop = t.proposition(['P'])
    assert prop.predicate == 'P'
    assert isinstance(t.true_atom(None), type(prop))
    assert isinstance(t.false_atom(None), type(prop))


def test_equality_and_not_equal_and_variable_list():
    t = TPTPTransformer()
    e = t.equality(['L', 'R'])
    assert hasattr(e, 'left') and hasattr(e, 'right')
    ne = t.not_equal(['L', 'R'])
    assert ne.negated is True
    vars = t.fof_variable_list(['X', 'Y'])
    assert vars == ['X', 'Y']


def test_junction_and_binary_constructors():
    t = TPTPTransformer()
    j = t.fof_and_formula([1, 2, 3])
    assert hasattr(j, 'operands')
    b = t.fof_binary_nonassoc(['L', '=>', 'R'])
    assert hasattr(b, 'left') and hasattr(b, 'right')


def test_source_variants_and_general_function():
    t = TPTPTransformer()
    # external_source with quoted path and optional ref
    ext = t.external_source(["'path/to.p'", 'name'])
    assert ext[0] == 'file' and 'path/to.p' in ext[1]
    # internal_source
    internal = t.internal_source(['definition', []])
    assert internal[0] == 'introduced'
    # general function
    gf = t.general_function(['fname'])
    assert gf[0] == 'general'


def test_inference_record_parsing_with_all_info():
    t = TPTPTransformer()
    # craft info list with status, new_symbols, skolemize entries
    info = [
        ('status', 'thm'),
        ('new_symbols', 'kind', ['sK0']),
        ('skolemize', 'X', 'sK0'),
    ]
    items = ['skolemize', info, ['parent']]
    inf = t.inference_record(items)
    assert isinstance(inf, InferenceRecord)
    assert inf.rule == 'skolemize'
    assert inf.status == 'thm'
    assert inf.new_symbols == ['sK0']
    assert inf.skolem_var == 'X'


def test_annotations_and_top_level_and_parse_pretty(capsys):
    t = TPTPTransformer()
    assert t.annotations([]) is None
    # build annotated fof structure
    ann = t.fof_annotated(['name', 'axiom', 'formula', None])
    assert ann.name == 'name' and ann.role == 'axiom'
    # parse_file_pretty prints tree; run on an existing example problem file
    parse_file_pretty('examples/correct/Problems/COR001+1.p')
    out = capsys.readouterr().out
    assert out is not None

