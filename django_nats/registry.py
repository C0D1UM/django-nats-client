from django.conf import settings


class FunctionRegistry:
    """Function registry for callback functions from NATS"""

    def __init__(self):
        self.registry = {}

    def register(self, subject: str = None, key: str = None, func=None):
        if subject is None and getattr(settings, 'NATS_SUBJECT') is None:
            raise ValueError('Require one of `subject` in register function or `NATS_SUBJECT` in settings')

        # @register()
        if subject is None and key is None and func is None:
            return self.register_function

        # register(...)
        if func is not None:
            return self.register_function(func, key, subject)

        # @register
        if subject is not None and key is None and func is None and callable(subject):
            return self.register_function(subject)

        # @register(...)
        def dec(func):
            return self.register(subject, key, func)

        return dec

    def register_function(self, func, key: str = None, subject: str = None):
        key = key or getattr(func, '_decorated_function', func).__name__
        subject = subject or settings.NATS_SUBJECT

        if (subject, key) in self.registry:
            raise ValueError(f'Duplicated NATS function named `{key}` in subject `{subject}`.')

        self.registry[(subject, key)] = func
        return func


default_registry = FunctionRegistry()
register = default_registry.register
