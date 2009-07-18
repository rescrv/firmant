import unittest


suite = unittest.TestSuite()

from test.plugins.datasource.flatfile import suite as flatfile_tests
suite.addTests(flatfile_tests)
