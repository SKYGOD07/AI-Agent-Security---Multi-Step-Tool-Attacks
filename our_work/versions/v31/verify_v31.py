"""Verify omega_v1_attack.ipynb is a valid, well-formed notebook."""
import json
import base64
from pathlib import Path

nb_path = Path(__file__).resolve().parent.parent.parent / "notebooks" / "omega_v1_attack.ipynb"
with open(nb_path) as f:
    nb = json.load(f)

print(f"Cells: {len(nb['cells'])}")
print(f"nbformat: {nb['nbformat']}.{nb['nbformat_minor']}")

for i, cell in enumerate(nb["cells"]):
    src = "".join(cell["source"])
    print(f"Cell {i} ({cell['id']}): {len(src)} chars, type={cell['cell_type']}")

# Decode attack.py
b64_line = [l for l in nb["cells"][1]["source"] if "ATTACK_B64" in l and "=" in l][0]
b64 = b64_line.split('"')[1]
code = base64.b64decode(b64).decode()

# Verify it compiles as valid Python
compile(code, "attack.py", "exec")
print(f"attack.py compiles OK ({len(code)} chars, {len(code.splitlines())} lines)")

# Check critical patterns
patterns = {
    "class AttackAlgorithm(AttackAlgorithmBase)": "Class definition",
    "def run(self, env, config)": "run() method",
    "def _fill(self, env, budget, hops)": "_fill() method",
    "def _check(self, env)": "_check() predicate probe",
    "def _exf(self, env)": "_exf() quick check",
    "REPLAY_FRAC = 0.97": "Replay safety fraction",
    "SLOW_N = 4": "Multi-post count",
    "fs.delete": "Destructive write",
}
for pat, desc in patterns.items():
    assert pat in code, f"Missing: {desc}"
    print(f"  [OK] {desc}")

# Check submission cell
cell3 = "".join(nb["cells"][2]["source"])
assert "IS_RERUN" in cell3
assert "server.serve()" in cell3
assert "submission.csv" in cell3
print("  [OK] Submission cell format")

print("\nALL CHECKS PASSED - Notebook is valid!")
