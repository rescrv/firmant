import unittest

from firmant.plugins.views.generic import paginate
from firmant.plugins.views.generic import GenericEntryViewProvider
from firmant.wsgi import RequestContext
from test.datasource.atom import entries


class DummyUrls(object):

    def build(self, endpoint, args, force_external):
        return (endpoint, args)


class TestPaginate(unittest.TestCase):

    def setUp(self):
        self.rc    = {}
        self.rc['args'] = {'args': True}
        self.rc['endpoint'] = 'endpoint'
        self.rc['urls'] = DummyUrls()

    def testNoPaginationNecessary(self):
        '''firmant.plugins.views.generic.paginate
        Tests the case where there are not enough entries in a list to trigger
        pagination.'''

        func  = lambda x, y: (range(1,11)[y:x + y], 10 - (x + y))
        page  = 0
        limit = 10

        new_list, page = paginate(lambda: self.rc.copy(), limit, func, page)

        self.assertEqual(range(1, 11), new_list)
        self.assertEqual(page.has_newer, False)
        self.assertEqual(page.has_older, False)
        self.assertEqual(page.newer, None)
        self.assertEqual(page.older, None)

    def testPaginationBeginning(self):
        '''firmant.plugins.views.generic.paginate
        Tests the case where there is a first and (at least) a second page
        because there are enough entries to require pagination.'''

        func = lambda x, y: (range(1, 16)[y:x + y], 15 - (x + y))
        page = 0
        limit = 5

        new_list, page = paginate(lambda: self.rc.copy(), limit, func, page)

        self.assertEqual(range(1, 6), new_list)
        self.assertEqual(page.has_newer, False)
        self.assertEqual(page.has_older, True)
        self.assertEqual(page.newer, None)
        self.assertEqual(page.older, ('endpoint', {'args': True, 'page': 1}))

    def testPaginationMiddle1(self):
        '''firmant.plugins.views.generic.paginate
        Tests the case where there is at least one middle page with one or more
        pages on each side.  This case has only 1 newer page.'''

        func = lambda x, y: (range(1, 16)[y:x + y], 15 - (x + y))
        page = 1
        limit = 5

        new_list, page = paginate(lambda: self.rc.copy(), limit, func, page)

        self.assertEqual(range(6, 11), new_list)
        self.assertEqual(page.has_newer, True)
        self.assertEqual(page.has_older, True)
        self.assertEqual(page.newer, ('endpoint', {'args': True}))
        self.assertEqual(page.older, ('endpoint', {'args': True, 'page': 2}))

    def testPaginationMiddle2(self):
        '''firmant.plugins.views.generic.paginate
        Tests the case where there is at least one middle page with one or more
        pages on each side.  This case has more than one newer page.'''

        func = lambda x, y: (range(1, 21)[y:x + y], 20 - (x + y))
        page = 2
        limit = 5

        new_list, page = paginate(lambda: self.rc.copy(), limit, func, page)

        self.assertEqual(range(11, 16), new_list)
        self.assertEqual(page.has_newer, True)
        self.assertEqual(page.has_older, True)
        self.assertEqual(page.newer, ('endpoint', {'args': True, 'page': 1}))
        self.assertEqual(page.older, ('endpoint', {'args': True, 'page': 3}))

    def testPaginationLast(self):
        '''firmant.plugins.views.generic.paginate
        Tests the case where there is at least one middle page with one or more
        pages on each side.  This case has only 1 newer page.'''

        func = lambda x, y: (range(1, 16)[y:x + y], 15 - (x + y))
        page = 2
        limit = 5

        new_list, page = paginate(lambda: self.rc.copy(), limit, func, page)

        self.assertEqual(range(11, 16), new_list)
        self.assertEqual(page.has_newer, True)
        self.assertEqual(page.has_older, False)
        self.assertEqual(page.newer, ('endpoint', {'args': True, 'page': 1}))
        self.assertEqual(page.older, None)


class DummyRequest(object):

    __slots__ = ['args']


class TestableGenericEntryViewProvider(GenericEntryViewProvider):

    limit = 1

    def _year(self, request, entries, page, year):
        return (year, entries, page.has_newer, page.has_older)

    def _month(self, request, entries, page, year, month):
        return (year, month, entries, page.has_newer, page.has_older)

    def _day(self, request, entries, page, year, month, day):
        return (year, month, day, entries, page.has_newer, page.has_older)


class TestGenericEntryViewProvider(unittest.TestCase):

    def setUp(self):
        prefix = 'firmant.plugins.datasource.flatfile.atom'
        settings = {}
        settings['ENTRY_PERMALINK'] = 'test.datasource.atom.DummyEntryPermalinkProvider'
        settings['FEED_PERMALINK'] = 'test.datasource.atom.DummyFeedPermalinkProvider'
        settings['ATOM_FEED_PROVIDER']     = prefix + '.AtomFlatfileFeedProvider'
        settings['ATOM_AUTHOR_PROVIDER']   = prefix + '.AtomFlatfileAuthorProvider'
        settings['ATOM_CATEGORY_PROVIDER'] = prefix + '.AtomFlatfileCategoryProvider'
        settings['ATOM_ENTRY_PROVIDER']    = prefix + '.AtomFlatfileEntryProvider'
        settings['FLATFILE_BASE']          = 'checkout/'
        self.rc = RequestContext(settings)
        self.rc.set('urls', DummyUrls())
        self.rc.set('endpoint', 'endpoint')
        self.rc.set('args', {})
        self.view = TestableGenericEntryViewProvider(lambda: self.rc, settings)

    def testYearPresent(self):
        '''firmant.plugins.views.generic.GenericEntryViewProvider.year
        Test the case that there are entries for the given year.'''
        request = DummyRequest()
        request.args = {}

        # page undefined
        expected = ('2009', [entries['2009-03-29-markdown']], False, True)
        returned = self.view.year(request, '2009')
        self.assertEqual(expected, returned)

        # page = 0
        self.rc.get('args')['page'] = request.args['page'] = 0
        expected = ('2009', [entries['2009-03-29-markdown']], False, True)
        returned = self.view.year(request, '2009')
        self.assertEqual(expected, returned)

        # page = 1
        self.rc.get('args')['page'] = request.args['page'] = 1
        expected = ('2009', [entries['2009-03-17-sample']], True, True)
        returned = self.view.year(request, '2009')
        self.assertEqual(expected, returned)

        # page = 2
        self.rc.get('args')['page'] = request.args['page'] = 2
        expected = ('2009', [entries['2009-02-17-loren-ipsum']], True, True)
        returned = self.view.year(request, '2009')
        self.assertEqual(expected, returned)

        # page = 3
        self.rc.get('args')['page'] = request.args['page'] = 3
        expected = ('2009', [entries['2009-02-13-sample']], True, False)
        returned = self.view.year(request, '2009')
        self.assertEqual(expected, returned)

    def testYearEmpty(self):
        '''firmant.plugins.views.generic.GenericEntryViewProvider.year
        Test the case that there are no entries for the given year.'''
        self.fail()

    def testYearNotValid(self):
        '''firmant.plugins.views.generic.GenericEntryViewProvider.year
        Test the case that the year requested is invalid.'''
        self.fail()

    def testMonthPresent(self):
        '''firmant.plugins.views.generic.GenericEntryViewProvider.month
        Test the case that there are entries for the given month.'''
        self.fail()

    def testMonthEmpty(self):
        '''firmant.plugins.views.generic.GenericEntryViewProvider.month
        Test the case that there are no entries for the given month.'''
        self.fail()

    def testMonthNotValid(self):
        '''firmant.plugins.views.generic.GenericEntryViewProvider.month
        Test the case that the month requested is invalid.'''
        self.fail()

    def testDayPresent(self):
        '''firmant.plugins.views.generic.GenericEntryViewProvider.day
        Test the case that there are entries for the given day.'''
        self.fail()

    def testDayEmpty(self):
        '''firmant.plugins.views.generic.GenericEntryViewProvider.day
        Test the case that there are no entries for the given day.'''
        self.fail()

    def testDayNotValid(self):
        '''firmant.plugins.views.generic.GenericEntryViewProvider.day
        Test the case that the day requested is invalid.'''
        self.fail()


from test import add_test
suite = unittest.TestSuite()
add_test(suite, TestPaginate)
add_test(suite, TestGenericEntryViewProvider)
