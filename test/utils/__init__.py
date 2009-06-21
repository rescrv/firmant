import unittest

from firmant.utils import not_implemented
from firmant.utils import get_module
from firmant.utils import mod_to_dict
from test.data.settings import full


class TestNotImplemented(unittest.TestCase):
    
    def testRaises1(self):
        '''firmant.utils.not_implemented
        Test not_implemented raises an error when called with no arguments'''
        self.assertRaises(NotImplementedError, not_implemented)
    
    def testRaises2(self):
        '''firmant.utils.not_implemented
        Test not_implemented raises an error when called with arguments'''
        self.assertRaises(NotImplementedError, not_implemented, 1, 2, 3)


class TestGetModule(unittest.TestCase):

    def testModuleExists(self):
        '''firmant.utils.get_module
        Tests the importing of a valid module'''
        self.assertEqual(full, get_module('test.data.settings.full'))

    def testModuleDoesNotExist(self):
        '''firmant.utils.get_module
        Tests the importing of a non-existent module'''
        self.assertRaises(ImportError, get_module, 'test.data.settings.noexist')


class TestModToDict(unittest.TestCase):

    def testEmpty(self):
        '''firmant.utils.mod_to_dict
        Load an empty module'''
        expected = {}
        returned = mod_to_dict(get_module('test.data.settings.empty'))
        self.assertEqual(expected, returned)

    def testPopulated(self):
        '''firmant.utils.mod_to_dict
        Load a populated module'''
        expected = {'INT': 42,
                    'STRING': 'hello world',
                    'LIST_TEST': [1, 2, 3, 4, 5],
                    'SINGLE_TUPLE_TEST': (1, ),
                    'TUPLE_TEST': (1, 2, 3, 4, 5),
                    'DICT_TEST': {'hello': 'world',
                                  "g'bye": 'world'},
                    'SET_TEST': set([1, 2, 3, 4, 5])}
        returned = mod_to_dict(get_module('test.data.settings.full'))
        self.assertEqual(expected, returned)


suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestNotImplemented))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestGetModule))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestModToDict))
