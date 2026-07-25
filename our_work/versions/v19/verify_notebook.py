import json

with open(r'c:\OPENAI AI AGENT CYBERSEC\our_work\stockfish_v19_attack.ipynb', 'r') as f:
    nb = json.load(f)

cells = nb["cells"]
print(f"Total cells: {len(cells)}")
for i, cell in enumerate(cells):
    src = "".join(cell["source"])
    ct = cell["cell_type"]
    first_line = src.split("\n")[0][:80]
    print(f"  Cell {i+1}: {ct} - {first_line}")

checks = {"writefile": False, "IS_RERUN": False, "JED": False}
for cell in cells:
    src = "".join(cell["source"])
    if "%%writefile" in src:
        checks["writefile"] = True
    if "IS_RERUN" in src:
        checks["IS_RERUN"] = True
    if "JEDAttackInferenceServer" in src:
        checks["JED"] = True

for k, v in checks.items():
    print(f"{'OK' if v else 'FAIL'}: {k} {'found' if v else 'MISSING'}")
