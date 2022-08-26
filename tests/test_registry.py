from django import test

from django_nats.registry import FunctionRegistry


@test.override_settings(NATS_SUBJECT='subject')
class FunctionRegistryRegisterTest(test.TestCase):
    def setUp(self) -> None:
        self.registry = FunctionRegistry()

    def test_register_with_no_parenthesis(self):
        @self.registry.register
        def func():
            pass

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn(('subject', 'func'), self.registry.registry)
        self.assertEqual(self.registry.registry[('subject', 'func')], func)

    def test_register_with_no_argument(self):
        @self.registry.register()
        def func():
            pass

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn(('subject', 'func'), self.registry.registry)
        self.assertEqual(self.registry.registry[('subject', 'func')], func)

    def test_register_with_custom_subject(self):
        @self.registry.register('custom')
        def func():
            pass

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn(('custom', 'func'), self.registry.registry)
        self.assertEqual(self.registry.registry[('custom', 'func')], func)

    def test_register_with_custom_name(self):
        @self.registry.register(name='custom')
        def func():
            pass

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn(('subject', 'custom'), self.registry.registry)
        self.assertEqual(self.registry.registry[('subject', 'custom')], func)

    def test_register_with_custom_subject_and_name(self):
        @self.registry.register('custom_subject', 'custom_name')
        def func():
            pass

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn(('custom_subject', 'custom_name'), self.registry.registry)
        self.assertEqual(self.registry.registry[('custom_subject', 'custom_name')], func)

    def test_register_without_decorator(self):
        def func():
            pass

        self.registry.register(func)

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn(('subject', 'func'), self.registry.registry)
        self.assertEqual(self.registry.registry[('subject', 'func')], func)

    def test_register_without_decorator_with_kwargs(self):
        def func():
            pass

        self.registry.register(func=func)

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn(('subject', 'func'), self.registry.registry)
        self.assertEqual(self.registry.registry[('subject', 'func')], func)

    def test_register_without_decorator_all_params(self):
        def func():
            pass

        self.registry.register('custom_subject', 'custom_name', func)

        self.assertEqual(len(self.registry.registry.keys()), 1)
        self.assertIn(('custom_subject', 'custom_name'), self.registry.registry)
        self.assertEqual(self.registry.registry[('custom_subject', 'custom_name')], func)

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

    def test_duplicated_name_but_different_subject(self):
        @self.registry.register
        def func():
            pass

        @self.registry.register('new_subject', 'func')
        def another_func():
            pass

        self.assertEqual(len(self.registry.registry.keys()), 2)
        self.assertIn(('subject', 'func'), self.registry.registry)
        self.assertIn(('new_subject', 'func'), self.registry.registry)
        self.assertEqual(self.registry.registry[('subject', 'func')], func)
        self.assertEqual(self.registry.registry[('new_subject', 'func')], another_func)
