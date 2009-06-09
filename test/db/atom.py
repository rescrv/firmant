import unittest

from firmant.configuration import settings
from firmant.db.relations import schema
from firmant.db.relations import DB
from firmant.db.atom import Entry
from firmant.db.atom import AtomDB
from test.backend.atom import generate_e1, \
                              generate_e2, \
                              generate_e3, \
                              generate_e4
from test.backend.atom import TestEntry as BaseTestEntry


def reset():
    _drop()
    _setup()


def _drop():
    conn = DB.connection()
    cur = conn.cursor()
    cur.execute('DROP SCHEMA IF EXISTS atom CASCADE;')
    cur.close()
    conn.commit()
    conn.close()


def _setup():
    atom = schema('atom')
    conn = DB.connection()
    cur = conn.cursor()
    cur.execute(atom)
    cur.close()
    conn.commit()
    conn.close()


class TestAtomSchema(unittest.TestCase):

    def setUp(self):
        # We do not want other tests to affect settings in here.
        reset()

    def tearDown(self):
        # We do not want settings in here to affect any other tests.
        reset()

    def testReset(self):
        # This tests the reset functionality of the schema.
        reset()

    def testGetReadConnection(self):
        conn = AtomDB.connection(readonly=True)
        conn.close()

    def testGetWriteConnection(self):
        conn = AtomDB.connection(readonly=False)
        conn.close()


class TestEntry(BaseTestEntry):

    def setUp(self):
        self.Entry = Entry
        self.e1 = generate_e1(Entry)
        self.e2 = generate_e2(Entry)
        self.e3 = generate_e3(Entry)
        self.e4 = generate_e4(Entry)
        # We do not want other tests to affect settings in here.
        reset()
        self.loadData()

    def tearDown(self):
        # We do not want settings in here to affect any other tests.
        reset()

    def loadData(self):
        # Load some sample fixtures for use by other tests.
        atom = schema('atom-sample-data')
        conn = AtomDB.connection(readonly=False)
        cur = conn.cursor()
        cur.execute(atom)
        cur.close()
        conn.commit()
        conn.close()


suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAtomSchema))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEntry))
