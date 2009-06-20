import unittest

from firmant.utils import not_implemented


class TestNotImplemented(unittest.TestCase):
    
    def testRaises1(self):
        '''firmant.utils.not_implemented
        Test not_implemented raises an error when called with no arguments'''
        self.assertRaises(NotImplementedError, not_implemented)
    
    def testRaises2(self):
        '''firmant.utils.not_implemented
        Test not_implemented raises an error when called with arguments'''
        self.assertRaises(NotImplementedError, not_implemented, 1, 2, 3)


suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestNotImplemented))
