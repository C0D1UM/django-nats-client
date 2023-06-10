from django.conf import settings


class FunctionRegistry:
    """Function registry for callback functions from NATS"""

    def __init__(self):
        self.registry = {}

    def register(self, name=None, func=None, **kwargs):
        # register(...)
        if func is not None:
            return self.register_function(func, name, **kwargs)

        # @register
        if name is not None and func is None and callable(name):
            return self.register_function(name, **kwargs)

        # @register(...)
        def dec(func):
            return self.register(name, func, **kwargs)

        return dec

    def register_function(self, func, name: str = None, **kwargs):
        subject = kwargs.get('subject', getattr(settings, 'NATS_LISTENING_SUBJECT', 'default'))
        name = name or getattr(func, '_decorated_function', func).__name__
        js = kwargs.get('js', False)
        key = f'{subject}.js.{name}' if js else f'{subject}.{name}'

        if key in self.registry:
            raise ValueError(f'Duplicated NATS function key `{key}`.')

        self.registry[key] = {
            'func': func,
            'name': name,
            'subject': subject,
            'js': js,
        }
        return func


default_registry = FunctionRegistry()
register = default_registry.register
