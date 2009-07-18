import unittest


def add_test(suite, testclass):
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(testclass))
