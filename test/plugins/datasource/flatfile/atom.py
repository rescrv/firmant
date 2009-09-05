import unittest
import weakref

from firmant.plugins.datasource.flatfile.atom import FlatfileAtomProvider
from firmant.plugins.datasource.flatfile.atom import AtomFlatfileCategoryProvider
from firmant.wsgi import RequestContext
from test.datasource.atom import TestEntry as BaseTestEntry
from test.datasource.atom import TestAuthor as BaseTestAuthor
from test.datasource.atom import TestCategory as BaseTestCategory
from test.datasource.atom import TestFeed as BaseTestFeed
from test.datasource.atom import DummyEntryPermalinkProvider
from test.datasource.atom import DummyFeedPermalinkProvider


settings = {
        'ENTRY_PERMALINK': 'test.datasource.atom.DummyEntryPermalinkProvider',
        'FEED_PERMALINK': 'test.datasource.atom.DummyFeedPermalinkProvider',
        'ATOM_DEFAULT_TITLE': 'Firmant Atom Feed',
        'ATOM_DEFAULT_RIGHTS': 'Same as source.',
        'ATOM_DEFAULT_SUBTITLE': 'The default atom feed',
        'ATOM_PROVIDER': 'firmant.plugins.datasource.flatfile.atom',
        'FLATFILE_BASE': 'checkout/'
}


class TestAuthor(BaseTestAuthor):

    def setUp(self):
        pass

    def get_provider(self, name):
        rc = RequestContext(settings)
        return rc.get(FlatfileAtomProvider)


class TestCategory(BaseTestCategory):

    def setUp(self):
        self.rc       = RequestContext(settings)
        self.provider = self.rc.get(AtomFlatfileCategoryProvider)


class TestEntry(BaseTestEntry):

    def setUp(self):
        pass

    def get_provider(self, name):
        rc = RequestContext(settings)
        return rc.get(FlatfileAtomProvider)


class TestFeed(BaseTestFeed):

    def setUp(self):
        pass

    def testBadPerms(self):
        '''firmant.plugins.datasource.flatfile.FlatfileAtomProvider.feed.by_slug
        Test the case that permissions are not adequately set on feeds.'''
        provider = self.get_provider('BySlug1')
        feed     = provider.feed

        expected = None
        returned = feed.by_slug('badperms')

        self.assertEqual(expected, returned)


    def get_provider(self, name):
        rc = RequestContext(settings)
        return rc.get(FlatfileAtomProvider)


from test import add_test
suite = unittest.TestSuite()
add_test(suite, TestAuthor)
add_test(suite, TestCategory)
add_test(suite, TestEntry)
add_test(suite, TestFeed)
