import unittest
from firmant.configuration import settings


class TestSettings(unittest.TestCase):

    def setUp(self):
        # We do not want other tests to affect settings in here.
        settings.reset()

    def tearDown(self):
        # We do not want settings in here to affect any other tests.
        settings.reset()

    def testEmptyInit(self):
        settings.configure('test.data.settings.empty')

    def testInit(self):
        settings.configure('test.data.settings.full')
        self.assertEqual(settings['INT'], 42)
        self.assertEqual(settings['STRING'], 'hello world')
        self.assertEqual(settings['LIST_TEST'], [1, 2, 3, 4, 5])
        self.assertEqual(settings['SINGLE_TUPLE_TEST'], (1, ))
        self.assertEqual(settings['TUPLE_TEST'], (1, 2, 3, 4, 5))
        self.assertEqual(settings['DICT_TEST'], {'hello': 'world',
                                                 "g'bye": 'world'})
        self.assertEqual(settings['SET_TEST'], set([1, 2, 3, 4, 5]))
        self.assertRaises(KeyError, settings.__getitem__, 'nonexistent')

    def testAlreadyConfigured(self):
        settings.configure('test.data.settings.full')
        # This fails because we've already configured the module.  We should be
        # using reconfigure, not configure.
        self.assertRaises(ImportError, settings.configure,
                          'test.data.settings.empty')

    def testConfigureInvalid(self):
        # We wish to test for unimportable modules
        self.assertRaises(ImportError, settings.configure,
            'test.data.settings.nonexistent')

    def testReconfigure(self):
        # We wish to make 'firmant.settings' change to be updated globally.
        # Reconfigure should only change the properties of the settings, but
        # the object should be the same.  This is vital for allowing statements
        # like 'from firmant import settings' to work properly if a reconfigure
        # is performed after the import.
        settings.configure('test.data.settings.empty')
        self.assertRaises(KeyError, settings.__getitem__,
                          'UNIQUE_TO_TEST_RECONFIGURE')
        settings.reconfigure('test.data.settings.unique_to_test_reconfigure')
        self.assertEqual(settings['UNIQUE_TO_TEST_RECONFIGURE'],
                         'this is the unique key, value pair')


suite = unittest.TestLoader().loadTestsFromTestCase(TestSettings)
