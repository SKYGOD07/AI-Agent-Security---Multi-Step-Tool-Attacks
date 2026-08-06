"""Verification script for omega_v3_attack.ipynb."""
import json
import base64
from pathlib import Path

nb_path = Path(__file__).resolve().parent.parent.parent / "notebooks" / "omega_v3_attack.ipynb"
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
    "def run(": "run() method",
    "def _fill(": "_fill() method",
    "REPLAY_SAFE_FRAC = 0.98": "Replay safety fraction (0.98)",
    "SPLIT_CLASSIFY_N = 7": "Classification sample count (7)",
    "BURST_K = 1": "Single post for fast row",
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

print("\nALL CHECKS PASSED — OMEGA v3 Notebook is valid!")
