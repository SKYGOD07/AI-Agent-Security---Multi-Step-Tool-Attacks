from aicomp_sdk.agents.tool_specs import to_openai_function_tool
from aicomp_sdk.agents.types import AgentToolSpec

def test_to_openai_function_tool():
    """Verify standard tool mapping."""
    agent_spec = AgentToolSpec(
        name="test_tool",
        description="A test tool",
        parameters_json_schema={"type": "object", "properties": {"a": {"type": "string"}}},
        strict=True,
    )
    result = to_openai_function_tool(agent_spec)
    assert result["type"] == "function"
    assert result["name"] == "test_tool"
    assert result["description"] == "A test tool"
    assert result["strict"] == True
    assert result["parameters"]["type"] == "object"

def test_to_openai_function_tool_name_override():
    """Verify name can be overridden."""
    agent_spec = AgentToolSpec(
        name="test_tool",
        description="A test tool",
        parameters_json_schema={"type": "object", "properties": {"a": {"type": "string"}}},
        strict=True,
    )
    result = to_openai_function_tool(agent_spec, name_override="override_name")
    assert result["name"] == "override_name"

def test_to_openai_function_tool_non_strict():
    """Verify non-strict mode doesn't apply OpenAI strict schema rewriting."""
    agent_spec = AgentToolSpec(
        name="test_tool",
        description="A test tool",
        parameters_json_schema={"type": "object", "properties": {"a": {"type": "string"}}},
        strict=False,
    )
    result = to_openai_function_tool(agent_spec)
    assert result["strict"] == False
    assert result["parameters"]["properties"]["a"]["type"] == "string" # should not be wrapped in anyOf null

def test_to_openai_function_tool_empty_schema():
    """Verify behavior with empty schema."""
    agent_spec = AgentToolSpec(
        name="test_tool",
        description="A test tool",
        parameters_json_schema={},
        strict=True,
    )
    result = to_openai_function_tool(agent_spec)
    assert result["parameters"] == {}

def test_to_openai_function_tool_complex_schema():
    """Verify correct strict property rewriting."""
    agent_spec = AgentToolSpec(
        name="test_tool",
        description="A test tool",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "a": {"type": "string"},
                "b": {"type": "integer"}
            },
            "required": ["a"]
        },
        strict=True,
    )
    result = to_openai_function_tool(agent_spec)

    # 'a' is required, so it stays as string
    assert result["parameters"]["properties"]["a"]["type"] == "string"

    # 'b' is optional, so strict mode rewrites it to anyOf null
    b_prop = result["parameters"]["properties"]["b"]
    assert "anyOf" in b_prop
    assert {"type": "integer"} in b_prop["anyOf"]
    assert {"type": "null"} in b_prop["anyOf"]

    # OpenAI strict mode requires all properties to be explicitly listed in required array
    assert set(result["parameters"]["required"]) == {"a", "b"}
