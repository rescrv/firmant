#!/usr/bin/python
import unittest
from firmant.utils import get_module
# Import this now to avoid it throwing errors.
import pytz

from test import suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
