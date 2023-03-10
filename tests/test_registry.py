from django import test

from nats_client.registry import FunctionRegistry


@test.override_settings(NATS_LISTENING_SUBJECT='subject')
class FunctionRegistryRegisterTest(test.TestCase):

    def setUp(self) -> None:
        self.registry = FunctionRegistry()

    def test_register_with_no_parenthesis(self):

        @self.registry.register
        def func():
            pass

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn('func', self.registry.registry)
        self.assertEqual(self.registry.registry['func'], func)

    def test_register_with_no_argument(self):

        @self.registry.register()
        def func():
            pass

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn('func', self.registry.registry)
        self.assertEqual(self.registry.registry['func'], func)

    def test_register_with_custom_name(self):

        @self.registry.register('custom')
        def func():
            pass

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn('custom', self.registry.registry)
        self.assertEqual(self.registry.registry['custom'], func)

    def test_register_with_custom_kwarg_name(self):

        @self.registry.register(name='custom')
        def func():
            pass

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn('custom', self.registry.registry)
        self.assertEqual(self.registry.registry['custom'], func)

    def test_register_without_decorator(self):

        def func():
            pass

        self.registry.register(func)

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn('func', self.registry.registry)
        self.assertEqual(self.registry.registry['func'], func)

    def test_register_without_decorator_with_kwargs(self):

        def func():
            pass

        self.registry.register(func=func)

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn('func', self.registry.registry)
        self.assertEqual(self.registry.registry['func'], func)

    def test_register_without_decorator_all_params(self):

        def func():
            pass

        self.registry.register('custom_name', func)

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn('custom_name', self.registry.registry)
        self.assertEqual(self.registry.registry['custom_name'], func)

    def test_duplicated_function(self):

        def func():
            pass

        self.registry.register(func)

        self.assertRaises(ValueError, self.registry.register, func)
        self.assertEqual(len(self.registry.registry.keys()), 1)

    def test_duplicated_name(self):

        @self.registry.register
        def func():
            pass

        def another_func():
            pass

        self.assertRaises(ValueError, self.registry.register, name='func', func=another_func)
        self.assertEqual(len(self.registry.registry.keys()), 1)

    def test_async_function(self):

        @self.registry.register
        async def func():
            pass

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn('func', self.registry.registry)
        self.assertEqual(self.registry.registry['func'], func)

    def test_async_function_with_parenthesis(self):

        @self.registry.register()
        async def func():
            pass

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn('func', self.registry.registry)
        self.assertEqual(self.registry.registry['func'], func)
