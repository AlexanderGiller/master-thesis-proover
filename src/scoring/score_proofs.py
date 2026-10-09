#!/usr/bin/env python
"""Standalone scoring script for proof verification results.

This script allows you to score proofs without re-running the full verification.
It assumes the verification results are already stored in a CSV file.
"""

import argparse
import csv
from pathlib import Path
from src.scoring import ProofScorer, ScoringResult, print_scoring_summary


def load_verification_results(results_csv: str) -> dict:
    """Load verification results from a CSV file."""
    results = {}
    path = Path(results_csv)

    if not path.exists():
        raise FileNotFoundError(f"Results file not found: {results_csv}")

    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            proof_name = row.get('Proof')
            status = row.get('Status')
            if proof_name and status:
                results[proof_name] = status

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Score proof verification results against expected outcomes."
    )
    parser.add_argument(
        "-e", "--expected",
        default="PRV_expected.csv",
        help="CSV file with expected results (default: PRV_expected.csv)"
    )
    parser.add_argument(
        "-r", "--results",
        default="ProoVer2026_results.csv",
        help="CSV file with verification results (default: ProoVer2026_results.csv)"
    )
    parser.add_argument(
        "-o", "--output",
        default="scoring_report.csv",
        help="Output file for scoring report (default: scoring_report.csv)"
    )

    args = parser.parse_args()
    base = Path(__file__).parent

    expected_file = base / args.expected
    results_file = base / args.results
    output_file = base / args.output

    print(f"Loading expected results from: {expected_file}")
    print(f"Loading verification results from: {results_file}")

    # Initialize scorer
    scorer = ProofScorer(str(expected_file))

    # Try to load existing results
    if results_file.exists():
        print(f"Reading verification results from: {results_file}")
        with open(results_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            results = []
            for row in reader:
                proof_name = row.get('Proof')
                expected = row.get('Expected', 'UNKNOWN')
                actual = row.get('Actual')
                if proof_name and actual:
                    score_result = ScoringResult(proof_name, expected, actual)
                    results.append(score_result)
    else:
        print(f"Results file not found: {results_file}")
        return

    # Calculate and display summary
    if results:
        summary = scorer.calculate_score_summary(results)
        print_scoring_summary(summary)

        # Export to CSV
        scorer.export_results_to_csv(results, str(output_file))
        print(f"\nScoring report exported to: {output_file}")
    else:
        print("No results to score")


if __name__ == "__main__":
    main()

