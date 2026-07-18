import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the source tree to the sys path so imports can be resolved
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

class TestVulnerableDeterministicAgent(unittest.TestCase):
    @patch.dict(sys.modules, {
        'aicomp_sdk.core.env': MagicMock(),
        'aicomp_sdk.core.env.api': MagicMock(),
        'aicomp_sdk.core.env.sandbox': MagicMock(),
        'aicomp_sdk.core.env.gym': MagicMock()
    })
    def test_reset_state(self):
        from aicomp_sdk.agents.deterministic_agent import VulnerableDeterministicAgent
        agent = VulnerableDeterministicAgent()
        agent._next_debug_turn_index = 5
        agent._next_call_index = 10

        agent.reset_state()

        self.assertEqual(agent._next_debug_turn_index, 1)
        self.assertEqual(agent._next_call_index, 1)

if __name__ == "__main__":
    unittest.main()
