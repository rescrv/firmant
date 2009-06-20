import unittest

from firmant.plugins.datasource.flatfile.atom import FlatfileAtomProvider
from test.datasource.atom import TestEntry as BaseTestEntry
from test.datasource.atom import TestAuthor as BaseTestAuthor
from test.datasource.atom import TestCategory as BaseTestCategory
from test.datasource.atom import TestFeed as BaseTestFeed
from test.datasource.atom import DummyEntryPermalinkProvider
from test.datasource.atom import DummyFeedPermalinkProvider


settings = {
        'PLUGINS': ['firmant.plugins.datasource.flatfile.atom',
                    'test.datasource.atom.DummyEntryPermalinkProvider',
                    'test.datasource.atom.DummyFeedPermalinkProvider'],
        'ENTRY_PERMALINK': 'test.datasource.atom',
        'FEED_PERMALINK': 'test.datasource.atom',
        'ATOM_DEFAULT_TITLE': 'Firmant Atom Feed',
        'ATOM_DEFAULT_RIGHTS': 'Same as source.',
        'ATOM_DEFAULT_SUBTITLE': 'The default atom feed',
        'ATOM_PROVIDER': 'firmant.plugins.datasource.flatfile.atom',
        'FLATFILE_BASE': 'checkout/'
}


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
