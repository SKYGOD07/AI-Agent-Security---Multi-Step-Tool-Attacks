import sys
import types
from unittest.mock import MagicMock
import pytest

@pytest.fixture(scope="session", autouse=True)
def patch_env():
    core = sys.modules.get('aicomp_sdk.core')
    if not core:
        core = types.ModuleType('aicomp_sdk.core')
        sys.modules['aicomp_sdk.core'] = core

    env = types.ModuleType('aicomp_sdk.core.env')
    api = types.ModuleType('aicomp_sdk.core.env.api')
    api.AttackEnvProtocol = MagicMock
    api.DEFAULT_MAX_TOOL_HOPS = 8
    env.api = api

    sandbox = types.ModuleType('aicomp_sdk.core.env.sandbox')
    sandbox.SandboxEnv = MagicMock
    env.sandbox = sandbox

    gym = types.ModuleType('aicomp_sdk.core.env.gym')
    env.gym = gym

    sys.modules['aicomp_sdk.core.env'] = env
    sys.modules['aicomp_sdk.core.env.api'] = api
    sys.modules['aicomp_sdk.core.env.sandbox'] = sandbox
    sys.modules['aicomp_sdk.core.env.gym'] = gym
