class block_set:
    """A decorator that validates that required context keys are present.

    Use this decorator to wrap a function that renders a block set for Slack.
    This will check that the context provided to the renderer contains all the
    required context variables.

    Args:
        required_context (list): List of keys to look up in context.
    """

    def __init__(self, required_context=[]):
        self.required_context = required_context

    def __call__(self, f):
        def wrapped_f(context):
            for prop in self.required_context:
                if context.get(prop) is None:
                    raise ValueError(f"context missing: {prop}, in {f.__name__}")
            return f(context)

        return wrapped_f


class processor:
    """
    Decorator. Checks for required context for a processor.
    """

    def __init__(self, required_context=[], *args, **kwargs):
        self.required_context = required_context

    def __call__(self, f):
        def wrapped_f(payload, context, *args, **kwargs):
            for prop in self.required_context:
                if context.get(prop) is None:
                    raise ValueError(f"context missing: {prop}, in {f.__name__}")
            return f(payload, context, *args, **kwargs)

        return wrapped_f
