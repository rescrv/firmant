#!/usr/bin/python
import unittest
from firmant.utils import get_module
# Import this now to avoid it throwing errors.
import pytz

from test.datasource.atom import suite as atom_tests
from test.plugins.datasource.flatfile.atom import suite as flatfile_atom_tests

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests(atom_tests)
    suite.addTests(flatfile_atom_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
