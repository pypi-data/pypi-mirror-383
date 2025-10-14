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

    def __init__(self, required_context=[]):
        self.required_context = required_context

    def __call__(self, f):
        def wrapped_f(payload, context, *args, **kwargs):
            for prop in self.required_context:
                if context.get(prop) is None:
                    raise ValueError(f"context missing: {prop}, in {f.__name__}")
            return f(payload, context, *args, **kwargs)

        return wrapped_f


class route:
    """A decorator that registers a function as a route handler.

    Use this decorator to automatically register functions as route handlers
    for different Slack interaction types. The decorator will register the
    function with the provided SlackApp instance.

    Args:
        app: SlackApp instance to register the route with
        route_type: Type of route (block_actions, view_submission, etc.)
        name: Optional name for the route, defaults to function name
        required_context: List of keys to validate in context
    """

    def __init__(self, app, route_type, name=None, required_context=[]):
        self.app = app
        self.route_type = route_type
        self.name = name
        self.required_context = required_context

    def __call__(self, f):
        def wrapped_f(payload, context, *args, **kwargs):
            for prop in self.required_context:
                if context.get(prop) is None:
                    raise ValueError(f"context missing: {prop}, in {f.__name__}")
            return f(payload, context, *args, **kwargs)

        route_name = self.name or f.__name__
        self.app.register_route(self.route_type, wrapped_f, route_name)
        return wrapped_f
