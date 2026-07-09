from src.parser.parser import load_proof, parse_file, parse_file_pretty
from src.checker.file_dir import check_axiom_provenance


problem_path = "examples/correct/Problems/COR002+1.p"
proof_path = "examples/correct/COR002+1.s"

problem_formulas = {f.name: f for f in parse_file(problem_path)}
proof = load_proof(proof_path)

for step in proof.steps:
    if step.role != "axiom":
        continue
    issues = check_axiom_provenance(step, problem_formulas, problem_path)
    if issues:
        for issue in issues:
            print(f"[FAIL] {issue.formula_name}: {issue.reason}")
    else:
        print(f"[OK] {step.name} correctly cites and matches the problem file")

