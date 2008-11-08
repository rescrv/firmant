#!/usr/bin/python
import unittest

import test.settings

if __name__ == '__main__':
    suite =     unittest.TestLoader().loadTestsFromTestCase(test.settings.TestSettings)
    unittest.TextTestRunner(verbosity=2).run(suite)
