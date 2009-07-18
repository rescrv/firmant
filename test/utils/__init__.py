import unittest
import datetime
import pytz

from firmant.utils import not_implemented
from firmant.utils import get_module
from firmant.utils import mod_to_dict
from firmant.utils import RFC3339
from firmant.utils import uniq
from firmant.utils import uniq_presorted
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


class TestRFC3339(unittest.TestCase):

    def testTimezone(self):
        '''firmant.utils.RFC3339'''
        pacific = pytz.timezone('US/Pacific')
        dt      = pacific.localize(datetime.datetime(1996, 12, 19, 16, 39, 57))

        expected = '1996-12-19T16:39:57-08:00'
        returned = RFC3339(dt)
        self.assertEqual(expected, returned)

    def testNoTimezone(self):
        '''firmant.utils.RFC3339'''
        expected = '1996-12-19T16:39:57Z'
        returned = RFC3339(datetime.datetime(1996, 12, 19, 16, 39, 57))
        self.assertEqual(expected, returned)


class TestUniq(unittest.TestCase):

    def testUnsorted(self):
        '''firmant.utils.uniq'''

        expected = [1, 2, 3]
        returned = uniq([3, 2, 2, 2, 3, 1, 1, 3, 2])

        self.assertEqual(expected, returned)

    def testEmpty(self):
        '''firmant.utils.uniq'''

        expected = []
        returned = uniq([])

        self.assertEqual(expected, returned)

    def testPresorted(self):
        '''firmant.utils.uniq_presorted'''

        expected = [1, 2, 3]
        returned = uniq_presorted([1, 1, 2, 2, 2, 2, 3, 3, 3])

        self.assertEqual(expected, returned)


from test import add_test
suite = unittest.TestSuite()
add_test(suite, TestNotImplemented)
add_test(suite, TestGetModule)
add_test(suite, TestModToDict)
add_test(suite, TestRFC3339)
add_test(suite, TestUniq)
