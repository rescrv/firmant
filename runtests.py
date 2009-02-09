#!/usr/bin/python
import unittest

from firmant.configuration import settings
from test.configuration import suite as configuration_tests
from test.db.atom import suite as db_atom_tests
from test.db.relations import suite as db_relations_tests


if __name__ == '__main__':
    settings.reconfigure('test_settings')
    suite = unittest.TestSuite()
    suite.addTests(configuration_tests)
    suite.addTests(db_atom_tests)
    suite.addTests(db_relations_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
