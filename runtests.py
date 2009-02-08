#!/usr/bin/python
import unittest

from firmant.configuration import settings
from test.settings import suite as settings_tests
from test.atom import suite as atom_tests
from test.relations import suite as relations_tests


if __name__ == '__main__':
    settings.reconfigure('test_settings')
    suite = unittest.TestSuite()
    suite.addTests(settings_tests)
    suite.addTests(atom_tests)
    suite.addTests(relations_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
