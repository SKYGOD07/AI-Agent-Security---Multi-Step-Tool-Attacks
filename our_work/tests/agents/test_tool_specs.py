import unittest
from unittest.mock import MagicMock, patch


class TestToolSpecs(unittest.TestCase):
    """Unit tests for tool_specs functions."""

    def setUp(self):
        # Create mocks for missing modules
        self.mock_env = MagicMock()
        self.mock_api = MagicMock()
        self.mock_api.DEFAULT_MAX_TOOL_HOPS = 10
        self.mock_sandbox = MagicMock()
        self.mock_gym = MagicMock()

        # We use patch.dict to safely mock sys.modules for the duration of the test
        self.modules_patcher = patch.dict('sys.modules', {
            'aicomp_sdk.core.env': self.mock_env,
            'aicomp_sdk.core.env.api': self.mock_api,
            'aicomp_sdk.core.env.sandbox': self.mock_sandbox,
            'aicomp_sdk.core.env.gym': self.mock_gym,
        })
        self.modules_patcher.start()

    def tearDown(self):
        self.modules_patcher.stop()

    def test_to_agent_tool_spec(self):
        """Verify that to_agent_tool_spec correctly maps fields and converts the schema to a dict."""
        # Imports are placed inside the test to ensure they happen after sys.modules is patched
        from aicomp_sdk.agents.tool_specs import to_agent_tool_spec
        from aicomp_sdk.agents.types import AgentToolSpec
        from aicomp_sdk.core.tools.models import RuntimeToolSpec, ToolSideEffect, ToolScope

        schema = {
            "type": "object",
            "properties": {
                "arg1": {"type": "string"}
            },
            "required": ["arg1"]
        }

        runtime_spec = RuntimeToolSpec(
            name="test_tool",
            description="A test tool description",
            side_effect=ToolSideEffect.READ,
            scope=ToolScope.PUBLIC,
            parameters_json_schema=schema,
        )

        agent_spec = to_agent_tool_spec(runtime_spec)

        self.assertIsInstance(agent_spec, AgentToolSpec)
        self.assertEqual(agent_spec.name, "test_tool")
        self.assertEqual(agent_spec.description, "A test tool description")
        self.assertEqual(agent_spec.parameters_json_schema, schema)
        self.assertTrue(agent_spec.strict)

        # Verify that parameters_json_schema is a new dict
        self.assertEqual(agent_spec.parameters_json_schema, schema)
        self.assertIsNot(agent_spec.parameters_json_schema, schema)


if __name__ == "__main__":
    unittest.main()
