from src.checker.junction_checker import check_excluded_middle
from src.parser.ast_nodes import AnnotatedFormula, Atom, Equality, InferenceRecord, StatusInfo
from src.var_mapping import BinaryConnective, FormulaRole, InferenceRule, InferenceStatus
from src.parser.ast_nodes import JunctionFormula


def test_excluded_middle_accepts_equality_or_its_negation():
    step = AnnotatedFormula(
        name="s",
        role=FormulaRole.PLAIN,
        formula=JunctionFormula(
            BinaryConnective.OR,
            [
                Equality(left=Atom("p", []), right=Atom("q", []), negated=False),
                Equality(left=Atom("p", []), right=Atom("q", []), negated=True),
            ],
        ),
        inference=InferenceRecord(
            rule=InferenceRule.EXCLUDED_MIDDLE,
            info=[StatusInfo(status=InferenceStatus.THM)],
            parents=["a"],
        ),
    )

    assert check_excluded_middle(step) == []

