import unittest
import firmant.settings


class TestSettings(unittest.TestCase):

    def testemptyinit(self):
        s = firmant.settings.Settings('test.data.settings.empty')

    def testinit(self):
        s = firmant.settings.Settings('test.data.settings.full')
        self.assertEqual(s['INT'], 42)
        self.assertEqual(s['STRING'], 'hello world')
        self.assertEqual(s['LIST_TEST'], [1, 2, 3, 4, 5])
        self.assertEqual(s['SINGLE_TUPLE_TEST'], (1, ))
        self.assertEqual(s['TUPLE_TEST'], (1, 2, 3, 4, 5))
        self.assertEqual(s['DICT_TEST'], {'hello': 'world', "g'bye": 'world'})
        self.assertEqual(s['SET_TEST'], set([1, 2, 3, 4, 5]))
        self.assertRaises(KeyError, s.__getitem__, 'nonexistent')

    def testfailure(self):
        self.assertRaises(ImportError, firmant.settings.Settings,
                'test.data.settings.nonexistent')


suite = unittest.TestLoader().loadTestsFromTestCase(TestSettings)
