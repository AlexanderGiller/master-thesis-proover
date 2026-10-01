from proof_checker_demo import print_prv_results_table, summarize_issues


def test_summarize_issues_lists_failed_check_types():
    details = {
        "axiom_issues": {"a1": ["invalid axiom"]},
        "skolem_issues": {"s1": ["invalid skolem"], "s2": ["not fresh"]},
    }
    for key in (
        "circular_dependency_issues",
        "conjecture_issues",
        "negated_conjecture_issues",
        "instantiate_issues",
        "existential_gen_issues",
        "modus_ponens_issues",
        "conjunction_issues",
        "split_conjunct_issues",
        "copy_issues",
        "duplicate_issues",
        "rename_variable_issues",
        "double_negation_issues",
        "remove_double_negation_issues",
        "weaken_issues",
        "commute_issues",
        "excluded_middle_issues",
        "resolution_issues",
        "paramodulation_issues",
        "reflexivity_issues",
        "transitivity_issues",
        "rewrite_issues",
        "external_atp_issues",
    ):
        details[key] = {}

    assert summarize_issues(details, "VerifiedBad") == "Axiom (1), Skolemization (2)"


def test_print_prv_results_table_includes_all_statuses(capsys):
    print_prv_results_table(
        [
            ("PRV001+1.s", "VerifiedGood", {"axiom_issues": {}}),
            ("PRV002+1.s", "Timeout", None),
        ]
    )

    output = capsys.readouterr().out
    assert "Results by PRV file" in output
    assert "PRV001+1.s" in output
    assert "VerifiedGood" in output
    assert "PRV002+1.s" in output
    assert "Timeout" in output
