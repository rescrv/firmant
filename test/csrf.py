import unittest
import re
import time


class TestCSRFTokenProvider(unittest.TestCase):

    def testRequestToken1(self):
        '''firmant.csrf.CSRFTokenProvider.request_token
        Get a valid token.'''
        token    = self._provider.request_token('127.0.0.1')

        expected = True
        returned = token != ''

        self.assertEqual(expected, returned)

    def testRequestToken2(self):
        '''firmant.csrf.CSRFTokenProvider.request_token
        Raise ValueError for bad IP.  It is an error to pass a hostname to the
        request_token function.'''
        raises   = ValueError
        function = lambda: self._provider.request_token('host.tld')

        self.assertRaises(raises, function)

    def testConsumeToken1(self):
        '''firmant.csrf.CSRFTokenProvider.consume_token
        Request and consume a valid token.'''
        token    = self._provider.request_token('127.0.0.1')

        expected = True
        returned = self._provider.consume_token(token, '127.0.0.1')

        self.assertEqual(expected, returned)

    def testConsumeToken2(self):
        '''firmant.csrf.CSRFTokenProvider.consume_token
        Consuming a false token returns False.'''
        token    = 'a token we have not received from the system.'

        expected = False
        returned = self._provider.consume_token(token, '127.0.0.1')

        self.assertEqual(expected, returned)

    def testConsumeToken3(self):
        '''firmant.csrf.CSRFTokenProvider.consume_token
        Request and consume a valid token.  If you consume it again, it will be
        return False.'''
        token    = self._provider.request_token('127.0.0.1')

        expected = True
        returned = self._provider.consume_token(token, '127.0.0.1')
        self.assertEqual(expected, returned)

        expected = False
        returned = self._provider.consume_token(token, '127.0.0.1')
        self.assertEqual(expected, returned)

    def testConsumeToken4(self):
        '''firmant.csrf.CSRFTokenProvider.consume_token
        Request a token, and wait for it to timeout.  It should not be
        consumable.'''
        token    = self._provider.request_token('127.0.0.1')
        time.sleep(2)

        expected = False
        returned = self._provider.consume_token(token, '127.0.0.1')

        self.assertEqual(expected, returned)
