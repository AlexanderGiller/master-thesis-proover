# tests/test_skolem_checker.py
import pytest

from src.checker.skolem_checker import SkolemError, check_skolemization
from src.parser.ast_nodes import AnnotatedFormula, InferenceRecord


def make_skolem_step(
    rule="skolemize",
    status="esa",
    new_symbols=None,
    skolem_var="X",
    skolem_term="sK0",
    parents=None,
):
    inf = InferenceRecord(
        rule=rule,
        status=status,
        parents=parents or ["ax1"],
        new_symbols=new_symbols or ["sK0"],
        skolem_var=skolem_var,
        skolem_term=skolem_term,
    )
    return AnnotatedFormula(name="ax1_sk", role="plain", formula=None, inference=inf)


def make_parent():
    # ?[X] : mortal(X) — minimal stand-in; skolem checker uses the tree
    # so we pass None and test only annotation-level checks here
    return AnnotatedFormula(name="ax1", role="axiom", formula=None)


class TestSkolemCheckerAnnotations:
    """Tests that verify annotation-level rules without needing a full parse tree."""

    def test_wrong_rule_name_raises(self):
        step = make_skolem_step(rule="resolution")
        with pytest.raises(SkolemError, match="Expected rule 'skolemize'"):
            check_skolemization(step, make_parent())

    def test_wrong_status_raises(self):
        step = make_skolem_step(status="thm")
        with pytest.raises(SkolemError, match="status 'esa'"):
            check_skolemization(step, make_parent())

    def test_no_new_symbols_raises(self):
        step = make_skolem_step(new_symbols=[])
        with pytest.raises(SkolemError, match="exactly one Skolem symbol"):
            check_skolemization(step, make_parent())

    def test_two_new_symbols_raises(self):
        step = make_skolem_step(new_symbols=["sK0", "sK1"])
        with pytest.raises(SkolemError, match="exactly one Skolem symbol"):
            check_skolemization(step, make_parent())

    def test_missing_skolem_var_raises(self):
        step = make_skolem_step(skolem_var=None)
        with pytest.raises(SkolemError, match="Missing skolemize"):
            check_skolemization(step, make_parent())

    def test_missing_skolem_term_raises(self):
        step = make_skolem_step(skolem_term=None)
        with pytest.raises(SkolemError, match="Missing skolemize"):
            check_skolemization(step, make_parent())
