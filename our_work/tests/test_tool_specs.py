"""Unit tests for tool_specs.py, specifically build_openai_tool_name_maps."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Important: Setup paths BEFORE importing
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tests.mocks.env_mock import patch_env_modules

class TestToolSpecs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # We must keep the patch active for the entire duration of the tests in this class
        # because the methods we test might rely on the imported classes
        cls.patcher = patch_env_modules()
        cls.patcher.__enter__()

        # Now it is safe to import
        global AgentToolSpec, build_openai_tool_name_maps
        from aicomp_sdk.agents.types import AgentToolSpec
        from aicomp_sdk.agents.tool_specs import build_openai_tool_name_maps

    @classmethod
    def tearDownClass(cls):
        cls.patcher.__exit__(None, None, None)

    def test_build_openai_tool_name_maps_happy_path(self):
        tools = [
            AgentToolSpec(name="my_tool_1", description="desc 1", parameters_json_schema={}),
            AgentToolSpec(name="my_tool_2", description="desc 2", parameters_json_schema={}),
        ]
        canonical, openai = build_openai_tool_name_maps(tools)

        self.assertEqual(canonical, {"my_tool_1": "my_tool_1", "my_tool_2": "my_tool_2"})
        self.assertEqual(openai, {"my_tool_1": "my_tool_1", "my_tool_2": "my_tool_2"})

    def test_build_openai_tool_name_maps_sanitization(self):
        tools = [
            AgentToolSpec(name="invalid tool name!", description="desc", parameters_json_schema={}),
            AgentToolSpec(name="-leading_and_trailing-", description="desc", parameters_json_schema={}),
        ]
        canonical, openai = build_openai_tool_name_maps(tools)

        # 'invalid tool name!' becomes 'invalid_tool_name_' but trailing _ is stripped so 'invalid_tool_name'
        self.assertEqual(canonical["invalid tool name!"], "invalid_tool_name")
        self.assertEqual(openai["invalid_tool_name"], "invalid tool name!")

        # '-leading_and_trailing-' remains '-leading_and_trailing-' because '-' is allowed
        self.assertEqual(canonical["-leading_and_trailing-"], "-leading_and_trailing-")
        self.assertEqual(openai["-leading_and_trailing-"], "-leading_and_trailing-")

    def test_build_openai_tool_name_maps_collisions(self):
        tools = [
            AgentToolSpec(name="tool 1", description="desc", parameters_json_schema={}),
            AgentToolSpec(name="tool-1", description="desc", parameters_json_schema={}),
            AgentToolSpec(name="tool_1", description="desc", parameters_json_schema={}),
        ]
        canonical, openai = build_openai_tool_name_maps(tools)

        # All three sanitize to 'tool_1', but should be resolved without collisions
        # The exact suffixes depend on hashes, but all values in `canonical` should be unique.

        aliases = list(canonical.values())
        self.assertEqual(len(aliases), 3)
        self.assertEqual(len(set(aliases)), 3)

        # One of them should get the base name
        self.assertIn("tool_1", aliases)

        for name, alias in canonical.items():
            self.assertEqual(openai[alias], name)

    def test_build_openai_tool_name_maps_empty_name(self):
        # Tools whose sanitized name becomes empty string should fall back to 'tool'
        tools = [
            AgentToolSpec(name="!!!", description="desc", parameters_json_schema={}),
            AgentToolSpec(name="???", description="desc", parameters_json_schema={}),
        ]
        canonical, openai = build_openai_tool_name_maps(tools)

        aliases = list(canonical.values())
        self.assertEqual(len(set(aliases)), 2)

        for name, alias in canonical.items():
            self.assertEqual(openai[alias], name)
            self.assertTrue(alias.startswith("tool"))

    def test_build_openai_tool_name_maps_max_length(self):
        # _OPENAI_TOOL_NAME_MAX_LEN = 64
        long_name = "a" * 70
        tools = [
            AgentToolSpec(name=long_name, description="desc", parameters_json_schema={}),
        ]
        canonical, openai = build_openai_tool_name_maps(tools)

        alias = canonical[long_name]
        self.assertTrue(len(alias) <= 64)
        self.assertEqual(openai[alias], long_name)

    def test_build_openai_tool_name_maps_multiple_max_length_collisions(self):
        long_name_1 = "a" * 70
        long_name_2 = "a" * 70 + "b"
        tools = [
            AgentToolSpec(name=long_name_1, description="desc 1", parameters_json_schema={}),
            AgentToolSpec(name=long_name_2, description="desc 2", parameters_json_schema={}),
        ]

        canonical, openai = build_openai_tool_name_maps(tools)

        self.assertEqual(len(canonical), 2)
        self.assertEqual(len(set(canonical.values())), 2)

        for name, alias in canonical.items():
            self.assertTrue(len(alias) <= 64)
            self.assertEqual(openai[alias], name)

# This prevents pytest from trying to collect the classes we use as mocks.
__test__ = True

if __name__ == "__main__":
    unittest.main()
