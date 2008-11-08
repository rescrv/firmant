#!/usr/bin/python
import unittest

from test.settings import TestSettings

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSettings)
    unittest.TextTestRunner(verbosity=2).run(suite)
