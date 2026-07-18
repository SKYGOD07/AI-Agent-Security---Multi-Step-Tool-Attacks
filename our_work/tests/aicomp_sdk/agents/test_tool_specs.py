"""Tests for agent tool specifications and transformations."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Mock out broken imports from aicomp_sdk before importing anything that depends on it.
# We do this cleanly by saving the original sys.modules state.
_original_modules = set(sys.modules.keys())

sys.modules["aicomp_sdk.core.env"] = MagicMock()
sys.modules["aicomp_sdk.core.env.api"] = MagicMock()
sys.modules["aicomp_sdk.core.env.sandbox"] = MagicMock()
sys.modules["aicomp_sdk.core.env.gym"] = MagicMock()

# Add our_work to sys.path so we can resolve aicomp_sdk correctly
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from aicomp_sdk.agents.tool_specs import to_hf_function_tool
from aicomp_sdk.agents.types import AgentToolSpec


class TestToolSpecs(unittest.TestCase):
    """Verifies correctness of tool specification transformations."""

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up mocked modules to avoid test pollution."""
        for module in list(sys.modules.keys()):
            if module not in _original_modules and module.startswith("aicomp_sdk.core.env"):
                del sys.modules[module]

        if str(project_root) in sys.path:
            sys.path.remove(str(project_root))

    def test_to_hf_function_tool(self) -> None:
        """Validate to_hf_function_tool outputs correct JSON schema format for HF."""
        spec = AgentToolSpec(
            name="test_tool",
            description="A test tool",
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                },
                "required": ["param1"],
            },
            strict=True,
        )

        hf_tool = to_hf_function_tool(spec)

        self.assertEqual(hf_tool["type"], "function")
        self.assertIn("function", hf_tool)
        self.assertEqual(hf_tool["function"]["name"], "test_tool")
        self.assertEqual(hf_tool["function"]["description"], "A test tool")
        self.assertEqual(
            hf_tool["function"]["parameters"],
            {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                },
                "required": ["param1"],
            },
        )

if __name__ == "__main__":
    unittest.main()
