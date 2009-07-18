import unittest


suite = unittest.TestSuite()

from test.datasource.atom import suite as atom_tests
suite.addTests(atom_tests)
