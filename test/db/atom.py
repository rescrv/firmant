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

        self.e2 = Entry()
        self.e2.slug           = 'loren-ipsum'
        self.e2.published_date = datetime.date(2009, 2, 17)
        self.e2.published_time = datetime.time(11, 31, 30)
        self.e2.author_name    = 'Loren Ipsum Generator'
        self.e2.author_uri     = 'http://www.lipsum.com'
        self.e2.author_email   = 'lipsum@/dev/null'
        self.e2.category_term  = 'Generated'
        self.e2.category_label = "You can't tell a computer wrote it."
        self.e2.rights         = 'Same as source.'
        self.e2.updated        = datetime.datetime(2009, 2, 17, 11, 31, 30)
        self.e2.title          = 'Loren Ipsum ...'
        self.e2.content        = (
     """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus eget
     ante sit amet elit condimentum varius. Nullam blandit pede quis neque.
     Suspendisse elit erat, malesuada quis, ultrices cursus, pretium eget,
     tortor. Sed volutpat pede in neque rhoncus aliquet. In vulputate, tellus id
     scelerisque vestibulum, eros diam vehicula massa, ac mollis leo augue quis
     tortor. Vivamus sed eros vitae tortor tincidunt consequat. Morbi in erat
     non erat tristique accumsan. Quisque ornare libero ut turpis. Phasellus et
     tortor. Vestibulum dapibus aliquet sapien. Quisque ut ante in erat auctor
     accumsan. Morbi accumsan dolor ut est.

     Nam urna lectus, auctor vel, placerat ac, fringilla interdum, leo. Donec
     congue venenatis lorem. Mauris pellentesque venenatis est. Mauris nisl
     dolor, ultrices a, condimentum vel, consequat sit amet, risus. Nulla
     porttitor nisl ut magna venenatis commodo. Donec sagittis leo in neque. Cum
     sociis natoque penatibus et magnis dis parturient montes, nascetur
     ridiculus mus. In hac habitasse platea dictumst. Praesent libero velit,
     volutpat sit amet, molestie id, condimentum nec, lorem. Aliquam erat
     volutpat. Vivamus scelerisque purus nec nulla. Aliquam tortor. Suspendisse
     laoreet porta augue. Curabitur at sapien in enim consequat blandit. Nulla
     ac dui. Nunc felis est, tempor sit amet, tincidunt id, auctor quis, eros.
     In molestie est a neque. Aliquam erat volutpat. Nam commodo tincidunt
     magna.  Morbi justo leo, faucibus nec, consectetur id, sodales vitae,
     nunc.""")
        self.e2.summary        = 'A generated loren ipsum paragraph.'

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

    def testEntrySingleEmpty(self):
        self.testLoadData()
        e = Entry.single('IDONOTEXIST', datetime.date(2009, 2, 13))
        self.assertEqual(e, None)

    def testEntrySinglePresent(self):
        self.testLoadData()
        e = Entry.single('sample', datetime.date(2009, 2, 13))
        self.assertEqual(e, self.e1)
        e = Entry.single('loren-ipsum', datetime.date(2009, 2, 17))
        self.assertEqual(e, self.e2)


suite = unittest.TestLoader().loadTestsFromTestCase(TestAtomSchema)
