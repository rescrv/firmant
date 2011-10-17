#!/usr/bin/python

import gettext
import importlib
import logging
import unittest
import doctest
import sys
from optparse import OptionParser


gettext.install('firmant')


def safe_displayhook(s):
    if s is not None:
        if isinstance(s, tuple):
            sys.stdout.write('%r\n' % (s,))
        else:
            sys.stdout.write('%r\n' % s)
sys.displayhook = safe_displayhook


if __name__ == '__main__':
    suite = unittest.TestSuite()

    modules = ['firmant.objects'
              ,'firmant.urls'
              ]

    if len(sys.argv[1:]) > 0:
        modules = sys.argv[1:]

    for module in modules:
        mod = importlib.import_module(module)
        args = {}
        for arg, attr in [('module_relative', '_module_relative')
                         ,('package', '_package')
                         ,('setUp', '_setup')
                         ,('tearDown', '_teardown')
                         ,('globs', '_globs')
                         ,('optionflags', '_optionflags')
                         ,('parser', '_parser')
                         ,('encoding', '_encoding')
                         ]:
            if hasattr(mod, attr):
                args[arg] = getattr(mod, attr)
        suite.addTest(doctest.DocTestSuite(mod, **args))

    results = unittest.TextTestRunner(verbosity=2).run(suite)

    if not results.wasSuccessful():
        sys.exit(1)
