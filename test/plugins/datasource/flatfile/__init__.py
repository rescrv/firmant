import unittest


suite = unittest.TestSuite()

from test.plugins.datasource.flatfile.atom import suite as atom_tests
suite.addTests(atom_tests)

from test.plugins.datasource.flatfile.comments import suite as comments_tests
suite.addTests(comments_tests)
