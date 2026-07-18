import sys
import unittest
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from aicomp_sdk.agents.deterministic_agent import VulnerableDeterministicAgent
from aicomp_sdk.agents.types import AGENT_STATE_VERSION, AgentStateVersionError

class TestDeterministicAgent(unittest.TestCase):
    def test_restore_state_success(self):
        agent = VulnerableDeterministicAgent()
        agent.restore_state({
            "version": AGENT_STATE_VERSION,
            "backend": "deterministic",
            "data": {"next_call_index": 5}
        })
        self.assertEqual(agent._next_call_index, 5)

    def test_restore_state_default_call_index(self):
        agent = VulnerableDeterministicAgent()
        agent.restore_state({
            "version": AGENT_STATE_VERSION,
            "backend": "deterministic",
            "data": {}
        })
        self.assertEqual(agent._next_call_index, 1)

    def test_restore_state_unsupported_version(self):
        agent = VulnerableDeterministicAgent()
        with self.assertRaisesRegex(AgentStateVersionError, "Unsupported agent snapshot version: 999"):
            agent.restore_state({
                "version": 999,
                "backend": "deterministic",
                "data": {"next_call_index": 5}
            })

    def test_restore_state_unsupported_backend(self):
        agent = VulnerableDeterministicAgent()
        with self.assertRaisesRegex(AgentStateVersionError, "Unsupported agent snapshot backend: invalid_backend"):
            agent.restore_state({
                "version": AGENT_STATE_VERSION,
                "backend": "invalid_backend",
                "data": {"next_call_index": 5}
            })

if __name__ == "__main__":
    unittest.main()
