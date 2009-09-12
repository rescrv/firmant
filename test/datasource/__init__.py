import unittest


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


suite = unittest.TestSuite()

from test.datasource.atom import suite as atom_tests
suite.addTests(atom_tests)
