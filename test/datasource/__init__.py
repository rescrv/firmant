import unittest

from firmant.datasource import Storage


def create_testSave1(tosave, docstring, expt, check_func, *args, **kwargs):
    def testSave1(self):
        provider = self.provider

        expected = None
        returned = provider.save(tosave)
        self.assertEqual(expected, returned)

        if not hasattr(provider, check_func):
            self.fail() # pragma: no cover
        check = getattr(provider, check_func)

        expected = expt
        returned = check(*args, **kwargs)
        self.assertEqual(expected, returned)
    testSave1.__doc__ = docstring
    return testSave1


def create_testSave2(tosave, docstring):
    def testSave2(self):
        provider = self.provider

        raised   = Storage.UniqueViolationError
        function = lambda: provider.save(tosave)

        self.assertRaises(raised, function)
    testSave2.__doc__ = docstring
    return testSave2


def create_testDelete1(dne, docstring):
    def testDelete1(self):
        provider = self.provider

        raised   = Storage.DoesNotExistError
        function = lambda: provider.delete(dne)

        self.assertRaises(raised, function)
    testDelete1.__doc__ = docstring
    return testDelete1


def create_testDelete2(todelete, docstring, expt, check_func, *args, **kwargs):
    def testDelete2(self):
        provider = self.provider

        expected = None
        returned = provider.delete(todelete)
        self.assertEqual(expected, returned)

        if not hasattr(provider, check_func):
            self.fail() # pragma: no cover
        check = getattr(provider, check_func)

        expected = expt
        returned = check(*args, **kwargs)
        self.assertEqual(expected, returned)
    testDelete2.__doc__ = docstring
    return testDelete2


class TestStorage(unittest.TestCase):

    class NewStorage1(Storage):

        def _save(self, obj):
            raise ValueError('save failed')

        def _delete(self, obj):
            raise ValueError('delete failed')

    class NewStorage2(Storage):

        def _save(self, obj):
            raise Storage.StorageError('save failed')

        def _delete(self, obj):
            raise Storage.StorageError('delete failed')

    def testSave1(self):
        '''firmant.datasource.Storage.save'''

        raised   = Storage.StorageError
        function = lambda: TestStorage.NewStorage1().save(None)

        self.assertRaises(raised, function)

    def testSave2(self):
        '''firmant.datasource.Storage.save'''

        raised   = Storage.StorageError
        function = lambda: TestStorage.NewStorage2().save(None)

        self.assertRaises(raised, function)

    def testDelete1(self):
        '''firmant.datasource.Storage.delete'''

        raised   = Storage.StorageError
        function = lambda: TestStorage.NewStorage1().delete(None)

        self.assertRaises(raised, function)

    def testDelete2(self):
        '''firmant.datasource.Storage.delete'''

        raised   = Storage.StorageError
        function = lambda: TestStorage.NewStorage2().delete(None)

        self.assertRaises(raised, function)


from test import add_test
suite = unittest.TestSuite()
add_test(suite, TestStorage)

from test.datasource.atom import suite as atom_tests
suite.addTests(atom_tests)

from test.datasource.comments import suite as comment_tests
suite.addTests(comment_tests)
