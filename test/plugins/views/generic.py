import unittest

from firmant.plugins.views.generic import paginate


class DummyUrls(object):

    def build(endpoint, args, force_external):
        return (endpoint, args, force_external)


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


from test import add_test
suite = unittest.TestSuite()
add_test(suite, TestPaginate)
