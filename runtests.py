#!/usr/bin/python
import unittest
import doctest
import sys
from optparse import OptionParser

from pysettings.modules import get_module

# Import this now to avoid it throwing errors.
import pytz

if __name__ == '__main__':
    suite = unittest.TestSuite()

    modules = ['firmant.application',
               'firmant.du',
               'firmant.extensions',
               'firmant.i18n',
               'firmant.parsers',
               'firmant.parsers.feeds',
               'firmant.parsers.posts',
               'firmant.parsers.tags',
               'firmant.utils',
               #'firmant.writers',
               #'firmant.writers.j2'
              ]

    for module in modules:
        mod = get_module(module)
        args = {}
        for attr in ['module_relative', 'package', 'setUp', 'tearDown', 'globs',
                'optionflags', 'parser', 'encoding']:
            if hasattr(mod, '_' + attr):
                args[attr] = getattr(mod, '_' + attr)
        suite.addTest(doctest.DocTestSuite(mod, **args))

    results = unittest.TextTestRunner(verbosity=2).run(suite)

    if not results.wasSuccessful():
        sys.exit(1)
