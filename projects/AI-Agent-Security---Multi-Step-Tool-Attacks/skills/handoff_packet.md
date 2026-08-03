# Handoff Packet: Red-Team AI Agent Security Engine

> **IMPORTANT**: The primary, comprehensive, 1000+ line handoff thesis for this repository is located at:
> 
> 📄 **[MASTER_AI_HANDOFF_THESIS.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/MASTER_AI_HANDOFF_THESIS.md)**

## Quick Handoff Summary
- **Current Version**: `stockfish_v29_attack.ipynb` (Decoded from `ai-agent-security-90.ipynb`, **Public Score Target: 90.090+**)
- **Key Mechanics**: Asymmetric Dual-Track Multi-Post Routing (`SLOW_MULTIPOST_N = 4` for `gpt_oss` via token forging, `BURST_K = 2` for `gemma`).
- **Scaffolding**: Base64 attack script encoding + defensive `try/except` imports + defensive `__init__` (Zero Format Error Guarantee).
