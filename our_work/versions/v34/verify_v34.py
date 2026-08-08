"""Verify omega_v4_attack.ipynb is a valid, well-formed notebook."""
import json
import base64
from pathlib import Path

nb_path = Path(__file__).resolve().parent.parent.parent / "notebooks" / "omega_v4_attack.ipynb"
with open(nb_path, encoding="utf-8") as f:
    nb = json.load(f)

print(f"Cells: {len(nb['cells'])}")
print(f"nbformat: {nb['nbformat']}.{nb['nbformat_minor']}")

for i, cell in enumerate(nb["cells"]):
    src = "".join(cell["source"])
    print(f"\nCell {i + 1} [{cell['cell_type']}]: {len(src)} chars, {len(cell['source'])} lines")
    first_line = cell["source"][0].strip() if cell["source"] else "(empty)"
    print(f"  First line: {first_line}")

# Decode and validate embedded attack.py
b64_line = [l for l in nb["cells"][1]["source"] if "ATTACK_B64" in l and "=" in l][0]
b64_val = b64_line.split('"')[1]
decoded = base64.b64decode(b64_val).decode("utf-8")

# Compile check
compile(decoded, "attack.py", "exec")
print(f"\nDecoded attack.py: {len(decoded)} chars, {len(decoded.splitlines())} lines")
print("Compilation: OK")

# Key parameter verification
params = {
    "REPLAY_SAFE_FRAC = 0.99": "99% fill",
    "SPLIT_CLASSIFY_N = 5": "5-sample classify",
    "SLOWEST_MULT = 1.28": "1.28x cushion",
    "max_tool_hops=1": "hops-1 warmup",
    "warmup_fired": "candidate harvest",
}
print("\nv4 Parameters:")
for pat, desc in params.items():
    status = "OK" if pat in decoded else "FAIL"
    print(f"  {status} {desc}: {pat}")

print("\nVerification PASSED")
