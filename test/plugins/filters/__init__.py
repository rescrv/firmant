import unittest


suite = unittest.TestSuite()

from test.plugins.filters.markdownfilter import suite as markdownfilter_tests
suite.addTests(markdownfilter_tests)

from test.plugins.filters.restructuredtext import suite as restructuredtext_tests
suite.addTests(restructuredtext_tests)
