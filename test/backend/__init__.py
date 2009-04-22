import unittest

from firmant.backend import get_atom_module
from firmant.backend import get_entry_class
from firmant.backend import get_feed_class

class TestBackendFactory(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testGetAtomModule(self):
        atom = get_atom_module()

    def testGetEntryClass(self):
        entry = get_entry_class()

    def testGetFeedClass(self):
        feed = get_feed_class()


suite = unittest.TestLoader().loadTestsFromTestCase(TestBackendFactory)
