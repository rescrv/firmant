import unittest

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

    def testYear(self):
        self.loadData()
        tdr = DateResolver()
        self.assertEqual([e3, e2, e1].__repr__(),
                tdr.resolve(FakeRequest('/2009/')))

    def testMonth(self):
        self.loadData()
        tdr = DateResolver()
        self.assertEqual([e3, e2, e1].__repr__(),
                tdr.resolve(FakeRequest('/2009/02/')))

    def testDay(self):
        self.loadData()
        tdr = DateResolver()
        self.assertEqual([e3, e2].__repr__(),
                tdr.resolve(FakeRequest('/2009/02/17/')))
        self.assertEqual([e1].__repr__(),
                tdr.resolve(FakeRequest('/2009/02/13/')))

    def testSingle(self):
        self.loadData()
        tdr = DateResolver()
        self.assertEqual(e3.__repr__(),
                tdr.resolve(FakeRequest('/2009/02/17/sample/')))
        self.assertEqual(e2.__repr__(),
                tdr.resolve(FakeRequest('/2009/02/17/loren-ipsum/')))
        self.assertEqual(e1.__repr__(),
                tdr.resolve(FakeRequest('/2009/02/13/sample/')))


suite = unittest.TestLoader().loadTestsFromTestCase(TestTxtDateResolver)
