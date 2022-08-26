from django.conf import settings


class FunctionRegistry:
    """Function registry for callback functions from NATS"""

    def __init__(self):
        self.registry = {}

    def register(self, subject=None, name=None, func=None):
        # @register()
        if subject is None and name is None and func is None:
            return self.register_function

        # register(...)
        if func is not None:
            return self.register_function(func, name, subject)

        # @register
        if subject is not None and name is None and func is None and callable(subject):
            return self.register_function(subject)

        # @register(...)
        def dec(func):
            return self.register(subject, name, func)

        return dec

    def register_function(self, func, name: str = None, subject: str = None):
        name = name or getattr(func, '_decorated_function', func).__name__
        subject = subject or getattr(settings, 'NATS_DEFAULT_SUBJECT', 'default')

        if (subject, name) in self.registry:
            raise ValueError(f'Duplicated NATS function named `{name}` in subject `{subject}`.')

        self.registry[(subject, name)] = func
        return func

    @property
    def subjects(self):
        return [x[0] for x in self.registry]


default_registry = FunctionRegistry()
register = default_registry.register
