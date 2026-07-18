import sys
import os
import unittest.mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../our_work/src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../our_work')))

# Mock the environment modules before importing search engine
sys.modules['aicomp_sdk.core.env'] = unittest.mock.MagicMock()
sys.modules['aicomp_sdk.core.env.api'] = unittest.mock.MagicMock()
sys.modules['aicomp_sdk.core.env.api'].DEFAULT_MAX_TOOL_HOPS = 8
sys.modules['aicomp_sdk.core.env.api'].AttackEnvProtocol = unittest.mock.MagicMock
sys.modules['aicomp_sdk.core.env.sandbox'] = unittest.mock.MagicMock()
sys.modules['aicomp_sdk.core.env.sandbox'].SandboxEnv = unittest.mock.MagicMock
sys.modules['aicomp_sdk.core.env.gym'] = unittest.mock.MagicMock()

import test_search
if hasattr(test_search, 'run_tests'):
    test_search.run_tests()
