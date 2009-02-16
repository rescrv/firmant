import unittest
import psycopg2
import datetime

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

    def testEntrySingle(self):
        # Load some sample fixtures for use by other tests.
        atom = schema('atom-sample-data')
        conn = AtomDB.connection(readonly=False)
        cur = conn.cursor()
        cur.execute(atom)
        cur.close()
        conn.commit()
        conn.close()
        e = Entry.single('sample', datetime.date(2009, 2, 13))
        self.assertEqual(e.slug, 'sample')
        self.assertEqual(e.published_date, datetime.date(2009, 2, 13))
        self.assertEqual(e.published_time, datetime.time(23, 31, 30))
        self.assertEqual(e.author_name, 'Robert Escriva')
        self.assertEqual(e.author_uri, 'http://robescriva.com')
        self.assertEqual(e.author_email, 'rob@/dev/null')
        self.assertEqual(e.category_term, 'General')
        self.assertEqual(e.category_label, 'All topics')
        self.assertEqual(e.rights, 'Same as source.')
        #self.assertEqual(e.updated, datetime.datetime(2009, 2, 13, 23, 31, 30))
        self.assertEqual(e.title, 'Unix 1234567890')
        self.assertEqual(e.content, 'This is the main content of revision two.')
        self.assertEqual(e.summary, 'This is the summary of revision two.')


suite = unittest.TestLoader().loadTestsFromTestCase(TestAtomSchema)
