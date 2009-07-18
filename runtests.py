#!/usr/bin/python
import unittest
import sys

# Import this now to avoid it throwing errors.
import pytz

from test import suite

if __name__ == '__main__':
    results = unittest.TextTestRunner(verbosity=2).run(suite)

    if not results.wasSuccessful():
        sys.exit(1)
