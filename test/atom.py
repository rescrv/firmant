import unittest
import psycopg2

from firmant.configuration import settings


class TestAtomSchema(unittest.TestCase):

    def setUp(self):
        # We do not want other tests to affect settings in here.
        # We do not use the DB api as we are testing the actual 
        self.conn = psycopg2.connect(settings['TEST_ATOM_DB_CONNECT'])

    def tearDown(self):
        # We do not want settings in here to affect any other tests.
        self.conn.commit()
        self.conn.close()

    def testDrop(self):
        cur = self.conn.cursor()
        cur.execute('DROP SCHEMA IF EXISTS atom CASCADE;')

suite = unittest.TestLoader().loadTestsFromTestCase(TestAtomSchema)
