import unittest
import tempfile
import shutil

from firmant.plugins.csrf.flatfile import FlatfileCSRFTokenProvider
from test.csrf import TestCSRFTokenProvider as BaseTestCSRFTokenProvider


class TestCSRFTokenProvider(BaseTestCSRFTokenProvider):

    def setUp(self):

        settings = {}
        # This CSRF secret is insufficient for production and is used as an
        # example.
        settings['CSRF_SERVER_SECRET'] = 'abc123'
        settings['CSRF_TOKENS_DIR']    = self._dir = tempfile.mkdtemp()
        if self.id().rsplit('.', 1)[1] == 'testConsumeToken4':
            settings['CSRF_TOKEN_TTL'] = 0
        else:
            settings['CSRF_TOKEN_TTL'] = 60
        self._provider = FlatfileCSRFTokenProvider(None, settings)

    def tearDown(self):
        del self._provider
        shutil.rmtree(self._dir)


from test import add_test
suite = unittest.TestSuite()
add_test(suite, TestCSRFTokenProvider)
