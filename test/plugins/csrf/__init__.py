import unittest


from test import add_test
suite = unittest.TestSuite()

from test.plugins.csrf.flatfile import suite as flatfile_suite
suite.addTests(flatfile_suite)
