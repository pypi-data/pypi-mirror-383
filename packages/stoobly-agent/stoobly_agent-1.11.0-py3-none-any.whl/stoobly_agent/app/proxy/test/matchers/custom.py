from stoobly_agent.app.proxy.test.context_abc import TestContextABC as TestContext

def matches(context: TestContext):
    lifecycle_hooks = context.lifecycle_hooks

    if not context.lifecycle_hooks_path:
        return False, 'Missing lifecycle hooks path' 

    if not 'handle_test' in lifecycle_hooks:
        return False, f"Expected function 'handle_test' to be defined in {context.lifecycle_hooks_path}"

    try:
        status, log = lifecycle_hooks['handle_test'](context)
    except Exception as e:
        return False, f"Exception: {e}"

    if not type(status) is bool or not type(log) is str:
        return False, f"Expected function 'test' to return [bool, str], got [{type(status)}, {type(log)}]"

    return status, log