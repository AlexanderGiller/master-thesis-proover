"""Fallback checker that validates unspecified steps with an external ATP."""

from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

from src.parser.ast_nodes import (
    Atom,
    BinaryFormula,
    Constant,
    Equality,
    FunctionTerm,
    JunctionFormula,
    Negation,
    QuantifiedFormula,
    Variable,
)
from src.var_mapping import BinaryConnective, InferenceStatus, Quantifier

ATP_TIMEOUT_SECONDS = 30.0


def _quote_symbol(name: str) -> str:
    if re.fullmatch(r"[a-z][A-Za-z0-9_]*", name):
        return name
    return "'" + name.replace("'", "''") + "'"


def _quote_variable(name: str) -> str:
    if re.fullmatch(r"[A-Z][A-Za-z0-9_]*", name):
        return name
    return f"V_{re.sub(r'[^A-Za-z0-9_]', '_', name)}"


def _term_to_tptp(term: object) -> str:
    if isinstance(term, Variable):
        return _quote_variable(term.name)
    if isinstance(term, Constant):
        return _quote_symbol(term.name)
    if isinstance(term, FunctionTerm):
        if not term.args:
            return _quote_symbol(term.functor)
        args = ", ".join(_term_to_tptp(arg) for arg in term.args)
        return f"{_quote_symbol(term.functor)}({args})"
    if isinstance(term, Atom):
        if not term.args:
            return _quote_symbol(term.predicate)
        args = ", ".join(_term_to_tptp(arg) for arg in term.args)
        return f"{_quote_symbol(term.predicate)}({args})"
    return str(term)


def formula_to_tptp(formula: object) -> str:
    """Serialize a parsed formula to a TPTP FOF string."""
    if isinstance(formula, Atom):
        if not formula.args:
            return _quote_symbol(formula.predicate)
        args = ", ".join(_term_to_tptp(arg) for arg in formula.args)
        return f"{_quote_symbol(formula.predicate)}({args})"
    if isinstance(formula, Constant):
        return _quote_symbol(formula.name)
    if isinstance(formula, Variable):
        return _quote_variable(formula.name)
    if isinstance(formula, FunctionTerm):
        return _term_to_tptp(formula)
    if isinstance(formula, Equality):
        op = "!=" if formula.negated else "="
        return f"({formula_to_tptp(formula.left)} {op} {formula_to_tptp(formula.right)})"
    if isinstance(formula, Negation):
        return f"~({formula_to_tptp(formula.formula)})"
    if isinstance(formula, BinaryFormula):
        connective = formula.connective
        if connective == BinaryConnective.IMPLIED:
            connective = BinaryConnective.IMPLIES
        return (
            f"({formula_to_tptp(formula.left)} {connective} "
            f"{formula_to_tptp(formula.right)})"
        )
    if isinstance(formula, JunctionFormula):
        sep = f" {formula.connective} "
        return f"({sep.join(formula_to_tptp(op) for op in formula.operands)})"
    if isinstance(formula, QuantifiedFormula):
        vars_str = ", ".join(_quote_variable(str(v)) for v in formula.variables)
        return f"{formula.quantifier} [{vars_str}] : ({formula_to_tptp(formula.formula)})"
    return str(formula)


def _render_problem(premises: list[object], goal: object) -> str:
    lines = ["% Automatically generated validation problem"]
    for index, premise in enumerate(premises):
        lines.append(f"fof(p{index}, axiom, {formula_to_tptp(premise)}).")
    lines.append(f"fof(goal, conjecture, {formula_to_tptp(goal)}).")
    return "\n".join(lines) + "\n"


def _resolve_atp_command() -> list[str]:
    configured = os.environ.get("EXTERNAL_ATP_COMMAND")
    if configured:
        return shlex.split(configured)

    binary = os.environ.get("EXTERNAL_ATP_BINARY", "vampire")
    found = shutil.which(binary)
    if found:
        return [found]

    wsl_default = Path.home() / "vampire" / "vampire"
    if wsl_default.exists():
        return [str(wsl_default)]

    return [binary]


def _maybe_translate_path_for_command(command: list[str], path: Path) -> Path:
    """Translate a Windows path to a WSL path when the ATP is launched via wsl."""
    if not command:
        return path
    if not Path(command[0]).name.lower().startswith("wsl"):
        return path

    translated = subprocess.run(
        [command[0], "wslpath", "-a", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    candidate = translated.stdout.strip()
    return Path(candidate) if candidate else path


def validate_step_with_atp(
    step_formula: object,
    premise_formulas: list[object],
    timeout_seconds: float = ATP_TIMEOUT_SECONDS,
) -> tuple[bool, str]:
    """Validate a step using an external ATP and only the step's premises."""
    problem_text = _render_problem(premise_formulas, step_formula)
    command = _resolve_atp_command() + [
        "--mode",
        "casc",
        "--time_limit",
        str(max(1, int(timeout_seconds))),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        problem_path = Path(tmpdir) / "validation.p"
        problem_path.write_text(problem_text, encoding="utf-8")
        command.append(str(problem_path))
        command[-1] = str(_maybe_translate_path_for_command(command, problem_path))
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except FileNotFoundError:
            return True, f"ATP executable not found: {command[0]}"
        except subprocess.TimeoutExpired:
            return False, "ATP timed out"

    output = f"{completed.stdout}\n{completed.stderr}"
    match = re.search(r"%\s*SZS status\s+([A-Za-z0-9_]+)", output)
    if not match:
        return True, "ATP output did not contain an SZS status"

    status = match.group(1)
    if status in {"Theorem", "Unsatisfiable", "ContradictoryAxioms"}:
        return True, status
    return False, status


def status_allows_atp(status: InferenceStatus | None) -> bool:
    """Only thm/cth steps may be delegated to an external ATP."""
    return status in {InferenceStatus.THM, InferenceStatus.CTH}
