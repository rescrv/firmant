import unittest

from firmant.utils import not_implemented
from firmant.utils import get_module
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


suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestNotImplemented))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestGetModule))
