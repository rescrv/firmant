#!/usr/bin/python
import unittest
# Import this now to avoid it throwing errors.
import pytz

from firmant.configuration import settings
from test.configuration import suite as configuration_tests
from test.plugins.datasource.postgresql.atom import suite as db_atom_tests
from test.plugins.datasource.postgresql.relations import suite as db_relations_tests
from test.plugins.datasource.flatfile.atom import suite as flatfile_atom_tests
from test.resolvers import suite as resolvers_tests


if __name__ == '__main__':
    settings.reconfigure('test_settings')
    suite = unittest.TestSuite()
    suite.addTests(configuration_tests)
    suite.addTests(db_atom_tests)
    suite.addTests(db_relations_tests)
    suite.addTests(flatfile_atom_tests)
    suite.addTests(resolvers_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
