"""Tests based on the generated cases in ProoVer2026/Extra (see scripts/gen_extra_tests.py).

The first group calls the rule checkers directly and needs no external prover.
The last test runs the whole pipeline and is skipped when no ATP is available.
"""

import csv
import os
import shutil
from pathlib import Path

import pytest

from main import check_proof_file
from src.checker.clausal_checker import check_resolution
from src.checker.instantiate_checker import check_instantiate
from src.parser.parser import parse_file

ROOT = Path(__file__).resolve().parents[1]
EXTRA = ROOT / "ProoVer2026" / "Extra"

pytestmark = pytest.mark.skipif(not EXTRA.exists(), reason="run scripts/gen_extra_tests.py first")


def _expected() -> dict[str, tuple[str, str]]:
    with open(ROOT / "src" / "scoring" / "EXT_expected.csv", encoding="utf-8") as fh:
        return {test: (name, exp) for name, test, exp, _ in csv.reader(fh)}


def _steps(test: str) -> dict:
    name, _ = _expected()[test]
    return {s.name: s for s in parse_file(str(EXTRA / name))}


def test_instantiate_rejects_variable_capture():
    """!X ?Y r(X,Y) does not entail ?Y r(Y,Y)."""
    st = _steps("instantiate_variable_capture")
    assert check_instantiate(st["s"], st["a1"]) != []


def test_instantiate_accepts_instance_below_existential():
    st = _steps("instantiate_under_existential")
    assert check_instantiate(st["s"], st["a1"]) == []


def test_resolution_standardises_variables_apart():
    st = _steps("resolution_variables_standardised_apart")
    assert check_resolution(st["s"], st["a1"], st["a2"]) == []


def test_resolution_rejects_conflated_variables():
    st = _steps("resolution_variables_conflated")
    assert check_resolution(st["s"], st["a1"], st["a2"]) != []


def test_resolution_requires_occurs_check():
    st = _steps("resolution_occurs_check")
    assert check_resolution(st["s"], st["a1"], st["a2"]) != []


def _atp_available() -> bool:
    return bool(
        os.environ.get("EXTERNAL_ATP_COMMAND")
        or shutil.which(os.environ.get("EXTERNAL_ATP_BINARY", "vampire"))
        or (Path.home() / "vampire" / "vampire").exists()
    )


@pytest.mark.skipif(
    not _atp_available(), reason="needs an external ATP for the final consequence step"
)
def test_extra_suite_matches_ground_truth():
    wrong = []
    for test, (name, exp) in _expected().items():
        if exp == "EDGE":
            continue
        proof = EXTRA / name
        problem = EXTRA / "Problems" / (proof.stem + ".p")
        ok = check_proof_file(str(proof), str(problem))["all_ok"]
        if ok != (exp == "CORRECT"):
            wrong.append(f"{name} ({test}): expected {exp}, got {'good' if ok else 'bad'}")
    assert not wrong, "\n".join(wrong)
