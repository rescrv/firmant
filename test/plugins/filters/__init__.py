import unittest


suite = unittest.TestSuite()

from test.plugins.filters.markdownfilter import suite as markdownfilter_tests
suite.addTests(markdownfilter_tests)
