from src.checker.dependency_checker import (
    check_conjecture_not_assumed,
    check_no_circular_dependencies,
)
from src.parser.ast_nodes import AnnotatedFormula, Atom, Constant, InferenceRecord, StatusInfo
from src.var_mapping import FormulaRole, InferenceRule, InferenceStatus


def annotated(name, parents=None, role=FormulaRole.PLAIN, rule=InferenceRule.DEDUCTION):
    inference = (
        InferenceRecord(rule, [StatusInfo(InferenceStatus.THM)], parents)
        if parents is not None
        else None
    )
    return AnnotatedFormula(name, role, Atom("p", [Constant("a")]), inference)


class TestNoCircularDependencies:
    def test_acyclic_chain_is_accepted(self):
        steps = [
            annotated("s1"),
            annotated("s2", ["s1"]),
            annotated("s3", ["s2"]),
            annotated("s4", ["s3"]),
        ]
        assert check_no_circular_dependencies(steps) == []

    def test_direct_cycle_is_detected(self):
        steps = [annotated("s1", ["s2"]), annotated("s2", ["s1"])]
        issues = check_no_circular_dependencies(steps)
        assert len(issues) == 1
        assert "circular dependency" in issues[0].reason

    def test_four_step_cycle_is_detected(self):
        # s1 depends on s2, s2 on s3, s3 on s4, s4 on s1
        steps = [
            annotated("s1", ["s2"]),
            annotated("s2", ["s3"]),
            annotated("s3", ["s4"]),
            annotated("s4", ["s1"]),
        ]
        issues = check_no_circular_dependencies(steps)
        assert len(issues) == 1
        reason = issues[0].reason
        for name in ("s1", "s2", "s3", "s4"):
            assert name in reason

    def test_self_referencing_step_is_detected(self):
        steps = [annotated("s1", ["s1"])]
        issues = check_no_circular_dependencies(steps)
        assert len(issues) == 1

    def test_dangling_parent_reference_is_ignored(self):
        steps = [annotated("s1", ["unknown_step"])]
        assert check_no_circular_dependencies(steps) == []

    def test_shared_ancestor_without_cycle_is_accepted(self):
        steps = [
            annotated("s1"),
            annotated("s2", ["s1"]),
            annotated("s3", ["s1"]),
            annotated("s4", ["s2", "s3"]),
        ]
        assert check_no_circular_dependencies(steps) == []


class TestConjectureNotAssumed:
    def test_valid_negated_conjecture_derivation_is_accepted(self):
        steps = [
            annotated("c", role=FormulaRole.CONJECTURE),
            annotated(
                "s1",
                ["c"],
                role=FormulaRole.NEGATED_CONJECTURE,
                rule=InferenceRule.NEGATED_CONJECTURE,
            ),
        ]
        assert check_conjecture_not_assumed(steps) == []

    def test_step_directly_assuming_conjecture_is_rejected(self):
        steps = [
            annotated("c", role=FormulaRole.CONJECTURE),
            annotated(
                "s1",
                ["c"],
                role=FormulaRole.NEGATED_CONJECTURE,
                rule=InferenceRule.NEGATED_CONJECTURE,
            ),
            # Later step illegitimately treats the (un-negated) conjecture as a premise.
            annotated("s2", ["c"]),
        ]
        issues = check_conjecture_not_assumed(steps)
        assert len(issues) == 1
        assert issues[0].step_name == "s2"
        assert "begs the question" in issues[0].reason

    def test_negated_conjecture_role_with_wrong_rule_is_still_flagged(self):
        # A step masquerading with role negated_conjecture but not actually
        # using the negated_conjecture inference rule does not get the pass.
        steps = [
            annotated("c", role=FormulaRole.CONJECTURE),
            annotated(
                "s1",
                ["c"],
                role=FormulaRole.NEGATED_CONJECTURE,
                rule=InferenceRule.COPY,
            ),
        ]
        issues = check_conjecture_not_assumed(steps)
        assert len(issues) == 1
        assert issues[0].step_name == "s1"

    def test_no_conjecture_present_yields_no_issues(self):
        steps = [annotated("s1"), annotated("s2", ["s1"])]
        assert check_conjecture_not_assumed(steps) == []
