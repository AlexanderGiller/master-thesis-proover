from src.checker.file_dir import check_axiom_provenance, ProvenanceIssue
from src.parser.ast_nodes import AnnotatedFormula, InferenceRecord, Atom, Constant


def make_annotated(name, role, formula, raw_source=None):
    return AnnotatedFormula(name=name, role=role, formula=formula, raw_source=raw_source)


def test_missing_raw_source_reports_issue():
    proof_ax = make_annotated(name="ax1", role="axiom", formula=Atom("p", args=[Constant("a")]), raw_source=None)
    issues = check_axiom_provenance(proof_ax, {}, "Problems/foo.p")
    assert len(issues) == 1
    assert "missing file(...) source directive" in issues[0].reason


def test_non_file_raw_source_reports_issue():
    proof_ax = make_annotated(name="ax1", role="axiom", formula=Atom("p", args=[Constant("a")]), raw_source=("introduced", "definition"))
    issues = check_axiom_provenance(proof_ax, {}, "Problems/foo.p")
    assert len(issues) == 1
    assert "missing file(...) source directive" in issues[0].reason


def test_cited_path_filename_mismatch_reports_issue():
    # proof cites Problems/other.p but expected_problem_path has name foo.p
    proof_ax = make_annotated(name="ax1", role="axiom", formula=Atom("p", args=[Constant("a")]), raw_source=("file", "Problems/other.p", "ax1"))
    problem_axioms = {"ax1": make_annotated("ax1", "axiom", Atom("p", args=[Constant("a")]))}
    issues = check_axiom_provenance(proof_ax, problem_axioms, "Problems/foo.p")
    assert any("points to" in it.reason for it in issues)


def test_missing_lookup_name_reports_issue():
    # proof cites a reference name that is not present in problem file
    proof_ax = make_annotated(name="ax_alias", role="axiom", formula=Atom("p", args=[Constant("a")]), raw_source=("file", "Problems/foo.p", "ax_not_there"))
    problem_axioms = {"ax1": make_annotated("ax1", "axiom", Atom("p", args=[Constant("a")]))}
    issues = check_axiom_provenance(proof_ax, problem_axioms, "Problems/foo.p")
    assert any("no formula named" in it.reason for it in issues)


def test_original_role_not_axiom_reports_issue():
    proof_ax = make_annotated(name="ax1", role="axiom", formula=Atom("p", args=[Constant("a")]), raw_source=("file", "Problems/foo.p", "ax1"))
    # original has role plain
    problem_axioms = {"ax1": make_annotated("ax1", "plain", Atom("p", args=[Constant("a")]))}
    issues = check_axiom_provenance(proof_ax, problem_axioms, "Problems/foo.p")
    assert any("has role" in it.reason for it in issues)


def test_not_alpha_equivalent_reports_issue():
    proof_ax = make_annotated(name="ax1", role="axiom", formula=Atom("p", args=[Constant("d")]), raw_source=("file", "Problems/foo.p", "ax1"))
    problem_axioms = {"ax1": make_annotated("ax1", "axiom", Atom("p", args=[Constant("a")]))}
    issues = check_axiom_provenance(proof_ax, problem_axioms, "Problems/foo.p")
    assert any("not alpha-equivalent" in it.reason for it in issues)


def test_all_ok_returns_empty_list():
    proof_ax = make_annotated(name="ax1", role="axiom", formula=Atom("p", args=[Constant("a")]), raw_source=("file", "Problems/foo.p", None))
    problem_axioms = {"ax1": make_annotated("ax1", "axiom", Atom("p", args=[Constant("a")]))}
    issues = check_axiom_provenance(proof_ax, problem_axioms, "Problems/foo.p")
    assert issues == []

