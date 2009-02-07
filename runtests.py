#!/usr/bin/python
import unittest

from test.settings import suite as settings_tests


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests(settings_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
