import unittest

from firmant.configuration import settings
from firmant.plugins.datasource.flatfile.atom import FlatfileAtomProvider
from test.datasource.atom import e1, \
                                 e2, \
                                 e3, \
                                 e4
from test.datasource.atom import TestEntry as BaseTestEntry
from test.datasource.atom import TestAuthor as BaseTestAuthor


class TestAuthor(BaseTestAuthor):

    def setUp(self):
        self.provider = FlatfileAtomProvider

    def configuration(self, name):
        return settings


class TestEntry(BaseTestEntry):

    def setUp(self):
        provider = FlatfileAtomProvider(settings)
        self.Entry = provider.entry
        self.e1 = e1
        self.e2 = e2
        self.e3 = e3
        self.e4 = e4

    def tearDown(self):
        pass

    def loadData(self):
        pass


suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAuthor))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEntry))
