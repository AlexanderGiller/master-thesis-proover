"""Scoring system for proof verification results."""

import csv
from pathlib import Path
from typing import Optional


class ScoringResult:
    """Result of scoring a single proof."""

    def __init__(self, proof_name: str, expected_status: str, actual_status: str, details=None):
        self.proof_name = proof_name
        self.expected_status = expected_status
        self.actual_status = actual_status
        self.details = details or {}
        self.is_correct = self._check_correctness()
        self.points = self._calculate_points()

    def _check_correctness(self) -> bool:
        """Determine if the actual result matches the expected result."""
        expected_map = {
            "CORRECT": "VerifiedGood",
            "INCORRECT": "VerifiedBad",
        }

        expected_szs_status = expected_map.get(self.expected_status)
        return self.actual_status == expected_szs_status

    def _calculate_points(self) -> int:
        """Calculate points based on scoring rule.

        Scoring rules:
        - Richtig als Richtig (CORRECT → VerifiedGood): +1
        - Falsch als Falsch (INCORRECT → VerifiedBad): +2
        - Richtig als Falsch (CORRECT → VerifiedBad): -1
        - Falsch als Richtig (INCORRECT → VerifiedGood): -10
        - Timeout: 0
        """
        # Timeout always gives 0 points
        if self.actual_status == "Timeout":
            return 0

        # Map expected status to expected szs status
        expected_map = {
            "CORRECT": "VerifiedGood",
            "INCORRECT": "VerifiedBad",
        }
        expected_szs_status = expected_map.get(self.expected_status)

        # Case 1: CORRECT → VerifiedGood (+1)
        if self.expected_status == "CORRECT" and self.actual_status == "VerifiedGood":
            return 1

        # Case 2: INCORRECT → VerifiedBad (+2)
        if self.expected_status == "INCORRECT" and self.actual_status == "VerifiedBad":
            return 2

        # Case 3: CORRECT → VerifiedBad (-1)
        if self.expected_status == "CORRECT" and self.actual_status == "VerifiedBad":
            return -1

        # Case 4: INCORRECT → VerifiedGood (-10)
        if self.expected_status == "INCORRECT" and self.actual_status == "VerifiedGood":
            return -10

        # Default (should not happen)
        return 0

    def get_error_categories(self) -> dict:
        """Extract error categories from the details."""
        if not self.details or self.actual_status == "Timeout":
            return {}

        error_categories = {}
        issue_columns = [
            ("circular_dependency_issues", "Circular dependency"),
            ("axiom_issues", "Axiom"),
            ("conjecture_issues", "Conjecture"),
            ("negated_conjecture_issues", "Negated conjecture"),
            ("instantiate_issues", "Instantiate"),
            ("existential_gen_issues", "Existential gen"),
            ("modus_ponens_issues", "Modus ponens"),
            ("conjunction_issues", "Conjunction"),
            ("split_conjunct_issues", "Split conjunct"),
            ("copy_issues", "Copy"),
            ("duplicate_issues", "Duplicate"),
            ("rename_variable_issues", "Rename variable"),
            ("double_negation_issues", "Double negation"),
            ("remove_double_negation_issues", "Remove double negation"),
            ("weaken_issues", "Weaken"),
            ("commute_issues", "Commute"),
            ("excluded_middle_issues", "Excluded middle"),
            ("resolution_issues", "Resolution"),
            ("paramodulation_issues", "Paramodulation"),
            ("reflexivity_issues", "Reflexivity"),
            ("transitivity_issues", "Transitivity"),
            ("rewrite_issues", "Rewrite"),
            ("skolem_issues", "Skolemization"),
            ("external_atp_issues", "External ATP"),
        ]

        for key, label in issue_columns:
            count = len(self.details.get(key, {}))
            if count > 0:
                error_categories[label] = count

        return error_categories


class ProofScorer:
    """Calculate scores for proof verification results."""

    def __init__(self, expected_results_file: str):
        """Load expected results from CSV file."""
        self.expected = self._load_expected_results(expected_results_file)

    def _load_expected_results(self, file_path: str) -> dict:
        """Load expected results from CSV file."""
        expected = {}
        path = Path(file_path)

        if not path.exists():
            print(f"Warning: Expected results file not found: {file_path}")
            return expected

        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('proof') and row.get('expected_status'):
                        expected[row['proof']] = row['expected_status']
        except Exception as e:
            print(f"Error loading expected results: {e}")

        return expected

    def score_proof(self, proof_name: str, actual_status: str, details=None) -> ScoringResult:
        """Score a single proof result."""
        expected_status = self.expected.get(proof_name, "UNKNOWN")
        return ScoringResult(proof_name, expected_status, actual_status, details)

    def calculate_score_summary(self, results: list[ScoringResult]) -> dict:
        """Calculate overall scoring summary using point-based system."""
        if not results:
            return {}

        total = len(results)
        correct = sum(1 for r in results if r.is_correct)
        incorrect = total - correct

        # Calculate total points
        total_points = sum(r.points for r in results)

        # Maximum possible points (all correct as correct = +1 each)
        max_points = total

        # Minimum possible points (all incorrect as incorrect = -10 each)
        min_points = -10 * total

        # Count by status
        verified_good = sum(1 for r in results if r.actual_status == "VerifiedGood")
        verified_bad = sum(1 for r in results if r.actual_status == "VerifiedBad")
        timeout = sum(1 for r in results if r.actual_status == "Timeout")
        error = sum(1 for r in results if r.actual_status not in ["VerifiedGood", "VerifiedBad", "Timeout"])

        # Count by scoring result type
        count_correct_as_correct = sum(1 for r in results if r.points == 1)
        count_false_as_false = sum(1 for r in results if r.points == 2)
        count_correct_as_false = sum(1 for r in results if r.points == -1)
        count_false_as_correct = sum(1 for r in results if r.points == -10)

        # Points by category
        points_correct_as_correct = count_correct_as_correct * 1
        points_false_as_false = count_false_as_false * 2
        points_correct_as_false = count_correct_as_false * (-1)
        points_false_as_correct = count_false_as_correct * (-10)

        # Count error categories across all results
        all_errors = {}
        for result in results:
            if not result.is_correct:
                for category, count in result.get_error_categories().items():
                    all_errors[category] = all_errors.get(category, 0) + count

        # Sort error categories by frequency
        sorted_errors = sorted(all_errors.items(), key=lambda x: x[1], reverse=True)

        return {
            "total": total,
            "correct": correct,
            "incorrect": incorrect,
            "total_points": total_points,
            "max_points": max_points,
            "min_points": min_points,
            "count_correct_as_correct": count_correct_as_correct,
            "count_false_as_false": count_false_as_false,
            "count_correct_as_false": count_correct_as_false,
            "count_false_as_correct": count_false_as_correct,
            "points_correct_as_correct": points_correct_as_correct,
            "points_false_as_false": points_false_as_false,
            "points_correct_as_false": points_correct_as_false,
            "points_false_as_correct": points_false_as_correct,
            "verified_good": verified_good,
            "verified_bad": verified_bad,
            "timeout": timeout,
            "error": error,
            "error_categories": sorted_errors,
        }

    def export_results_to_csv(self, results: list[ScoringResult], output_file: str) -> None:
        """Export scoring results to CSV file."""
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Proof",
                "Expected",
                "Actual",
                "Points",
                "Error Categories"
            ])

            for result in results:
                errors = ", ".join(
                    f"{cat} ({count})"
                    for cat, count in result.get_error_categories().items()
                )

                writer.writerow([
                    result.proof_name,
                    result.expected_status,
                    result.actual_status,
                    result.points,
                    errors
                ])


def print_scoring_summary(summary: dict) -> None:
    """Print a formatted scoring summary."""
    if not summary:
        print("No results to summarize")
        return

    print("\n" + "="*70)
    print("SCORING SUMMARY (Point-based System)")
    print("="*70)
    print(f"Total Proofs:          {summary['total']}")
    print(f"Total Points:          {summary['total_points']}")
    print(f"Max Possible:          {summary['max_points']} (all +1)")
    print(f"Min Possible:          {summary['min_points']} (all -10)")
    print()
    print("Score Breakdown:")
    print(f"  Correct → VerifiedGood:  {summary['count_correct_as_correct']:3d} proofs × (+1) = {summary['points_correct_as_correct']:+4d}")
    print(f"  Incorrect → VerifiedBad: {summary['count_false_as_false']:3d} proofs × (+2) = {summary['points_false_as_false']:+4d}")
    print(f"  Correct → VerifiedBad:   {summary['count_correct_as_false']:3d} proofs × (-1) = {summary['points_correct_as_false']:+4d}")
    print(f"  Incorrect → VerifiedGood:{summary['count_false_as_correct']:3d} proofs × (-10) = {summary['points_false_as_correct']:+4d}")
    print()
    print("Verification Status:")
    print(f"  VerifiedGood:    {summary['verified_good']}")
    print(f"  VerifiedBad:     {summary['verified_bad']}")
    print(f"  Timeout:         {summary['timeout']}")
    print(f"  Error:           {summary['error']}")

    if summary['error_categories']:
        print()
        print("Top Error Categories:")
        for category, count in summary['error_categories'][:10]:
            print(f"  {category}: {count}")

    print("="*70)







