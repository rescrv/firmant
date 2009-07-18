import unittest
from werkzeug.routing import Map

from firmant.views import CatchallProvider


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


suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCatchallProvider))
