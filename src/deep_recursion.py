"""Helper for running deeply recursive work without hitting Python's stack limits.

TPTP problems may contain deeply right-nested formulas (e.g. hundreds of
stacked negations or function applications, as seen in stress-test cases like
PRV042). Parsing (Lark's tree transformer) and the checkers (alpha-equivalence,
Skolemization, etc.) all walk the formula tree recursively, once per nesting
level. That can exceed Python's default recursion limit.

Simply raising ``sys.setrecursionlimit`` is not enough on its own: each Python
stack frame still needs room on the underlying OS thread stack, so a high
limit without a bigger stack risks a hard interpreter crash instead of a clean
``RecursionError``. Running the work in a dedicated thread lets us safely
raise both the stack size and the recursion limit together, and revert them
afterwards.
"""

from __future__ import annotations

import sys
import threading
from typing import Callable, TypeVar

T = TypeVar("T")

# 64 MB is generous for formulas nested many thousands of levels deep.
DEEP_RECURSION_STACK_SIZE = 64 * 1024 * 1024
DEEP_RECURSION_LIMIT = 100_000


def run_with_larger_stack(func: Callable[[], T]) -> T:
    """Run a zero-argument callable in a thread with a bigger stack/recursion limit."""
    previous_stack_size = None
    try:
        previous_stack_size = threading.stack_size()
        threading.stack_size(DEEP_RECURSION_STACK_SIZE)
    except (ValueError, RuntimeError):
        # Platform doesn't support changing the thread stack size; fall back
        # to running with the default stack.
        previous_stack_size = None

    outcome: dict = {}

    def _target():
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(DEEP_RECURSION_LIMIT)
        try:
            outcome["value"] = func()
        except BaseException as exc:  # re-raised on the calling thread below
            outcome["error"] = exc
        finally:
            sys.setrecursionlimit(old_limit)

    worker = threading.Thread(target=_target)
    worker.start()
    worker.join()

    if previous_stack_size is not None:
        try:
            threading.stack_size(previous_stack_size)
        except (ValueError, RuntimeError):
            pass

    if "error" in outcome:
        raise outcome["error"]
    return outcome["value"]
