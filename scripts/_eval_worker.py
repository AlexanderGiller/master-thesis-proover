#!/usr/bin/env python3
"""Check one proof in a fresh process and print one JSON record.

Used by scripts/eval_all.py.  The record contains the verdict, the issue maps
(truncated), the per-step branch log of the driver, the time spent in ATP calls,
the wall-clock/CPU time of the check, the parse time, and the peak memory.

Usage: python scripts/_eval_worker.py PROOF PROBLEM
"""

from __future__ import annotations

import contextlib
import io
import json
import re
import resource
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

STEP_RE = re.compile(
    r"^\[DBG\] (?P<name>.+?): branch=(?P<branch>.*?), rule=(?P<rule>[^,]*), status=(?P<status>[^,]*), parents=(?P<n>\d+)$"
)
ATP_RE = re.compile(
    r"^\[DBG\] (?P<name>.+?): ATP call took (?P<t>[\d.]+)s, valid=(?P<v>[^,]+), note=(?P<note>.*)$"
)


def main() -> None:
    proof, problem = sys.argv[1], sys.argv[2]
    t_start = time.perf_counter()
    import main as verifier  # noqa: E402
    from src.deep_recursion import run_with_larger_stack  # noqa: E402

    t_import = time.perf_counter() - t_start
    verifier.DEBUG_PROOF_FLOW = True

    buf = io.StringIO()
    cpu0 = time.process_time()
    wall0 = time.perf_counter()
    err = None
    result = None
    try:
        with contextlib.redirect_stdout(buf):
            result = run_with_larger_stack(lambda: verifier.check_proof_file(proof, problem))
    except Exception as exc:  # noqa: BLE001
        err = f"{type(exc).__name__}: {exc}"
    wall = time.perf_counter() - wall0
    cpu = time.process_time() - cpu0

    t_check_end = time.time()
    maxrss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    t0 = time.perf_counter()
    verifier.parse_file(problem)
    verifier.load_proof(proof)
    t_parse_warm = time.perf_counter() - t0

    steps = []
    atp = {}
    for line in buf.getvalue().splitlines():
        m = STEP_RE.match(line)
        if m:
            steps.append(
                dict(
                    name=m["name"],
                    branch=m["branch"],
                    rule=m["rule"],
                    status=m["status"],
                    parents=int(m["n"]),
                )
            )
            continue
        m = ATP_RE.match(line)
        if m:
            atp.setdefault(m["name"], []).append(
                dict(t=float(m["t"]), valid=m["v"], note=m["note"])
            )

    atp_time = sum(c["t"] for calls in atp.values() for c in calls)
    rec = dict(
        proof=Path(proof).name,
        error=err,
        all_ok=None if result is None else bool(result["all_ok"]),
        verdict=None if result is None else result.get("verdict"),
        issues=(
            {}
            if result is None
            else {
                k: {s: v[:2] for s, v in list(val.items())[:20]}
                for k, val in result.items()
                if k.endswith("_issues") and val
            }
        ),
        n_issue_steps=(
            0 if result is None else sum(len(v) for k, v in result.items() if k.endswith("_issues"))
        ),
        steps=steps,
        atp=atp,
        atp_calls=sum(len(c) for c in atp.values()),
        atp_time=atp_time,
        wall=wall,
        cpu=cpu,
        parse_warm=t_parse_warm,
        t_import=t_import,
        t_check_end=t_check_end,
        maxrss_kb=maxrss_kb,
    )
    print("@@JSON@@" + json.dumps(rec))


if __name__ == "__main__":
    main()
