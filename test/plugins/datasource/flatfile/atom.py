import unittest

from firmant.configuration import settings
from firmant.plugins.datasource.flatfile.atom import FlatfileAtomProvider
from test.datasource.atom import TestEntry as BaseTestEntry
from test.datasource.atom import TestAuthor as BaseTestAuthor
from test.datasource.atom import TestCategory as BaseTestCategory
from test.datasource.atom import TestFeed as BaseTestFeed


class TestAuthor(BaseTestAuthor):

    def setUp(self):
        self.provider = FlatfileAtomProvider

    def configuration(self, name):
        return settings


class TestCategory(BaseTestCategory):

    def setUp(self):
        self.provider = FlatfileAtomProvider

    def configuration(self, name):
        return settings


class TestEntry(BaseTestEntry):

    def setUp(self):
        self.provider = FlatfileAtomProvider

    def configuration(self, name):
        return settings


class TestFeed(BaseTestFeed):

    def setUp(self):
        self.provider = FlatfileAtomProvider

    def configuration(self, name):
        return settings



suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAuthor))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCategory))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEntry))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFeed))
