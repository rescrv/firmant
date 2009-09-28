import unittest


suite = unittest.TestSuite()

from test.plugins.views.generic import suite as generic_suite
suite.addTests(generic_suite)
