import unittest

from firmant.plugins import SingleProviderPlugin
from firmant.plugins import MultiProviderPlugin
from firmant.plugins import load_plugin
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


class MultiProviderPluginTest(unittest.TestCase):

    class DummyMultiPlugin(MultiProviderPlugin):

        providers_setting = 'DUMMY_PROVIDER'

    def testValid(self):
        '''firmant.plugins.MultiProviderPlugin.__init__'''
        settings = {'DUMMY_PROVIDER': ['test.plugins.DummyPlugin',
                                       'test.plugins.DummyPlugin']}
        rc       = None
        inst     = self.DummyMultiPlugin(rc, settings)

        expected = True
        returned = isinstance(inst._plugins[0], DummyPlugin)
        self.assertEqual(expected, returned)

        expected = True
        returned = isinstance(inst._plugins[1], DummyPlugin)
        self.assertEqual(expected, returned)

    def testUnsetPath(self):
        '''firmant.plugins.MultiProviderPlugin.__init__'''
        settings = {}
        rc       = None

        raises   = ValueError
        function = lambda: self.DummyMultiPlugin(rc, settings)

        self.assertRaises(raises, function)


class LoadPluginTest(unittest.TestCase):

    def testInvalidImport(self):
        '''firmant.plugins.load_plugin'''

        raises   = ImportError
        function = lambda: load_plugin('test.noexist.Plugin')

        self.assertRaises(raises, function)

    def testValidModuleInvalidAttribute(self):
        '''firmant.plugins.load_plugin'''

        raises   = AttributeError
        function = lambda: load_plugin('test.plugins.NoExist')

        self.assertRaises(raises, function)

    def testValid(self):
        '''firmant.plugins.load_plugin'''

        expected = DummyPlugin
        returned = load_plugin('test.plugins.DummyPlugin')

        self.assertEqual(expected, returned)


suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(SingleProviderPluginTest))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MultiProviderPluginTest))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(LoadPluginTest))
