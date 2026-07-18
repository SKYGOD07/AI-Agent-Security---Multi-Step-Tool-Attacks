import sys
import unittest.mock

# The tests will naturally crash on import because aicomp_sdk.core.env is missing from this
# codebase entirely. To solve this globally for the test suite without polluting sys.modules for real code,
# we just use a small mock here.

# We create the missing package dynamically
import types

core_env_mock = types.ModuleType('aicomp_sdk.core.env')
sys.modules['aicomp_sdk.core.env'] = core_env_mock

api_mock = types.ModuleType('aicomp_sdk.core.env.api')
api_mock.AttackEnvProtocol = object
api_mock.EnvSelection = object
api_mock.DiagnosticsEnv = object
api_mock.EnvInteractionResult = object
api_mock.EnvRunDiagnostics = object
api_mock.coerce_env_selection = lambda x: x
api_mock.DEFAULT_MAX_TOOL_HOPS = 10
sys.modules['aicomp_sdk.core.env.api'] = api_mock

sandbox_mock = types.ModuleType('aicomp_sdk.core.env.sandbox')
sandbox_mock.SandboxEnv = object
sys.modules['aicomp_sdk.core.env.sandbox'] = sandbox_mock

gym_mock = types.ModuleType('aicomp_sdk.core.env.gym')
sys.modules['aicomp_sdk.core.env.gym'] = gym_mock
