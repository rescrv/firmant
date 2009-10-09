import unittest
from werkzeug.routing import Map, Rule
from werkzeug import Response

from firmant.views import CatchallProvider
from firmant.views import ViewProvider
from firmant.wsgi import RequestContext


class DummyViewProvider(object):

    def __init__(self, rc, settings):
        pass

    @property
    def rules(self):
        url_rules = [
            Rule('/' + self.name, endpoint=self.name + 'ViewProvider')
        ]
        return url_rules


class FooViewProvider(DummyViewProvider):
    name = 'Foo'

class BarViewProvider(DummyViewProvider):
    name = 'Bar'

class BazViewProvider(DummyViewProvider):
    name = 'Baz'

class QuuxViewProvider(DummyViewProvider):
    name = 'Quux'


class TestViewProvider(unittest.TestCase):

    def setUp(self):
        views    = map(lambda x: 'test.views.%sViewProvider' % x,
                        ['Foo', 'Bar', 'Baz', 'Quux'])
        self.settings = {'VIEWS': views}
        self.rc       = RequestContext(self.settings)
        self.vp       = self.rc.get(ViewProvider)
        self.urlmap   = self.vp.url_map

    def testUrlMap(self):
        '''firmant.views.ViewProvider.url_map'''

        urlmap   = self.urlmap

        expected = [('FooViewProvider', '/Foo'),
                    ('BarViewProvider', '/Bar'),
                    ('BazViewProvider', '/Baz'),
                    ('QuuxViewProvider', '/Quux')]
        returned = map(lambda x: (x.endpoint, x.rule), urlmap.iter_rules())

        self.assertEqual(expected, returned)

    def testGetClass1(self):
        '''firmant.views.ViewProvider.get_class
        Get the instantiated class for valid endpoint.'''

        instance = self.vp.get_class('test.views.FooViewProvider')
        returned = isinstance(instance, FooViewProvider)

        self.assertTrue(returned)

    def testGetClass2(self):
        '''firmant.views.ViewProvider.get_class
        Receive 'None' if we ask for an invalid endpoint'''

        expected = None
        returned = self.vp.get_class('Invalid Endpoint')

        self.assertEqual(expected, returned)


class TestCatchallProvider(unittest.TestCase):

    def testCatchall(self):
        '''firmant.views.CatchallProvider.catchall'''
        provider         = CatchallProvider(None, None)
        returned         = provider.catchall(None, 'hello/world/')

        expected_content = '''If you're reading this the catchall provider
            functions well on your system (hello/world/).'''
        expected_status  = 200
        expected_mime    = 'text/plain'

        returned_content = returned.data
        returned_status  = returned.status_code
        returned_mime    = returned.mimetype

        self.assertEqual(expected_content, returned_content)
        self.assertEqual(expected_status,  returned_status)
        self.assertEqual(expected_mime,    returned_mime)

    def testRules(self):
        '''firmant.views.CatchallProvider.rules'''

        provider                   = CatchallProvider(None, None)
        mapped                     = Map(provider.rules)
        environ                    = {}
        environ['SERVER_NAME']     = 'unittests.localdomain'
        environ['SERVER_PORT']     = '80'
        environ['REQUEST_METHOD']  = 'GET'
        environ['PATH_INFO']       = '/hello/world'
        environ['wsgi.url_scheme'] = 'http'
        urls                       = mapped.bind_to_environ(environ)

        expected = ('firmant.views.CatchallProvider.catchall',
                   {'p': 'hello/world'})
        returned = urls.match()

        self.assertEqual(expected, returned)


from test import add_test
suite = unittest.TestSuite()
add_test(suite, TestViewProvider)
add_test(suite, TestCatchallProvider)

from test.views.generic import suite as generic_tests
suite.addTests(generic_tests)
