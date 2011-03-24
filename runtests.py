#!/usr/bin/python

import gettext
import logging
import unittest
import doctest
import sys
from optparse import OptionParser

from minimock import Mock
from pprint import pprint
from pysettings.modules import get_module


gettext.install('firmant')


def safe_displayhook(s):
    if s is not None:
        if isinstance(s, tuple):
            sys.stdout.write('%r\n' % (s,))
        else:
            sys.stdout.write('%r\n' % s)
sys.displayhook = safe_displayhook


def get_logger():
    logger = logging.getLogger('logger')
    logger.setLevel(logging.WARN)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


if __name__ == '__main__':
    suite = unittest.TestSuite()

    modules = ['firmant'
              ,'firmant.application'
              ,'firmant.chunks'
              ,'firmant.decorators'
              ,'firmant.du'
              ,'firmant.globs'
              ,'firmant.paginate'
              ,'firmant.parsers'
              ,'firmant.parsers.feeds'
              ,'firmant.parsers.posts'
              ,'firmant.parsers.static'
              ,'firmant.parsers.staticrst'
              ,'firmant.parsers.tags'
              ,'firmant.plugin'
              ,'firmant.routing'
              ,'firmant.routing.components'
              ,'firmant.settings'
              ,'firmant.urls'
              ,'firmant.utils'
              ,'firmant.utils.exceptions'
              ,'firmant.utils.paths'
              ,'firmant.utils.workarounds'
              ,'firmant.writers'
              ,'firmant.writers.atom'
              ,'firmant.writers.feeds'
              ,'firmant.writers.j2'
              ,'firmant.writers.posts'
              ,'firmant.writers.static'
              ,'firmant.writers.staticrst'
              ]

    if len(sys.argv[1:]) > 0:
        modules = sys.argv[1:]

    for module in modules:
        mod = get_module(module)
        args = {}
        extraglobs = {'Mock': Mock
                     ,'pprint': pprint
                     ,'get_logger': get_logger
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
