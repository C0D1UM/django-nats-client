from django import test

from nats_client.registry import FunctionRegistry


class FunctionRegistryRegisterTest(test.TestCase):

    def setUp(self) -> None:
        self.registry = FunctionRegistry()

    def test_register_with_no_parenthesis(self):
        @self.registry.register
        def func():
            pass

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn('default.func', self.registry.registry)
        self.assertEqual(self.registry.registry['default.func'], {
            'func': func,
            'namespace': 'default',
            'name': 'func',
            'js': False,
        })

    def test_register_with_no_argument(self):
        @self.registry.register()
        def func():
            pass

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn('default.func', self.registry.registry)
        self.assertEqual(self.registry.registry['default.func'], {
            'func': func,
            'namespace': 'default',
            'name': 'func',
            'js': False,
        })

    def test_register_with_custom_name(self):
        @self.registry.register('custom')
        def func():
            pass

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn('default.custom', self.registry.registry)
        self.assertEqual(self.registry.registry['default.custom'], {
            'func': func,
            'namespace': 'default',
            'name': 'custom',
            'js': False,
        })

    def test_register_with_custom_kwarg_name(self):
        @self.registry.register(name='custom')
        def func():
            pass

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn('default.custom', self.registry.registry)
        self.assertEqual(self.registry.registry['default.custom'], {
            'func': func,
            'namespace': 'default',
            'name': 'custom',
            'js': False,
        })

    def test_register_without_decorator(self):
        def func():
            pass

        self.registry.register(func)

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn('default.func', self.registry.registry)
        self.assertEqual(self.registry.registry['default.func'], {
            'func': func,
            'namespace': 'default',
            'name': 'func',
            'js': False,
        })

    def test_register_without_decorator_with_kwargs(self):
        def func():
            pass

        self.registry.register(func=func)

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn('default.func', self.registry.registry)
        self.assertEqual(self.registry.registry['default.func'], {
            'func': func,
            'namespace': 'default',
            'name': 'func',
            'js': False,
        })

    def test_register_without_decorator_all_params(self):
        def func():
            pass

        self.registry.register('custom', func)

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn('default.custom', self.registry.registry)
        self.assertEqual(self.registry.registry['default.custom'], {
            'func': func,
            'namespace': 'default',
            'name': 'custom',
            'js': False,
        })

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
        self.assertIn('default.func', self.registry.registry)
        self.assertEqual(self.registry.registry['default.func'], {
            'func': func,
            'namespace': 'default',
            'name': 'func',
            'js': False,
        })

    def test_async_function_with_parenthesis(self):
        @self.registry.register()
        async def func():
            pass

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn('default.func', self.registry.registry)
        self.assertEqual(self.registry.registry['default.func'], {
            'func': func,
            'namespace': 'default',
            'name': 'func',
            'js': False,
        })

    def test_js_function(self):
        @self.registry.register(js=True)
        def func():
            pass

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn('default.js.func', self.registry.registry)
        self.assertEqual(self.registry.registry['default.js.func'], {
            'func': func,
            'namespace': 'default',
            'name': 'func',
            'js': True,
        })

    def test_custom_namespace(self):
        @self.registry.register(namespace='custom')
        def func():
            pass

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn('custom.func', self.registry.registry)
        self.assertEqual(self.registry.registry['custom.func'], {
            'func': func,
            'namespace': 'custom',
            'name': 'func',
            'js': False,
        })
