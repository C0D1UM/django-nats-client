class FunctionRegistry:
    """Function registry for callback functions from NATS"""

    def __init__(self):
        self.registry = {}

    def register(self, name=None, func=None):
        # @register()
        if name is None and func is None:
            return self.register_function

        # register(...)
        if func is not None:
            return self.register_function(func, name)

        # @register
        if name is not None and func is None and callable(name):
            return self.register_function(name)

        # @register(...)
        def dec(func):
            return self.register(name, func)

        return dec

    def register_function(self, func, name: str = None):
        name = name or getattr(func, '_decorated_function', func).__name__

        if name in self.registry:
            raise ValueError(f'Duplicated NATS function named `{name}`.')

        self.registry[name] = func
        return func


default_registry = FunctionRegistry()
register = default_registry.register
