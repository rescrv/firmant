import unittest

from firmant.plugins.filters.restructuredtext import RestructuredTextFilter


class TestRestructuredTextFilter(unittest.TestCase):

    def testProvides1(self):
        '''firmant.plugins.filters.restructuredtext.RestructuredTextFilter.provides
        Tests RESTRUCTUREDTEXT_XHTML_ENABLED = True.'''

        settings = {'RESTRUCTUREDTEXT_XHTML_ENABLED': True}
        filter   = RestructuredTextFilter(None, settings)

        expected = True
        returned = filter.provides('XHTML')

        self.assertEqual(expected, returned)

    def testProvides2(self):
        '''firmant.plugins.filters.restructuredtext.RestructuredTextFilter.provides
        Tests RESTRUCTUREDTEXT_XHTML_ENABLED = False.'''

        settings = {'RESTRUCTUREDTEXT_XHTML_ENABLED': False}
        filter   = RestructuredTextFilter(None, settings)

        expected = False
        returned = filter.provides('XHTML')

        self.assertEqual(expected, returned)

    def testFilter1(self):
        '''firmant.plugins.filters.restructuredtext.RestructuredTextFilter.filter'''

        filter   = RestructuredTextFilter(None, {})

        expected = '<p><em>hello world</em></p>\n'
        returned = filter.filter('XHMTL', '*hello world*')

        self.assertEqual(expected, returned)


from test import add_test
suite = unittest.TestSuite()
add_test(suite, TestRestructuredTextFilter)
