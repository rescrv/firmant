import unittest


def add_test(suite, testclass):
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(testclass))


suite = unittest.TestSuite()

from test.datasource import suite as datasource_tests
suite.addTests(datasource_tests)

from test.filters import suite as filters_tests
suite.addTests(filters_tests)

from test.plugins import suite as plugins_tests
suite.addTests(plugins_tests)

from test.utils import suite as utils_tests
suite.addTests(utils_tests)

from test.views import suite as views_tests
suite.addTests(views_tests)
