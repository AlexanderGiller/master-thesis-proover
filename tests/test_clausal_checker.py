from proof_checker_demo import check_proof_file
from src.checker.clausal_checker import (
    check_paramodulation,
    check_reflexivity,
    check_resolution,
    check_rewrite,
    check_transitivity,
)
from src.parser.ast_nodes import (
    AnnotatedFormula,
    Atom,
    Constant,
    Equality,
    FunctionTerm,
    InferenceRecord,
    JunctionFormula,
    Negation,
    StatusInfo,
    Variable,
    QuantifiedFormula,
)
from src.var_mapping import BinaryConnective, FormulaRole, InferenceRule, InferenceStatus, Quantifier


def annotated(name, formula, inference=None):
    return AnnotatedFormula(name, FormulaRole.PLAIN, formula, inference)


def inference(rule, parents):
    return InferenceRecord(rule, [StatusInfo(InferenceStatus.THM)], parents)


class TestReflexivity:
    def test_valid_reflexivity(self):
        parent = annotated("p", Atom("p", [Constant("a")]))
        step = annotated(
            "s",
            Equality(Constant("a"), Constant("a")),
            inference(InferenceRule.REFLEXIVITY, ["p"]),
        )
        assert check_reflexivity(step, parent) == []

    def test_reflexivity_rejects_mismatched_sides(self):
        parent = annotated("p", Atom("p", [Constant("a")]))
        step = annotated(
            "s",
            Equality(Constant("a"), Constant("b")),
            inference(InferenceRule.REFLEXIVITY, ["p"]),
        )
        issues = check_reflexivity(step, parent)
        assert any("reflexive" in it.reason for it in issues)

    def test_reflexivity_rejects_non_equality(self):
        parent = annotated("p", Atom("p", [Constant("a")]))
        step = annotated("s", Atom("q", [Constant("a")]), inference(InferenceRule.REFLEXIVITY, ["p"]))
        issues = check_reflexivity(step, parent)
        assert any("non-negated equality" in it.reason for it in issues)


class TestTransitivity:
    def test_valid_transitivity_chain(self):
        first = annotated("a1", Equality(Constant("a"), Constant("b")))
        second = annotated("a2", Equality(Constant("b"), Constant("c")))
        step = annotated(
            "s1",
            Equality(Constant("a"), Constant("c")),
            inference(InferenceRule.TRANSITIVITY, ["a1", "a2"]),
        )
        assert check_transitivity(step, first, second) == []

    def test_transitivity_handles_reversed_orientation(self):
        first = annotated("a1", Equality(Constant("b"), Constant("a")))
        second = annotated("a2", Equality(Constant("c"), Constant("b")))
        step = annotated(
            "s1",
            Equality(Constant("c"), Constant("a")),
            inference(InferenceRule.TRANSITIVITY, ["a1", "a2"]),
        )
        assert check_transitivity(step, first, second) == []

    def test_transitivity_rejects_unrelated_equations(self):
        first = annotated("a1", Equality(Constant("a"), Constant("b")))
        second = annotated("a2", Equality(Constant("c"), Constant("d")))
        step = annotated(
            "s1",
            Equality(Constant("a"), Constant("d")),
            inference(InferenceRule.TRANSITIVITY, ["a1", "a2"]),
        )
        issues = check_transitivity(step, first, second)
        assert any("share a common term" in it.reason for it in issues)

    def test_transitivity_rejects_wrong_conclusion(self):
        first = annotated("a1", Equality(Constant("a"), Constant("b")))
        second = annotated("a2", Equality(Constant("b"), Constant("c")))
        step = annotated(
            "s1",
            Equality(Constant("a"), Constant("d")),
            inference(InferenceRule.TRANSITIVITY, ["a1", "a2"]),
        )
        issues = check_transitivity(step, first, second)
        assert any("does not match the transitive chain" in it.reason for it in issues)


class TestRewrite:
    def test_valid_rewrite_matches_parent(self):
        parent = annotated("p", Atom("q", [Constant("a")]))
        step = annotated("s", Atom("q", [Constant("a")]), inference(InferenceRule.REWRITE, ["p"]))
        assert check_rewrite(step, parent) == []

    def test_rewrite_rejects_changed_formula(self):
        parent = annotated("p", Atom("q", [Constant("a")]))
        step = annotated("s", Atom("q", [Constant("b")]), inference(InferenceRule.REWRITE, ["p"]))
        issues = check_rewrite(step, parent)
        assert any("does not match" in it.reason for it in issues)


class TestParamodulation:
    def test_valid_ground_rewrite(self):
        equation = annotated("eq", Equality(Constant("a"), Constant("b")))
        target = annotated("target", Atom("p", [Constant("a")]))
        step = annotated(
            "s",
            Atom("p", [Constant("b")]),
            inference(InferenceRule.PARAMODULATION, ["eq", "target"]),
        )
        assert check_paramodulation(step, equation, target) == []

    def test_valid_rewrite_with_universally_quantified_equation(self):
        equation = annotated(
            "eq",
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["Y"],
                Equality(FunctionTerm("m", [Variable("Y")]), FunctionTerm("f", [Variable("Y")])),
            ),
        )
        target = annotated("target", Atom("q", [FunctionTerm("m", [Constant("a")])]))
        step = annotated(
            "s",
            Atom("q", [FunctionTerm("f", [Constant("a")])]),
            inference(InferenceRule.PARAMODULATION, ["eq", "target"]),
        )
        assert check_paramodulation(step, equation, target) == []

    def test_paramodulation_accepts_either_parent_order(self):
        equation = annotated("eq", Equality(Constant("a"), Constant("b")))
        target = annotated("target", Atom("p", [Constant("a")]))
        step = annotated(
            "s",
            Atom("p", [Constant("b")]),
            inference(InferenceRule.PARAMODULATION, ["target", "eq"]),
        )
        assert check_paramodulation(step, target, equation) == []

    def test_paramodulation_rejects_unrelated_conclusion(self):
        equation = annotated("eq", Equality(Constant("a"), Constant("b")))
        target = annotated("target", Atom("p", [Constant("a")]))
        step = annotated(
            "s", Atom("p", [Constant("c")]), inference(InferenceRule.PARAMODULATION, ["eq", "target"])
        )
        issues = check_paramodulation(step, equation, target)
        assert any("not obtainable" in it.reason for it in issues)

    def test_paramodulation_rejects_unsound_generalization(self):
        # Regression check for the PRV007+1.s pattern: generalizing a rewritten
        # ground term into a fresh universally quantified variable is not a
        # valid single paramodulation step.
        equation = annotated(
            "eq",
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["Y"],
                Equality(FunctionTerm("m", [Variable("Y")]), FunctionTerm("f", [Variable("Y")])),
            ),
        )
        target = annotated(
            "target", Atom("p", [FunctionTerm("sk0", [FunctionTerm("m", [Constant("a")])])])
        )
        step = annotated(
            "s",
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["Z"],
                Atom("p", [FunctionTerm("sk0", [FunctionTerm("f", [Variable("Z")])])]),
            ),
            inference(InferenceRule.PARAMODULATION, ["target", "eq"]),
        )
        issues = check_paramodulation(step, target, equation)
        assert any("not obtainable" in it.reason for it in issues)


class TestResolution:
    def test_valid_ground_resolution(self):
        left = annotated(
            "a1", JunctionFormula(BinaryConnective.OR, [Atom("p", [Constant("a")]), Atom("q", [Constant("a")])])
        )
        right = annotated("a2", Negation(Atom("p", [Constant("a")])))
        step = annotated(
            "s", Atom("q", [Constant("a")]), inference(InferenceRule.RESOLUTION, ["a1", "a2"])
        )
        assert check_resolution(step, left, right) == []

    def test_valid_universally_quantified_resolution(self):
        left = annotated(
            "a1",
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                JunctionFormula(BinaryConnective.OR, [Atom("p", [Variable("X")]), Atom("q", [Variable("X")])]),
            ),
        )
        right = annotated(
            "a2",
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                JunctionFormula(
                    BinaryConnective.OR, [Negation(Atom("p", [Variable("X")])), Atom("s", [Variable("X")])]
                ),
            ),
        )
        step = annotated(
            "r1",
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                JunctionFormula(BinaryConnective.OR, [Atom("q", [Variable("X")]), Atom("s", [Variable("X")])]),
            ),
            inference(InferenceRule.RESOLUTION, ["a1", "a2"]),
        )
        assert check_resolution(step, left, right) == []

    def test_resolution_resolves_to_false(self):
        left = annotated("r", Atom("p", [Constant("a")]))
        right = annotated("neg", Negation(Atom("p", [Constant("a")])))
        step = annotated("bot", Atom("$false", []), inference(InferenceRule.RESOLUTION, ["r", "neg"]))
        assert check_resolution(step, left, right) == []

    def test_resolution_rejects_inconsistent_instantiation(self):
        # Regression check for the PRV067+1.s pattern: instantiating each
        # parent's variable independently and inconsistently is not a valid
        # resolution step, even though the two "pivot" literals look similar.
        left = annotated(
            "a1",
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                JunctionFormula(BinaryConnective.OR, [Atom("p", [Variable("X")]), Atom("r", [Variable("X")])]),
            ),
        )
        right = annotated(
            "a2",
            QuantifiedFormula(
                Quantifier.UNIVERSAL,
                ["X"],
                JunctionFormula(
                    BinaryConnective.OR, [Negation(Atom("p", [Variable("X")])), Atom("t", [Variable("X")])]
                ),
            ),
        )
        step = annotated(
            "s",
            JunctionFormula(
                BinaryConnective.OR, [Atom("r", [Constant("a")]), Atom("t", [Constant("b")])]
            ),
            inference(InferenceRule.RESOLUTION, ["a1", "a2"]),
        )
        issues = check_resolution(step, left, right)
        assert any("no pair of complementary" in it.reason for it in issues)


class TestIntegrationAgainstRealProofs:
    def test_prv018_transitivity_and_paramodulation(self):
        result = check_proof_file("ProoVer2026/PRV018+1.s", "ProoVer2026/Problems/PRV018+1.p")
        assert result["transitivity_issues"] == {}
        assert result["paramodulation_issues"] == {}

    def test_prv020_resolution(self):
        result = check_proof_file("ProoVer2026/PRV020+1.s", "ProoVer2026/Problems/PRV020+1.p")
        assert result["resolution_issues"] == {}

    def test_prv021_resolution_and_paramodulation(self):
        result = check_proof_file("ProoVer2026/PRV021+1.s", "ProoVer2026/Problems/PRV021+1.p")
        assert result["resolution_issues"] == {}
        assert result["paramodulation_issues"] == {}

    def test_prv007_reflexivity_ok_but_paramodulation_unsound(self):
        result = check_proof_file("ProoVer2026/PRV007+1.s", "ProoVer2026/Problems/PRV007+1.p")
        assert result["reflexivity_issues"] == {}
        # The proof's "s" step generalizes a rewritten ground fact into a
        # fresh universally quantified variable, which is not a logically
        # sound single paramodulation step (and is not actually entailed by
        # the axioms), so this must be flagged.
        assert result["paramodulation_issues"] != {}

    def test_prv067_resolution_is_unsound(self):
        result = check_proof_file("ProoVer2026/PRV067+1.s", "ProoVer2026/Problems/PRV067+1.p")
        # a1, a2 do not entail r(a) | t(b) under independent instantiation of
        # the shared pivot variable X; this must be flagged as invalid.
        assert result["resolution_issues"] != {}
