import unittest


suite = unittest.TestSuite()

from test.plugins.datasource.flatfile.atom import suite as atom_tests
suite.addTests(atom_tests)
