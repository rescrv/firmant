import unittest

from firmant.plugins import SingleProviderPlugin
from firmant.utils import not_implemented


class DummyPlugin(object):

    def __init__(self, rc, settings):
        pass

class SingleProviderPluginTest(unittest.TestCase):

    class DummySinglePlugin(SingleProviderPlugin):

        provider_setting = 'DUMMY_PROVIDER'

    def testValid(self):
        '''firmant.plugins.SingleProviderPlugin.__init__'''
        settings = {'DUMMY_PROVIDER': 'test.plugins.DummyPlugin'}
        rc       = None
        inst     = self.DummySinglePlugin(rc, settings)

        expected = True
        returned = isinstance(inst._provider, DummyPlugin)

        self.assertEqual(expected, returned)

    def testUnsetPath(self):
        '''firmant.plugins.SingleProviderPlugin.__init__'''
        settings = {}
        rc       = None

        raises   = ValueError
        function = lambda: self.DummySinglePlugin(rc, settings)

        self.assertRaises(raises, function)

    def testInvalidImport(self):
        '''firmant.plugins.SingleProviderPlugin.__init__'''
        settings = {'DUMMY_PROVIDER': 'test.noexist.Plugin'}
        rc       = None

        raises   = ImportError
        function = lambda: self.DummySinglePlugin(rc, settings)

        self.assertRaises(raises, function)

    def testValidModuleInvalidAttribute(self):
        '''firmant.plugins.SingleProviderPlugin.__init__'''
        settings = {'DUMMY_PROVIDER': 'test.plugins.NoExist'}
        rc       = None

        raises   = AttributeError
        function = lambda: self.DummySinglePlugin(rc, settings)

        self.assertRaises(raises, function)


suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(SingleProviderPluginTest))
