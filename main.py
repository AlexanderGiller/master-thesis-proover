from src.parser.parser import load_proof, parse_file, parse_file_pretty


parse_file_pretty("Problems/example1_proover.p")
problem = parse_file("Problems/example1_proover.p")

print("=== Problem steps ===")
for step in problem:
    print(f"  {step.name} [{step.role}]")

proof = load_proof("Proofs/example1_proover_proof.p")
print(f"\n=== Proof (ref: '{proof.problem_ref}') ===")
for step in proof.steps:
    inf = step.inference
    if inf:
        print(f"  {step.name} [{step.role}] via {inf.rule}({inf.status}) ← {inf.parents}")
    else:
        print(f"  {step.name} [{step.role}] (no inference)")
