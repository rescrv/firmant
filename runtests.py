#!/usr/bin/python
import unittest
import sys
from optparse import OptionParser

# Import this now to avoid it throwing errors.
import pytz

from firmant.utils import get_module

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-m', '--module',
            dest='module', type='string', default='test',
            help='the module from which to import the test suite.')
    (options, args) = parser.parse_args()
    mod = get_module(options.module)

    if not hasattr(mod, 'suite'):
        sys.stderr.write("Module doesn't contain attribute 'suite'")
        sys.exit(1)

    results = unittest.TextTestRunner(verbosity=2).run(mod.suite)

    if not results.wasSuccessful():
        sys.exit(1)
