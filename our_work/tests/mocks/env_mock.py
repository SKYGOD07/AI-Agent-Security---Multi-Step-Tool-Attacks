import sys
import types
from contextlib import contextmanager

@contextmanager
def patch_env_modules():
    """Context manager to patch missing env modules."""
    original_modules = {}

    modules_to_mock = [
        ('aicomp_sdk.core.env.api', {
            'AttackEnvProtocol': type('AttackEnvProtocol', (), {}),
            'DiagnosticsEnv': type('DiagnosticsEnv', (), {}),
            'EnvInteractionResult': type('EnvInteractionResult', (), {}),
            'EnvRunDiagnostics': type('EnvRunDiagnostics', (), {}),
            'EnvSelection': type('EnvSelection', (), {}),
            'coerce_env_selection': lambda *args, **kwargs: None,
            'DEFAULT_MAX_TOOL_HOPS': 10,
            'MAX_USER_MESSAGE_CHARS': 1000
        }),
        ('aicomp_sdk.core.env.sandbox', {
            'SandboxEnv': type('SandboxEnv', (), {})
        }),
        ('aicomp_sdk.core.env', {})
    ]

    for name, attrs in modules_to_mock:
        if name in sys.modules:
            original_modules[name] = sys.modules[name]

        module = types.ModuleType(name)
        if attrs:
            for k, v in attrs.items():
                setattr(module, k, v)
        sys.modules[name] = module

    # Keep track of any other aicomp_sdk modules loaded during this context
    # so we can unload them and not pollute sys.modules
    pre_existing_sdk_modules = {k for k in sys.modules.keys() if k.startswith('aicomp_sdk')}

    try:
        yield
    finally:
        # Unload aicomp_sdk modules loaded during the context to prevent pollution
        current_sdk_modules = {k for k in sys.modules.keys() if k.startswith('aicomp_sdk')}
        for name in current_sdk_modules - pre_existing_sdk_modules:
            del sys.modules[name]

        for name in ['aicomp_sdk.core.env.api', 'aicomp_sdk.core.env.sandbox', 'aicomp_sdk.core.env']:
            if name in sys.modules and name not in original_modules:
                del sys.modules[name]

        for name, module in original_modules.items():
            sys.modules[name] = module
