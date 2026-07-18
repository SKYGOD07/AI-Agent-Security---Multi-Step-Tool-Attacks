import sys
import types
from unittest.mock import patch
import pytest

# Use a fixture to safely mock the missing modules so we don't pollute sys.modules globally
@pytest.fixture(autouse=True)
def mock_missing_env_modules():
    env_mod = types.ModuleType('aicomp_sdk.core.env')

    api_mod = types.ModuleType('aicomp_sdk.core.env.api')
    api_mod.AttackEnvProtocol = type('AttackEnvProtocol', (), {})
    api_mod.DiagnosticsEnv = type('DiagnosticsEnv', (), {})
    api_mod.EnvInteractionResult = type('EnvInteractionResult', (), {})
    api_mod.EnvRunDiagnostics = type('EnvRunDiagnostics', (), {})
    api_mod.EnvSelection = type('EnvSelection', (), {})
    api_mod.coerce_env_selection = lambda *args, **kwargs: None
    api_mod.DEFAULT_MAX_TOOL_HOPS = 10

    sandbox_mod = types.ModuleType('aicomp_sdk.core.env.sandbox')
    sandbox_mod.SandboxEnv = type('SandboxEnv', (), {})

    gym_mod = types.ModuleType('aicomp_sdk.core.env.gym')
    gym_mod.GymAttackEnv = type('GymAttackEnv', (), {})

    modules_to_patch = {
        'aicomp_sdk.core.env': env_mod,
        'aicomp_sdk.core.env.api': api_mod,
        'aicomp_sdk.core.env.sandbox': sandbox_mod,
        'aicomp_sdk.core.env.gym': gym_mod
    }

    with patch.dict('sys.modules', modules_to_patch):
        yield

def test_coerce_agent_selection_valid_strings():
    # Import inside the test to ensure sys.modules is patched during import
    from aicomp_sdk.agents.factory import coerce_agent_selection, AgentSelection
    assert coerce_agent_selection("auto") == AgentSelection.AUTO
    assert coerce_agent_selection("deterministic") == AgentSelection.DETERMINISTIC
    assert coerce_agent_selection("openai") == AgentSelection.OPENAI
    assert coerce_agent_selection("gpt_oss") == AgentSelection.GPT_OSS
    assert coerce_agent_selection("gemma") == AgentSelection.GEMMA
    assert coerce_agent_selection("gemma_4") == AgentSelection.GEMMA_4

def test_coerce_agent_selection_valid_enum():
    from aicomp_sdk.agents.factory import coerce_agent_selection, AgentSelection
    assert coerce_agent_selection(AgentSelection.AUTO) == AgentSelection.AUTO
    assert coerce_agent_selection(AgentSelection.DETERMINISTIC) == AgentSelection.DETERMINISTIC

def test_coerce_agent_selection_invalid_string():
    from aicomp_sdk.agents.factory import coerce_agent_selection
    with pytest.raises(ValueError, match="Unsupported agent selection: invalid"):
        coerce_agent_selection("invalid")
