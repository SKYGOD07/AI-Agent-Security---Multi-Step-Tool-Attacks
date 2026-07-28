import json

# Load v16 as the trusted base
with open('our_work/notebooks/stockfish_v16_attack.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Update title
nb['cells'][0]['source'][0] = '# AI Agent Security \u2014 Multi-Step Tool Attacks \u00b7 **Submission notebook v23**\n'

# Get the attack.py code cell (index 2)
code_cell = nb['cells'][2]
code = ''.join(code_cell['source'])

# v23 upgrade: enable PROBE_HOPS=1 with conservative REPLAY_COST_COEF=2.0
# This is the ONLY safe throughput lever in v16's own docstring:
#   'Probing at PROBE_HOPS=1 skips the scoring-irrelevant wrap-up generation
#    for a ~1.5-2x faster fill'
# Each candidate still fires identically at hops=8 during replay.
# REPLAY_COST_COEF=2.0 conservatively scales the measured hops=1 elapsed
# back up so REPLAY_SAFE_SIZING doesn't under-count and risk a void.

old_probe = "PROBE_HOPS = 0                # 0 == probe at the grader's max_tool_hops (today's 8)"
new_probe = "PROBE_HOPS = 1                # probe at 1 hop for ~1.5-2x faster fill throughput"

old_coef = "REPLAY_COST_COEF = 1.0        # measured elapsed x this == estimated hops=8 replay cost"
new_coef = "REPLAY_COST_COEF = 2.0        # conservative: hops=1 probe is ~2x cheaper than hops=8 replay"

code = code.replace(old_probe, new_probe)
code = code.replace(old_coef, new_coef)

# Split back into lines for the notebook cell format
lines = code.split('\n')
code_cell['source'] = [line + '\n' for line in lines[:-1]]
if lines[-1]:
    code_cell['source'].append(lines[-1])

# Write v23
with open('our_work/notebooks/stockfish_v23_attack.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

cell_count = len(nb['cells'])
print(f'v23 created successfully with {cell_count} cells')

# Verify the changes took effect
final_code = ''.join(code_cell['source'])
assert 'PROBE_HOPS = 1' in final_code, 'PROBE_HOPS replacement failed!'
assert 'REPLAY_COST_COEF = 2.0' in final_code, 'REPLAY_COST_COEF replacement failed!'
assert 'BURST_K = 1' in final_code, 'BURST_K must remain 1!'
assert 'SLOW_MULTIPOST_N = 1' in final_code, 'SLOW_MULTIPOST_N must remain 1!'
print('All safety assertions passed:')
print('  PROBE_HOPS = 1 (faster fill)')
print('  REPLAY_COST_COEF = 2.0 (conservative cost scaling)')
print('  BURST_K = 1 (single post per candidate)')
print('  SLOW_MULTIPOST_N = 1 (single post on slow row)')
