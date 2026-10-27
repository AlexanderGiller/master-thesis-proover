# ProoVer Thesis Proof Checker

This project is a proof checker for TPTP/TSTP proofs in the setting of the ProoVer 2026 competition.
It verifies individual inference steps, uses an external ATP (Vampire) where needed, and produces result and scoring reports.

## Context

The project was developed as part of the master's thesis "Designing a Competitive Proof Verification System for
TPTP-Style Benchmarks" at the "Chair of Theoretical Computer Science and Theorem Proving" at Ludwig-Maximilians-Universität München (LMU).
Its focus is on transparent verification, reproducible experiments, and a clear separation between proof search and proof checking.

## Contents

- [Requirements](#requirements)
- [Installation on Linux](#installation-on-linux)
- [Installation on Windows with WSL](#installation-on-windows-with-wsl)
- [External ATP integration (Vampire)](#external-atp-integration-vampire)
- [Project structure](#project-structure)
- [Command-line usage](#command-line-usage)
- [Output and results](#output-and-results)
- [Scripts (scripts/)](#scripts-scripts)
- [Reproducing the results of the thesis](#reproducing-the-results-of-the-thesis)
- [Tests and development](#tests-and-development)
- [Troubleshooting](#troubleshooting)

## Requirements

- Python 3.11+ (recommended: 3.12)
- `pip`
- Optional for development: `pytest`, `black`, `isort`, `flake8` (via `requirements-dev.txt`)
- For all ATP-based step checks: **Vampire** as the external ATP

Note:

- Without an external ATP, only the internal rule checks run completely.
- Some steps (for example general `thm`/`cth` steps without an internal checker) need an ATP call.

## Installation on Linux

Run in the root directory of the repository:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

## Installation on Windows with WSL

On Windows, **WSL is currently required** if you want to use ATP checks with Vampire.
It is recommended running the project directly in a WSL shell (for example Ubuntu).

### 1) Prepare WSL (once)

In PowerShell as administrator:

```powershell
wsl --install
```

Then restart Windows and set up a distribution (for example Ubuntu).

### 2) Use the project in WSL

In the WSL shell, change into the repository. Windows drives are mounted under `/mnt/<drive letter>/`, so a clone in `C:\path\to\master-thesis-proover` is reached as follows (adjust the path to your clone, or clone the repository directly inside WSL):

```bash
cd /mnt/c/path/to/master-thesis-proover
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

Note on editors:

- The code can be edited in a Windows editor.
- Runs that involve the ATP should be started in the WSL terminal, not natively on Windows.

## External ATP integration (Vampire)

By default the checker looks for `vampire` in the `PATH`.
Optionally, the following variables can be set:

- `EXTERNAL_ATP_BINARY` (name or path of the binary only)
- `EXTERNAL_ATP_COMMAND` (complete command)

Examples:

```bash
export EXTERNAL_ATP_BINARY=/usr/local/bin/vampire
```

or:

```bash
export EXTERNAL_ATP_COMMAND="/path/to/vampire"   # the verifier adds --mode casc and --time_limit itself
```

If you start Python on Windows and Vampire is installed in WSL, a WSL wrapper can be used:

```powershell
$env:EXTERNAL_ATP_COMMAND = "wsl vampire"
```

It is still recommended running everything directly in WSL.

## Project structure

```
main.py                 entry point: command-line interface, step dispatch, verdict
src/
  parser/               Lark grammar (tptp_grammar.lark), parser, AST classes
  checker/              rule checkers (structural, propositional, quantifier, junction,
                        clausal/equational, Skolemization), provenance, dependencies,
                        alpha-equivalence, ATP interface (external_atp_checker.py)
  scoring/              expected results (PRV/TST/EXT_expected.csv) and ProoVer scoring
  performance/          run-time measurement for the batch mode of main.py
  deep_recursion.py     thread with a large stack for deeply nested formulas
scripts/                experiments and generators for the thesis (see below)
tests/                  pytest test suite
ProoVer2026/            proofs and problems (PRV, Deprecated, Test, Extra)
results/eval/           raw data of the evaluation in the thesis (from scripts/eval_all.py)
results/extra/          results of the rule-level test suite (from scripts/exp_extra_tests.py)
thesis/                 LaTeX sources of the thesis; thesis/generated/ is written by the scripts
```

## Command-line usage

All examples are run from the project root.

### 1) Proof sets and commands

```
ProoVer2026/
  PRV/          official ProoVer proofs (91) + Problems/
  Deprecated/   9 earlier sample proofs (PRV005, ...) + Problems/
  Test/         hand-written test proofs (TST) + Problems/
  Extra/        generated rule tests (EXT) + Problems/
```

| Goal | Command |
|---|---|
| Check one proof | `python main.py PROOF [-p PROBLEM]` |
| Check and score all proofs of a directory | `python main.py -d DIRECTORY` |
| Experiments of the thesis (run time, ablation, mutation, coverage, tables) | `python scripts/eval_all.py --parts all` |
| Re-score an existing result CSV | `python src/scoring/score_proofs.py` |

`main.py` is the tool for checking and scoring; `scripts/eval_all.py` is the experiment script of the thesis and not needed for normal use.

### 2) Check all proofs of a directory (batch mode)

Without a proof argument, `main.py` searches the directory for `*.s`, maps each proof to `Problems/*.p`, checks everything, and writes a summary and a scoring CSV.
The expected results are chosen from the directory name (`src/scoring/`); `-e` selects another CSV.

```bash
python main.py                             # default: ProoVer2026/PRV (official proofs)
python main.py -d ProoVer2026/Test         # hand-written test proofs (TST_expected.csv)
python main.py -d ProoVer2026/Extra        # generated rule tests (EXT_expected.csv)
python main.py -d ProoVer2026/Deprecated   # earlier sample proofs
python main.py -d ProoVer2026/PRV --prefix PRV01   # only files with this prefix
```

The results are written to `results/<directory name>_results.csv` (for example `PRV_results.csv`, `Test_results.csv`, `Extra_results.csv`) and the run times to `results/<directory name>_performance.csv`.

### 3) Check a single proof

```bash
python main.py ProoVer2026/PRV/PRV000+1.s
```

The problem file is then assumed to be `ProoVer2026/PRV/Problems/PRV000+1.p`.
With an explicit problem file:

```bash
python main.py ProoVer2026/PRV/PRV000+1.s -p ProoVer2026/PRV/Problems/PRV000+1.p
```

### 4) Increase the time limit per proof

The default is `30` seconds wall-clock time per proof.

All proofs with a higher limit:

```bash
python main.py -t 120
```

A single proof with a higher limit:

```bash
python main.py ProoVer2026/PRV/PRV010+1.s -t 90
```

### 5) Control the output

```bash
python main.py ProoVer2026/PRV/PRV010+1.s --quiet          # only the SZS line
python main.py --quiet                                     # batch: one SZS line per proof
python main.py ProoVer2026/PRV/PRV097+1.s --debug          # shows which checker handles which step
python main.py --binary-verdict                            # prints Unknown as VerifiedBad
```

### 6) All options

| Option | Mode | Meaning |
|---|---|---|
| `proof` | single | proof file (`.s`); without it, batch mode |
| `-p`, `--problem` | single | problem file, default `Problems/<name>.p` next to the proof |
| `-t`, `--timeout` | both | wall-clock limit per proof in seconds (default 30) |
| `-d`, `--dir` | batch | directory with `*.s` and `Problems/` (default `ProoVer2026/PRV`) |
| `-e`, `--expected` | batch | CSV with expected results (default chosen by directory name) |
| `--prefix` | batch | only proofs whose file name starts with this prefix |
| `--binary-verdict` | both | `VerifiedBad` instead of `Unknown` (two-valued output) |
| `--quiet` | both | only the SZS line per proof; errors go to stderr, CSVs are still written |
| `--debug` | both | sets `DEBUG_PROOF_FLOW`: dispatch of every step and ATP calls, marked `[DBG]` |

### 7) Show the command-line help

```bash
python main.py -h
```

## Output and results

When you run `main.py` you get:

- an SZS-style status per proof (`VerifiedGood`, `VerifiedBad`, `Unknown`, `Timeout`)
  - `Unknown` (three-valued verdict): no defect was found, but at least one step could not be decided (prover timeout, no answer, or no checker for the rule). The tool abstains (0 points).
  - `--binary-verdict` prints `VerifiedBad` instead (two-valued output).
- a summary over all proofs
- a performance report (wall-clock time per proof, without the start-up of the interpreter; the CPU time only covers the parent process)
- a scoring summary

Files:

- `results/<directory name>_results.csv` (scoring and results, for example `PRV_results.csv`)
- `results/<directory name>_performance.csv` (performance per proof)

Additional scoring script:

```bash
python src/scoring/score_proofs.py
```

With options:

```bash
python src/scoring/score_proofs.py -h
```

## Scripts (scripts/)

The scripts belong to the thesis and are not needed for normal use of the verifier.
All of them are started from the project root. Scripts that need Vampire use the same variables
`EXTERNAL_ATP_BINARY` / `EXTERNAL_ATP_COMMAND` as the verifier (on Windows, run them in WSL).

| Script | Purpose | Needs Vampire | Result in the thesis |
|---|---|---|---|
| `eval_all.py` | driver of the whole evaluation | yes (except `noatp`, `coverage`, `inputs`, `tables`) | all tables, numbers, and figures of Chapter 7 |
| `_eval_worker.py` | checks one proof in a fresh process (called by `eval_all.py`) | indirectly | run-time and memory values |
| `gen_extra_tests.py` | generates the Extra set (rule-level tests) | no | Section 7.2 |
| `exp_extra_tests.py` | checks the Extra set and compares with the expectation | yes | Section 7.2 |
| `run_vampire_all.sh` | runs Vampire on all problems | yes | case study in 8.3 |
| `exp_vampire_compat.py` | passes the Vampire proofs to the verifier | optional | table on unmodified Vampire proofs (8.3) |
| `exp_skolem_mutants.py` | compares the Skolem check with an entailment oracle | optional | table Skolem check vs. oracle (8.3) |
| `gen_dag_figure.py` | draws the dependency graph of a proof | no (Graphviz) | figure of `PRV089` (Design) |
| `gen_appendix_tables.py` | per-proof tables (status, run time) | no | no longer in the thesis, overview for the repository |

### eval_all.py

Runs all experiments of the evaluation and writes
raw data to `results/eval/` and LaTeX tables and `\providecommand` macros to `thesis/generated/`.
This way no number in the evaluation chapter is typed by hand.

```bash
python scripts/eval_all.py --parts all --reps 3      # everything (takes a while, needs Vampire)
python scripts/eval_all.py --parts runs,tables       # only the runs and the tables derived from them
python scripts/eval_all.py --parts tables            # only tables/macros/figures from existing raw data (seconds)
```

| Part | Content | Raw data |
|---|---|---|
| `runs` | every proof (PRV, Deprecated, Test, Extra) `--reps` times in a fresh process: verdict, steps, ATP calls, run time, memory | `runs.json`, `per_proof.csv` |
| `noatp` | the same runs with a prover command that does not exist (fail-closed test) | `noatp.json` |
| `internal` | a sample of internally checked steps, each also checked by Vampire | `internal.json` |
| `mutation` | mutations of valid proofs; accepted mutants are classified with Vampire | `mutation.json`, `mutation_misses.json` |
| `inputs` | ten broken inputs derived from `PRV010+1.s` | `inputs.json` |
| `extra` | regenerates the Extra set (`gen_extra_tests.py`) and evaluates it (`exp_extra_tests.py`) | `results/extra/results.csv` |
| `coverage` | test coverage with pytest-cov and lines per module | `coverage.json` |
| `tables` | regenerates tables, macros, and the figures `rule_coverage`, `runtime_scatter`, `mutation_outcomes` | - |

Notes:
- The statistics of the thesis refer to the 91 official PRV pairs; the 9 proofs in `Deprecated/` only enter the total row of the verdict matrix.
- The measured time of a proof runs from the start of the process to the verdict, as in the competition. The breakdown into phases (parsing, checks, ATP) is measured separately after the check and does not count towards the total.
- Commit, date, CPU, Python and Vampire version are recorded in `results/eval/env.json` and appear in the thesis (`\EvalCommit` etc.).

### _eval_worker.py

Internal helper of `eval_all.py`. Starts the verifier for exactly one proof in a new Python process,
writes the debug log into a buffer, and prints one JSON line with verdict, steps, ATP calls,
times, and peak memory. It can be called directly to debug a single measurement:

```bash
python scripts/_eval_worker.py ProoVer2026/PRV/PRV010+1.s ProoVer2026/PRV/Problems/PRV010+1.p
```

### gen_extra_tests.py and exp_extra_tests.py

`gen_extra_tests.py` generates, for the rules that the TST set hardly covers (resolution, paramodulation,
rewrite, transitivity, reflexivity, junction, quantifier, and structural rules), one correct base proof
and several variants with a known defect, plus some edge cases. Output: `ProoVer2026/Extra/` with
`EXTnnn+1.s`, `Problems/EXTnnn+1.p`, and `EXT_expected.csv`.

`exp_extra_tests.py` checks this set and also records whether the defect is reported by the checker of the rule itself
or only by the final `consequence` step. Output: `results/extra/results.csv` and `summary.json`.

```bash
python scripts/gen_extra_tests.py                 # regenerate the Extra set (overwrites ProoVer2026/Extra)
python scripts/exp_extra_tests.py --timeout 60    # evaluate the Extra set
```

Useful when a new rule checker is added: extend the generator, regenerate the set, and evaluate it.

### run_vampire_all.sh

Runs Vampire in CASC mode on all 176 problems in `ProoVer2026/PRV/Problems`, `ProoVer2026/Deprecated/Problems`,
and `ProoVer2026/Test/Problems`, and stores the SZS results and the proofs in `results/vampire/`
(`summary.csv`, `raw/`, `proofs/`). This is the basis of the case study on transfer to other provers (Chapter 8.3).
The deprecated pairs are included on purpose, so that the numbers of the thesis (176 problems) are reproduced.

```bash
bash scripts/run_vampire_all.sh                      # all problems
bash scripts/run_vampire_all.sh PRV000+1 PRV010+1    # only selected problems
TIMEOUT=30 JOBS=4 VAMPIRE=/path/to/vampire bash scripts/run_vampire_all.sh
```

### exp_vampire_compat.py

Evaluates the proofs produced by `run_vampire_all.sh`: whether a proof (and not a saturation) was produced,
whether the parser accepts the file, which inference rules occur and how many of them belong to the ProoVer vocabulary,
the size of the proofs, and, with `--verify`, the verdict of the verifier.
Output: `results/vampire/compat.csv` and `compat_summary.json`.

```bash
python scripts/exp_vampire_compat.py --verify --timeout 60
```

### exp_skolem_mutants.py

Takes the Skolemization steps of the reference proofs, generates mutants with a known defect
(`drop_arg`, `universal`, `negate_atom`, `drop_conjunct`), and compares the internal Skolem check with an
entailment oracle (Vampire checks whether the conclusion implies the premise). This shows which defects a pure
entailment test misses. Without `--vampire`, only the checker is evaluated. The expected results of the proofs are read from
`results/PRV_results.csv`, `results/Deprecated_results.csv`, and `results/Test_results.csv`, so run
`python main.py -d ProoVer2026/PRV`, `-d ProoVer2026/Deprecated`, and `-d ProoVer2026/Test` first.
Output: `results/skolem_mutants.csv` and `skolem_mutants_summary.json`.

```bash
python scripts/exp_skolem_mutants.py --vampire /path/to/vampire --max-per-proof 10 --timeout 10
```

### gen_dag_figure.py

Draws the dependency graph of a TSTP proof with Graphviz (`dot` must be installed).
Nodes are the formulas, edges lead from a parent to the derived step, and the color shows
which check validates the node (provenance, negated conjecture, Skolem, internal checker, shortcut, ATP).
Useful to understand or debug individual proofs.

```bash
python scripts/gen_dag_figure.py ProoVer2026/PRV/PRV089+1.s thesis/diagrams/dag_prv089
```

### gen_appendix_tables.py

Generates tables with the status, assessment, and run time of every proof from `results/eval/runs.json`
(`thesis/generated/tab_app_prv.tex`, `tab_app_tst.tex`, `tab_app_ext.tex`, as `longtable`).
The shortened thesis no longer includes them, but they are a compact overview per proof.

```bash
python scripts/gen_appendix_tables.py
```

## Reproducing the results of the thesis

1. Install as described above, with Vampire 5.0.1 in the `PATH` or configured via `EXTERNAL_ATP_BINARY`.
2. Tests: `pytest` (291 tests run without a prover, 2 need Vampire).
3. Evaluation: `python scripts/eval_all.py --parts all --reps 3` (several minutes; avoid other load on the machine).
4. Optionally the case study of Chapter 8.3:
   `bash scripts/run_vampire_all.sh`, then `python scripts/exp_vampire_compat.py --verify` and `python scripts/exp_skolem_mutants.py --vampire <path>`.

The raw data of the run reported in the thesis are in `results/eval/` and `results/extra/` (commit: see `results/eval/env.json`).

## Tests and development

Tests from the project root:

```bash
pytest
```

Formatting and linting (optional):

```bash
black .
isort .
flake8
```

## Troubleshooting

- `ATP executable not found`: Vampire is not installed or not in the `PATH`.
- ATP calls fail on Windows: start the run in the WSL terminal.
- `Proof file not found` or `Problem file not found`: check the paths and start from the project root.
- Many timeouts: increase `-t` (for example `-t 120`) and check that Vampire can be reached.
