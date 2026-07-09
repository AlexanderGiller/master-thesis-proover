from src.parser.ast_nodes import (
    Atom,
    BinaryFormula,
    Constant,
    Equality,
    FunctionTerm,
    JunctionFormula,
    Negation,
    QuantifiedFormula,
    Variable,
)


def test_repr_variable_and_constant():
    v = Variable("X")
    c = Constant("a")
    assert repr(v) == "X"
    assert repr(c) == "a"


def test_repr_function_term_empty_and_nested():
    f0 = FunctionTerm("f", [])
    assert repr(f0) == "f()"
    f1 = FunctionTerm("g", [Constant("a"), Variable("X")])
    assert "g(a" in repr(f1) and "X" in repr(f1)


def test_repr_atom_no_args_and_with_args():
    a0 = Atom("p", args=[])
    assert repr(a0) == "p"
    a1 = Atom("p", args=[Constant("a")])
    assert repr(a1).startswith("p(") and "a" in repr(a1)


def test_repr_equality_and_negated():
    e = Equality(Constant("a"), Constant("b"))
    assert "=" in repr(e)
    en = Equality(Constant("a"), Constant("b"), negated=True)
    assert "!=" in repr(en)


def test_repr_negation_and_binary_and_junction():
    n = Negation(Atom("p", args=[]))
    assert repr(n).startswith("~")
    b = BinaryFormula("=>", Atom("p", args=[]), Atom("q", args=[]))
    assert "=>" in repr(b)
    j = JunctionFormula("&", [Atom("p", args=[]), Atom("q", args=[])])
    s = repr(j)
    assert "&" in s and s.startswith("(") and s.endswith(")")


def test_repr_quantified_formula():
    q = QuantifiedFormula("!", ["X", "Y"], Atom("p", args=[Variable("X"), Variable("Y")]))
    s = repr(q)
    assert s.startswith("!") and ":" in s and "p(" in s

