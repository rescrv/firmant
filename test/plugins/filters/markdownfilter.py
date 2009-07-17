import unittest

from firmant.plugins.filters.markdownfilter import MarkdownFilter


class TestMarkdownFilter(unittest.TestCase):

    def testProvides1(self):
        '''firmant.plugins.filters.markdown.MarkdownFilter.provides
        Tests MARKDOWN_XHTML_ENABLED = True.'''

        settings = {'MARKDOWN_XHTML_ENABLED': True}
        filter   = MarkdownFilter(None, settings)

        expected = True
        returned = filter.provides('XHTML')

        self.assertEqual(expected, returned)

    def testProvides2(self):
        '''firmant.plugins.filters.markdown.MarkdownFilter.provides
        Tests MARKDOWN_XHTML_ENABLED = False.'''

        settings = {'MARKDOWN_XHTML_ENABLED': False}
        filter   = MarkdownFilter(None, settings)

        expected = False
        returned = filter.provides('XHTML')

        self.assertEqual(expected, returned)

    def testFilter1(self):
        '''firmant.plugins.filters.markdown.MarkdownFilter.filter
        Tests safemode is None'''

        settings = {'MARKDOWN_XHTML_SAFE_MODE': None}
        filter   = MarkdownFilter(None, settings)

        expected = '<p>Hello World\n</p>'
        returned = filter.filter('XHMTL', 'Hello World')

        self.assertEqual(expected, returned)

    def testFilter2(self):
        '''firmant.plugins.filters.markdown.MarkdownFilter.filter
        Tests safemode is not None'''

        settings = {'MARKDOWN_XHTML_SAFE_MODE': 'remove'}
        filter   = MarkdownFilter(None, settings)

        expected = '<p>Hello World\n</p>'
        returned = filter.filter('XHMTL', '<em>Hello World</em>')

        self.assertEqual(expected, returned)


suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMarkdownFilter))
