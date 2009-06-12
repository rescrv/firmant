import unittest

from firmant.configuration import settings
from firmant.plugins.datasource.flatfile.atom import FlatfileAtomProvider
from test.datasource.atom import generate_e1, \
                              generate_e2, \
                              generate_e3, \
                              generate_e4
from test.datasource.atom import TestEntry as BaseTestEntry


class TestEntry(BaseTestEntry):

    def setUp(self):
        provider = FlatfileAtomProvider(settings)
        self.Entry = provider.entry
        self.e1 = generate_e1(provider.entry)
        self.e2 = generate_e2(provider.entry)
        self.e3 = generate_e3(provider.entry)
        self.e4 = generate_e4(provider.entry)

    def tearDown(self):
        pass

    def loadData(self):
        pass


suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEntry))
