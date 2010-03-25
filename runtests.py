#!/usr/bin/python
import unittest
import doctest
import sys
from optparse import OptionParser

from minimock import Mock
from pprint import pprint
from pysettings.modules import get_module

if __name__ == '__main__':
    suite = unittest.TestSuite()

    modules = ['firmant.application',
               'firmant.du',
               'firmant.i18n',
               'firmant.paginate',
               'firmant.parsers',
               'firmant.parsers.feeds',
               'firmant.parsers.posts',
               'firmant.parsers.tags',
               'firmant.routing',
               'firmant.routing.components',
               'firmant.utils',
               'firmant.utils.exceptions',
               'firmant.utils.paths',
               'firmant.writers',
               'firmant.writers.posts',
               'firmant.writers.j2'
              ]

    for module in modules:
        mod = get_module(module)
        args = {}
        extraglobs = {'Mock': Mock
                     ,'pprint': pprint
                     }
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
        extraglobs.update(args.get('extraglobs', dict()))
        args['extraglobs'] = extraglobs
        suite.addTest(doctest.DocTestSuite(mod, **args))

    results = unittest.TextTestRunner(verbosity=2).run(suite)

    if not results.wasSuccessful():
        sys.exit(1)
