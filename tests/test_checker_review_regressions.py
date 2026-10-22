"""Regression tests for defects found in the final review of the checkers.

Each test states a step that is not entailed by its parents (and must be
rejected) next to a correct variant (which must still be accepted).
"""

from pathlib import Path

import pytest

from src.checker.clausal_checker import check_resolution
from src.checker.existential_gen_checker import check_existential_gen
from src.checker.instantiate_checker import check_instantiate
from src.parser.parser import parse_file


def _steps(tmp_path: Path, text: str) -> dict:
    f = tmp_path / "steps.p"
    f.write_text(text, encoding="utf-8")
    return {s.name: s for s in parse_file(str(f))}


def test_resolution_applies_the_unifier_completely(tmp_path):
    # Unifier {X -> f(Z), Z -> a}: the resolvent is q(f(a)), not ![Z]: q(f(Z)).
    st = _steps(
        tmp_path,
        """fof(c1, axiom, ![X]: (~p(X,X) | q(X))).
fof(c2, axiom, ![Z]: p(f(Z), f(a))).
fof(wrong, plain, ![Z]: q(f(Z)), inference(resolution,[status(thm)],[c1,c2])).
fof(right, plain, q(f(a)), inference(resolution,[status(thm)],[c1,c2])).
""",
    )
    assert check_resolution(st["wrong"], st["c1"], st["c2"]) != []
    assert check_resolution(st["right"], st["c1"], st["c2"]) == []


def test_instantiate_detects_capture_below_negation(tmp_path):
    # ![X]: ?[Y]: ~p(X,Y) does not entail ?[Y]: ~p(Y,Y) (Y would be captured).
    st = _steps(
        tmp_path,
        """fof(par, axiom, ![X]: ?[Y]: ~p(X,Y)).
fof(wrong, plain, ?[Y]: ~p(Y,Y), inference(instantiate,[status(thm)],[par])).
fof(right, plain, ?[Y]: ~p(a,Y), inference(instantiate,[status(thm)],[par])).
""",
    )
    assert check_instantiate(st["wrong"], st["par"]) != []
    assert check_instantiate(st["right"], st["par"]) == []


def test_instantiate_rejects_renaming_into_an_inner_binder(tmp_path):
    # Renaming the kept X to Y, which is bound inside, would capture it.
    st = _steps(
        tmp_path,
        """fof(par, axiom, ![X]: ?[Y]: p(X,Y)).
fof(wrong, plain, ![Y]: ?[Y]: p(Y,Y), inference(instantiate,[status(thm)],[par])).
""",
    )
    assert check_instantiate(st["wrong"], st["par"]) != []


@pytest.mark.parametrize(
    ("parent", "accepted"),
    [("(p(a) & q)", True), ("(p(a) | q)", False)],
)
def test_existential_gen_from_a_junction(tmp_path, parent, accepted):
    # From p(a) & q one may infer ?[X]: p(X); from p(a) | q one may not.
    st = _steps(
        tmp_path,
        f"""fof(par, axiom, {parent}).
fof(s, plain, ?[X]: p(X), inference(existential_gen,[status(thm)],[par])).
""",
    )
    assert (check_existential_gen(st["s"], st["par"]) == []) is accepted


def test_existential_gen_with_renamed_preserved_variable(tmp_path):
    st = _steps(
        tmp_path,
        """fof(par, axiom, ?[Y]: p(a,Y)).
fof(s, plain, ?[X,Z]: p(X,Z), inference(existential_gen,[status(thm)],[par])).
""",
    )
    assert check_existential_gen(st["s"], st["par"]) == []
