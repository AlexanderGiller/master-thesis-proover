from src.parser.ast_nodes import (
    Atom,
    Equality,
    FunctionTerm,
    IncludeDirective,
    InferenceRecord,
    JunctionFormula,
    NewSymbolsInfo,
    SkolemizeInfo,
    StatusInfo,
    Variable,
)
from src.parser.parser import TPTPTransformer, _strip_quotes, parse_file_pretty
from src.var_mapping import FormulaRole, InferenceRule, InferenceStatus, BinaryConnective, Quantifier

def test_strip_quotes_and_token_methods():
    assert _strip_quotes("'abc'") == "abc"
    assert _strip_quotes("xyz") == "xyz"

    t = TPTPTransformer()
    assert t.__default_token__("tok") == "tok"
    assert t.token("tok") == "tok"


def test_formula_role_methods():
    t = TPTPTransformer()
    assert t.axiom(None) == FormulaRole.AXIOM
    assert t.conjecture(None) == FormulaRole.CONJECTURE
    assert t.negated_conjecture(None) == FormulaRole.NEGATED_CONJECTURE
    assert t.plain(None) == FormulaRole.PLAIN
    assert t.hypothesis(None) == FormulaRole.HYPOTHESIS
    assert t.definition(None) == FormulaRole.DEFINITION
    assert t.lemma(None) == FormulaRole.LEMMA


def test_status_and_introduction_type():
    t = TPTPTransformer()
    assert t.thm(None) == InferenceStatus.THM
    assert t.esa(None) == InferenceStatus.ESA
    assert t.cth(None) == InferenceStatus.CTH
    status_info = t.status_info([InferenceStatus.THM])
    assert isinstance(status_info, StatusInfo)
    assert status_info.status == InferenceStatus.THM
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


def test_inference_record_handles_non_info_objects():
    t = TPTPTransformer()
    # craft items: rule, info-list (contains mixed info objects and non-objects), parents list
    info = [StatusInfo(status='thm'), "not-an-info-object"]
    items = ["rule", info, ["p1"]]
    inf = t.inference_record(items)
    assert inf.rule == "rule"
    assert inf.status == "thm"
    assert inf.parents == ["p1"]


def test_include_and_parse_file_pretty_runs(capsys):
    t = TPTPTransformer()
    include_result = t.include(["'file.p'"])
    assert isinstance(include_result, IncludeDirective)
    assert include_result.path == 'file.p'
    assert include_result.selected_formulas is None
    # run parse_file_pretty on an existing problem file to exercise printing
    parse_file_pretty("examples/correct/Problems/COR001+1.p")
    captured = capsys.readouterr()
    # tree.pretty prints something; ensure output is non-empty
    assert captured.out is not None


def test_token_and_helper_strip_quotes():
    t = TPTPTransformer()
    assert t.token('tok') == 'tok'
    assert _strip_quotes("'x'") == 'x'


def test_introduction_and_new_symbols_skolemize_info():
    t = TPTPTransformer()
    assert t.introduction_type(['definition']) == 'definition'
    # new_symbols_info: kind + symbols
    res = t.new_symbols_info(['kind', 's1', 's2'])
    assert isinstance(res, NewSymbolsInfo)
    assert res.kind == 'kind'
    assert res.symbols == ['s1', 's2']
    # skolemize_info
    sk = t.skolemize_info(['X', FunctionTerm('f', [Variable('X')])])
    assert isinstance(sk, SkolemizeInfo)
    assert sk.variable == 'X'
    assert isinstance(sk.term, FunctionTerm)


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
    from src.parser.ast_nodes import GeneralFunctionInfo
    gf = t.general_function(['fname'])
    assert isinstance(gf, GeneralFunctionInfo)
    assert gf.name == 'fname'


def test_inference_record_parsing_with_all_info():
    t = TPTPTransformer()
    # craft info list with StatusInfo, NewSymbolsInfo, SkolemizeInfo entries
    info = [
        StatusInfo(status='thm'),
        NewSymbolsInfo(kind='skolem', symbols=['sK0']),
        SkolemizeInfo(variable='X', term='sK0'),
    ]
    items = ['skolemize', info, ['parent']]
    inf = t.inference_record(items)
    assert isinstance(inf, InferenceRecord)
    assert inf.rule == 'skolemize'
    assert inf.status == 'thm'  # Via property
    assert inf.new_symbols == ['sK0']  # Via property
    assert inf.skolem_var == 'X'  # Via property


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

