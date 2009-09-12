import unittest
import weakref
import shutil

from firmant.datasource.atom import AtomCategoryProvider
from firmant.datasource.atom import AtomAuthorProvider
from firmant.datasource.atom import AtomEntryProvider
from firmant.datasource.atom import AtomFeedProvider
from firmant.wsgi import RequestContext
from test.datasource.atom import TestEntry as BaseTestEntry
from test.datasource.atom import TestAuthor as BaseTestAuthor
from test.datasource.atom import TestCategory as BaseTestCategory
from test.datasource.atom import TestFeed as BaseTestFeed
from test.datasource.atom import DummyEntryPermalinkProvider
from test.datasource.atom import DummyFeedPermalinkProvider
from test.utils import clone_dir_to_tmp

prefix = 'firmant.plugins.datasource.flatfile.atom'

settings = {
        'ENTRY_PERMALINK': 'test.datasource.atom.DummyEntryPermalinkProvider',
        'FEED_PERMALINK': 'test.datasource.atom.DummyFeedPermalinkProvider',
        'ATOM_DEFAULT_TITLE': 'Firmant Atom Feed',
        'ATOM_DEFAULT_RIGHTS': 'Same as source.',
        'ATOM_DEFAULT_SUBTITLE': 'The default atom feed',
        'ATOM_FEED_PROVIDER': prefix + '.AtomFlatfileFeedProvider',
        'ATOM_AUTHOR_PROVIDER': prefix + '.AtomFlatfileAuthorProvider',
        'ATOM_CATEGORY_PROVIDER': prefix + '.AtomFlatfileCategoryProvider',
        'ATOM_ENTRY_PROVIDER': prefix + '.AtomFlatfileEntryProvider',
        'FLATFILE_BASE': 'checkout/'
}


class TestAuthor(BaseTestAuthor):

    def setUp(self):
        s = settings.copy()
        method = self.id().split('.')[-1]
        if method in ('testSave1', 'testSave2', 'testDelete1', 'testDelete2'):
            self.tmpdir = tmp = clone_dir_to_tmp('checkout/')
            s['FLATFILE_BASE'] = tmp
        else:
            self.tmpdir = None
        self.rc       = RequestContext(s)
        self.provider = self.rc.get(AtomAuthorProvider)

    def tearDown(self):
        if self.tmpdir is not None:
            shutil.rmtree(self.tmpdir)


class TestCategory(BaseTestCategory):

    def setUp(self):
        self.rc       = RequestContext(settings)
        self.provider = self.rc.get(AtomCategoryProvider)


class TestEntry(BaseTestEntry):

    def setUp(self):
        self.rc       = RequestContext(settings)
        self.provider = self.rc.get(AtomEntryProvider)


class TestFeed(BaseTestFeed):

    def setUp(self):
        self.rc       = RequestContext(settings)
        self.provider = self.rc.get(AtomFeedProvider)

    def testBadPerms(self):
        '''firmant.plugins.datasource.flatfile.FlatfileAtomProvider.feed.by_slug
        Test the case that permissions are not adequately set on feeds.'''
        provider = self.provider

        expected = None
        returned = provider.by_slug('badperms')

        self.assertEqual(expected, returned)


from test import add_test
suite = unittest.TestSuite()
add_test(suite, TestAuthor)
add_test(suite, TestCategory)
add_test(suite, TestEntry)
add_test(suite, TestFeed)
