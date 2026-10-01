"""Checkers that detect circular reasoning in a proof's dependency graph.
"""

from dataclasses import dataclass

from src.parser.ast_nodes import AnnotatedFormula
from src.var_mapping import FormulaRole, InferenceRule


@dataclass
class CircularDependencyIssue:
    step_name: str
    reason: str


def check_no_circular_dependencies(
    steps: list[AnnotatedFormula],
) -> list[CircularDependencyIssue]:
    """Detect cycles in the parent/child graph induced by inference(...).parents.

    Builds a directed graph where each step points to the parent step(s) it
    was derived from, then runs an iterative depth-first search with a
    three-color marking (white/gray/black) to find back-edges, which are the
    signature of a cycle. Unknown/missing parents are ignored here (that is
    reported elsewhere, e.g. as a "parent not found" issue).
    """
    parents_of: dict[str, list[str]] = {
        step.name: (step.inference.parents if step.inference else []) for step in steps
    }

    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = dict.fromkeys(parents_of, WHITE)
    issues: list[CircularDependencyIssue] = []
    reported_cycles: set[frozenset[str]] = set()

    def visit(start: str) -> None:
        # Iterative DFS to avoid Python recursion-depth limits on long proofs.
        stack: list[tuple[str, int]] = [(start, 0)]
        path: list[str] = [start]
        color[start] = GRAY

        while stack:
            node, next_idx = stack[-1]
            parents = parents_of.get(node, [])
            if next_idx >= len(parents):
                color[node] = BLACK
                path.pop()
                stack.pop()
                continue

            stack[-1] = (node, next_idx + 1)
            parent = parents[next_idx]
            if parent not in color:
                continue  # dangling reference; not this checker's concern

            state = color[parent]
            if state == WHITE:
                color[parent] = GRAY
                path.append(parent)
                stack.append((parent, 0))
            elif state == GRAY:
                cycle_start = path.index(parent)
                cycle = path[cycle_start:] + [parent]
                key = frozenset(cycle)
                if key not in reported_cycles:
                    reported_cycles.add(key)
                    issues.append(
                        CircularDependencyIssue(
                            node,
                            "circular dependency detected: " + " -> ".join(cycle),
                        )
                    )
            # state == BLACK: already fully explored, no cycle through here

    for name in parents_of:
        if color[name] == WHITE:
            visit(name)

    return issues


def check_conjecture_not_assumed(
    steps: list[AnnotatedFormula],
) -> list[CircularDependencyIssue]:
    """Detect steps that use the raw conjecture as a premise instead of its
    negation.

    In a refutation-style TSTP proof, the "conjecture"-role formula itself
    must never be cited as a `parent` except by the single, dedicated
    negated_conjecture step (which is separately checked to make sure it
    really is the negation, not a copy). Any other step that lists a
    conjecture-role formula among its parents is treating the goal as an
    established premise, i.e. assuming what it set out to prove.
    """
    steps_by_name = {step.name: step for step in steps}
    conjecture_names = {
        step.name for step in steps if step.role == FormulaRole.CONJECTURE
    }
    issues: list[CircularDependencyIssue] = []

    if not conjecture_names:
        return issues

    for step in steps:
        if step.inference is None:
            continue
        is_valid_negation_derivation = (
            step.role == FormulaRole.NEGATED_CONJECTURE
            and step.inference.rule == InferenceRule.NEGATED_CONJECTURE
        )
        if is_valid_negation_derivation:
            continue  # the one legitimate use of the conjecture as a parent

        assumed = [p for p in step.inference.parents if p in conjecture_names]
        for conj_name in assumed:
            issues.append(
                CircularDependencyIssue(
                    step.name,
                    f"step assumes conjecture '{conj_name}' as a premise instead of "
                    "deriving from its negated_conjecture; this begs the question "
                    "(petitio principii)",
                )
            )

    return issues
