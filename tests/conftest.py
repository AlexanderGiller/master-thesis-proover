# tests/conftest.py
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def simple_problem_path():
    return str(FIXTURES / "simple.p")


@pytest.fixture
def skolem_problem_path():
    return str(FIXTURES / "skolem.p")


@pytest.fixture
def simple_proof_path():
    return str(FIXTURES / "simple_proof.p")


@pytest.fixture
def skolem_proof_path():
    return str(FIXTURES / "skolem_proof.p")


@pytest.fixture
def simple_problem(simple_problem_path):
    from src.parser.parser import parse_file

    return parse_file(simple_problem_path)


@pytest.fixture
def simple_proof(simple_proof_path):
    from src.parser.parser import load_proof

    return load_proof(simple_proof_path)


@pytest.fixture
def skolem_proof(skolem_proof_path):
    from src.parser.parser import load_proof

    return load_proof(skolem_proof_path)
