#!/usr/bin/python
import unittest
from firmant.utils import get_module
# Import this now to avoid it throwing errors.
import pytz

from firmant.configuration import settings
from test.configuration import suite as configuration_tests
from test.datasource.atom import suite as atom_tests
from test.plugins.datasource.flatfile.atom import suite as flatfile_atom_tests
from test.resolvers import suite as resolvers_tests

if __name__ == '__main__':
    settings.reconfigure('test_settings')
    for plugin in settings['PLUGINS']:
        try:
            mod = get_module(plugin)
        except ImportError:
            raise
    suite = unittest.TestSuite()
    suite.addTests(configuration_tests)
    suite.addTests(atom_tests)
    #suite.addTests(flatfile_atom_tests)
    suite.addTests(resolvers_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
