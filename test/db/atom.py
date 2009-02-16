import unittest
import psycopg2

from firmant.configuration import settings
from firmant.db.relations import schema
from firmant.db.atom import AtomDB
from firmant.db.atom import Entry


class TestAtomSchema(unittest.TestCase):

    def setUp(self):
        # We do not want other tests to affect settings in here.
        AtomDB.reset()

    def tearDown(self):
        # We do not want settings in here to affect any other tests.
        AtomDB.reset()

    def testReset(self):
        # This tests the reset functionality of the schema.
        AtomDB.reset()

    def testGetReadConnection(self):
        conn = AtomDB.connection(readonly=True)
        conn.close()

    def testGetWriteConnection(self):
        conn = AtomDB.connection(readonly=False)
        conn.close()

    def testLoadData(self):
        # Load some sample fixtures for use by other tests.
        atom = schema('atom-sample-data')
        conn = AtomDB.connection(readonly=False)
        cur = conn.cursor()
        cur.execute(atom)
        cur.close()
        conn.commit()
        conn.close()



suite = unittest.TestLoader().loadTestsFromTestCase(TestAtomSchema)
