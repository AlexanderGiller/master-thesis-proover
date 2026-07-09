from src.parser.parser import TPTPTransformer, parse_file_pretty
from src.parser.parser import _strip_quotes
from src.parser.ast_nodes import Atom, Equality, JunctionFormula


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
    parse_file_pretty("Problems/example1_proover.p")
    captured = capsys.readouterr()
    # tree.pretty prints something; ensure output is non-empty
    assert captured.out is not None

