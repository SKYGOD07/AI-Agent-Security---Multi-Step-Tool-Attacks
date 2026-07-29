import base64
import json

with open("zOthers works/jed-multi-step-attack.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

# Line 1 of cell 1 contains: ATTACK_PY_B64 = "..."
b64_line = nb["cells"][1]["source"][1]

# Find the base64 content between quotes
q1 = b64_line.find('"')
q2 = b64_line.rfind('"')
b64_str = b64_line[q1+1:q2]

attack_py = base64.b64decode(b64_str).decode("utf-8")
print(f"Decoded attack.py: {len(attack_py)} bytes")

# Save decoded attack.py for inspection
with open("our_work/jed_attack_decoded_v24.py", "w", encoding="utf-8") as f:
    f.write(attack_py)

print("Saved to our_work/jed_attack_decoded_v24.py")

# Check key features
assert "REPLAY_SAFE = 0.99" in attack_py, "Missing REPLAY_SAFE = 0.99"
assert "inj_close" in attack_py, "Missing inj_close"
assert "class AttackAlgorithm" in attack_py, "Missing AttackAlgorithm"
print("All key features present!")
