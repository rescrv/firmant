import unittest

from firmant.wsgi import Response
from firmant.frontend.txt.resolvers import TxtDateResolver as DateResolver
from firmant.db.relations import schema
from firmant.db.atom import AtomDB
from test.db.atom import e1, e2, e3
from test.resolvers import FakeRequest


class TestTxtDateResolver(unittest.TestCase):

    def setUp(self):
        # We do not want other tests to affect settings in here.
        AtomDB.reset()

    def tearDown(self):
        # We do not want settings in here to affect any other tests.
        AtomDB.reset()

    def loadData(self):
        # Load some sample fixtures for use by other tests.
        atom = schema('atom-sample-data')
        conn = AtomDB.connection(readonly=False)
        cur = conn.cursor()
        cur.execute(atom)
        cur.close()
        conn.commit()
        conn.close()

    def testRecent(self):
        self.loadData()
        tdr = DateResolver()
        self.assertEqual(Response(content=[e3, e2, e1].__repr__()),
                tdr.resolve(FakeRequest('/')))

    def testYear(self):
        self.loadData()
        tdr = DateResolver()
        self.assertEqual(Response(content=[e3, e2, e1].__repr__()),
                tdr.resolve(FakeRequest('/2009/')))

    def testMonth(self):
        self.loadData()
        tdr = DateResolver()
        self.assertEqual(Response(content=[e2, e1].__repr__()),
                tdr.resolve(FakeRequest('/2009/02/')))

    def testDay(self):
        self.loadData()
        tdr = DateResolver()
        self.assertEqual(Response(content=[e3].__repr__()),
                tdr.resolve(FakeRequest('/2009/03/17/')))
        self.assertEqual(Response(content=[e2].__repr__()),
                tdr.resolve(FakeRequest('/2009/02/17/')))
        self.assertEqual(Response(content=[e1].__repr__()),
                tdr.resolve(FakeRequest('/2009/02/13/')))

    def testSingle(self):
        self.loadData()
        tdr = DateResolver()
        self.assertEqual(Response(content=e3.__repr__()),
                tdr.resolve(FakeRequest('/2009/03/17/sample/')))
        self.assertEqual(Response(content=e2.__repr__()),
                tdr.resolve(FakeRequest('/2009/02/17/loren-ipsum/')))
        self.assertEqual(Response(content=e1.__repr__()),
                tdr.resolve(FakeRequest('/2009/02/13/sample/')))

    def testInvalid(self):
        tdr = DateResolver()
        self.assertEqual(None, tdr._year(None, '200a'))
        self.assertEqual(None, tdr._month(None, '200a', '02'))
        self.assertEqual(None, tdr._month(None, '2009', '0a'))
        self.assertEqual(None, tdr._day(None, '200a', '02', '13'))
        self.assertEqual(None, tdr._day(None, '2009', '0a', '13'))
        self.assertEqual(None, tdr._day(None, '2009', '02', 'b3'))
        self.assertEqual(None, tdr._single(None, 'foo', '200a', '02', '13'))
        self.assertEqual(None, tdr._single(None, 'foo', '2009', '0a', '13'))
        self.assertEqual(None, tdr._single(None, 'foo', '2009', '02', 'b3'))
        self.assertEqual(None, tdr._single(None, 'fo#o', '2009', '02', '13'))


suite = unittest.TestLoader().loadTestsFromTestCase(TestTxtDateResolver)
