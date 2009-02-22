import unittest
from firmant.resolvers import *


class FakeRequest(object):

    def __init__(self, url):
        self.url = url


class TestResolver(unittest.TestCase):

    def testNonInstantiable(self):
        self.assertRaises(NotImplementedError, Resolver)


class TestDateResolver(unittest.TestCase):

    def testNoPrefixSuccess(self):
        dr = DateResolver()
        fr = FakeRequest('/')
        self.assertEqual('RECENT', dr.resolve(fr))
        fr = FakeRequest('/2009/02/13/foo/')
        self.assertEqual('2009-02-13 foo', dr.resolve(fr))
        fr = FakeRequest('/2009/02/13/')
        self.assertEqual('2009-02-13', dr.resolve(fr))
        fr = FakeRequest('/2009/02/')
        self.assertEqual('2009-02', dr.resolve(fr))
        fr = FakeRequest('/2009/')
        self.assertEqual('2009', dr.resolve(fr))

    def testNoPrefixFail(self):
        dr = DateResolver()
        fr = FakeRequest('')
        self.assertEqual(None, dr.resolve(fr))
        fr = FakeRequest('/2009/02/13/foo')
        self.assertEqual(None, dr.resolve(fr))
        fr = FakeRequest('/2009/02/13')
        self.assertEqual(None, dr.resolve(fr))
        fr = FakeRequest('/2009/02')
        self.assertEqual(None, dr.resolve(fr))
        fr = FakeRequest('/20a9/')
        self.assertEqual(None, dr.resolve(fr))

    def testPrefixSuccess(self):
        dr = DateResolver('prefix')
        fr = FakeRequest('/prefix/')
        self.assertEqual('RECENT', dr.resolve(fr))
        fr = FakeRequest('/prefix/2009/02/13/foo/')
        self.assertEqual('2009-02-13 foo', dr.resolve(fr))
        fr = FakeRequest('/prefix/2009/02/13/')
        self.assertEqual('2009-02-13', dr.resolve(fr))
        fr = FakeRequest('/prefix/2009/02/')
        self.assertEqual('2009-02', dr.resolve(fr))
        fr = FakeRequest('/prefix/2009/')
        self.assertEqual('2009', dr.resolve(fr))

    def testPrefixFail(self):
        dr = DateResolver()
        fr = FakeRequest('/prefix')
        self.assertEqual(None, dr.resolve(fr))
        fr = FakeRequest('/prefix/2009/02/13/foo')
        self.assertEqual(None, dr.resolve(fr))
        fr = FakeRequest('/prefix/2009/02/13')
        self.assertEqual(None, dr.resolve(fr))
        fr = FakeRequest('/prefix/2009/02')
        self.assertEqual(None, dr.resolve(fr))
        fr = FakeRequest('/prefix/20a9/')
        self.assertEqual(None, dr.resolve(fr))


suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestResolver))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDateResolver))
