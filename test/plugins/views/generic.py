import unittest

from firmant.plugins.views.generic import paginate


class DummyUrls(object):

    def build(self, endpoint, args, force_external):
        return (endpoint, args)


rc    = {}
rc['args'] = {'args': True}
rc['endpoint'] = 'endpoint'
rc['urls'] = DummyUrls()


class TestPaginate(unittest.TestCase):

    def testNoPaginationNecessary(self):
        '''firmant.plugins.views.generic.paginate
        Tests the case where there are not enough entries in a list to trigger
        pagination.'''

        func  = lambda x, y: (range(1,11)[y:x + y], 10 - (x + y))
        page  = 0
        limit = 10

        new_list, page = paginate(lambda: rc.copy(), limit, func, page)

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

        new_list, page = paginate(lambda: rc.copy(), limit, func, page)

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

        new_list, page = paginate(lambda: rc.copy(), limit, func, page)

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

        new_list, page = paginate(lambda: rc.copy(), limit, func, page)

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

        new_list, page = paginate(lambda: rc.copy(), limit, func, page)

        self.assertEqual(range(11, 16), new_list)
        self.assertEqual(page.has_newer, True)
        self.assertEqual(page.has_older, False)
        self.assertEqual(page.newer, ('endpoint', {'args': True, 'page': 1}))
        self.assertEqual(page.older, None)


from test import add_test
suite = unittest.TestSuite()
add_test(suite, TestPaginate)
