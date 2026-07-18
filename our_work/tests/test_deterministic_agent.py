import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# We MUST mock sys.modules BEFORE importing the things that fail.
# Since pytest collects files and runs them, the imports at module level
# will trigger the ModuleNotFoundError before our fixture runs.
# We patch sys.modules right here at the top level of the test file.

# A safer approach is to preserve original sys.modules and restore it,
# but for a test suite where `core.env` doesn't exist at all on the system,
# mocking it globally in the test file is sometimes the only way if it's deeply nested.
# Let's create a dummy module structure dynamically instead to be cleaner,
# or just mock it. We will use a try-finally block around the test execution.
# Actually, since it's just missing `env`, let's just create dummy modules in `sys.modules`.

_mock_modules = {
    'aicomp_sdk.core.env': MagicMock(),
    'aicomp_sdk.core.env.api': MagicMock(),
    'aicomp_sdk.core.env.sandbox': MagicMock(),
    'aicomp_sdk.core.env.gym': MagicMock(),
    'aicomp_sdk.core.env.opaque': MagicMock()
}
sys.modules.update(_mock_modules)

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root / "our_work"))
sys.path.insert(0, str(project_root / "ai-agent-security-multi-step-tool-attacks"))

import pytest
from aicomp_sdk.agents.deterministic_agent import VulnerableDeterministicAgent
from aicomp_sdk.agents.types import AGENT_STATE_VERSION, AgentStateVersionError

def test_snapshot_state():
    """Test the snapshot_state function returns correct state representation."""
    agent = VulnerableDeterministicAgent()

    # Verify initial snapshot
    snapshot = agent.snapshot_state()
    assert snapshot["version"] == AGENT_STATE_VERSION
    assert snapshot["backend"] == "deterministic"
    assert snapshot["data"]["next_call_index"] == 1

    # Change agent state to verify snapshot reflects changes
    agent._next_call_index = 5
    snapshot2 = agent.snapshot_state()
    assert snapshot2["data"]["next_call_index"] == 5

def test_restore_state_valid():
    """Test the restore_state function correctly restores state."""
    agent = VulnerableDeterministicAgent()

    # Valid restore
    valid_snapshot = {
        "version": AGENT_STATE_VERSION,
        "backend": "deterministic",
        "data": {"next_call_index": 10},
    }
    agent.restore_state(valid_snapshot)
    assert agent._next_call_index == 10

def test_restore_state_invalid_version():
    agent = VulnerableDeterministicAgent()
    invalid_version_snapshot = {
        "version": AGENT_STATE_VERSION + 1,
        "backend": "deterministic",
        "data": {"next_call_index": 10},
    }
    with pytest.raises(AgentStateVersionError, match="Unsupported agent snapshot version"):
        agent.restore_state(invalid_version_snapshot)

def test_restore_state_invalid_backend():
    agent = VulnerableDeterministicAgent()
    invalid_backend_snapshot = {
        "version": AGENT_STATE_VERSION,
        "backend": "not_deterministic",
        "data": {"next_call_index": 10},
    }
    with pytest.raises(AgentStateVersionError, match="Unsupported agent snapshot backend"):
        agent.restore_state(invalid_backend_snapshot)

def test_restore_state_missing_data():
    agent = VulnerableDeterministicAgent()
    missing_data_snapshot = {
        "version": AGENT_STATE_VERSION,
        "backend": "deterministic",
        "data": {},
    }
    # It should fallback to 1 as per the agent's implementation
    agent.restore_state(missing_data_snapshot)
    assert agent._next_call_index == 1

# Cleanup mocked modules after tests
def teardown_module(module):
    for mod in _mock_modules:
        if mod in sys.modules:
            del sys.modules[mod]
