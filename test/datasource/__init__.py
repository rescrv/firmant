import unittest

from firmant.datasource import Storage


def create_testSave1(tosave, docstring, expt, check_func, *args, **kwargs):
    def testSave1(self):
        provider = self.provider

        expected = None
        returned = provider.save(tosave)
        self.assertEqual(expected, returned)

        if not hasattr(provider, check_func):
            self.fail()
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


suite = unittest.TestSuite()

from test.datasource.atom import suite as atom_tests
suite.addTests(atom_tests)
