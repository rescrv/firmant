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
        self.e1 = Entry()
        self.e1.slug           = 'sample'
        self.e1.published_date = datetime.date(2009, 2, 13)
        self.e1.published_time = datetime.time(23, 31, 30)
        self.e1.author_name    = 'Robert Escriva'
        self.e1.author_uri     = 'http://robescriva.com'
        self.e1.author_email   = 'rob@/dev/null'
        self.e1.category_term  = 'General'
        self.e1.category_label = 'All topics'
        self.e1.rights         = 'Same as source.'
        self.e1.updated        = datetime.datetime(2009, 2, 13, 23, 31, 30)
        self.e1.title          = 'Unix 1234567890'
        self.e1.content        = 'This is the main content of revision two.'
        self.e1.summary        = 'This is the summary of revision two.'

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
        self.assertEqual(e, self.e1)


suite = unittest.TestLoader().loadTestsFromTestCase(TestAtomSchema)
