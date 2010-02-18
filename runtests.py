#!/usr/bin/python
import unittest
import doctest
import sys
from optparse import OptionParser

# Import this now to avoid it throwing errors.
import pytz

if __name__ == '__main__':
    suite = unittest.TestSuite()

    from firmant import du
    suite.addTest(doctest.DocTestSuite(du))
    from firmant import entries
    suite.addTest(doctest.DocTestSuite(entries))
    from firmant import feeds
    suite.addTest(doctest.DocTestSuite(feeds))
    from firmant import parser
    suite.addTest(doctest.DocTestSuite(parser))
    from firmant import tags
    suite.addTest(doctest.DocTestSuite(tags))
    from firmant import utils
    suite.addTest(doctest.DocTestSuite(utils))
    from firmant import writers
    suite.addTest(doctest.DocTestSuite(writers))

    results = unittest.TextTestRunner(verbosity=2).run(suite)

    if not results.wasSuccessful():
        sys.exit(1)
