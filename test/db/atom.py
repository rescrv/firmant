import unittest
import psycopg2
import datetime

from firmant.configuration import settings
from firmant.db.relations import schema
from firmant.db.atom import AtomDB
from firmant.db.atom import Entry


e1 = Entry()
e1.slug           = 'sample'
e1.published      = datetime.datetime(2009, 2, 14, 04, 31, 30)
e1.author_name    = 'Robert Escriva'
e1.author_uri     = 'http://robescriva.com'
e1.author_email   = 'rob@/dev/null'
e1.category_term  = 'General'
e1.category_label = 'All topics'
e1.rights         = 'Same as source.'
e1.updated        = datetime.datetime(2009, 2, 14, 04, 31, 31)
e1.title          = 'Unix 1234567890'
e1.content        = 'This is the main content of revision two.'
e1.summary        = 'This is the summary of revision two.'

e2 = Entry()
e2.slug           = 'loren-ipsum'
e2.published      = datetime.datetime(2009, 2, 17, 16, 31, 30)
e2.author_name    = 'Loren Ipsum Generator'
e2.author_uri     = 'http://www.lipsum.com'
e2.author_email   = 'lipsum@/dev/null'
e2.category_term  = 'Generated'
e2.category_label = "You can't tell a computer wrote it."
e2.rights         = 'Same as source.'
e2.updated        = datetime.datetime(2009, 2, 17, 16, 31, 30)
e2.title          = 'Loren Ipsum ...'
e2.content        = (
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
e2.summary        = 'A generated loren ipsum paragraph.'

e3 = Entry()
e3.slug           = 'sample'
e3.published      = datetime.datetime(2009, 2, 17, 21, 31, 30)
e3.author_name    = 'Loren Ipsum Generator'
e3.author_uri     = 'http://www.lipsum.com'
e3.author_email   = 'lipsum@/dev/null'
e3.category_term  = 'Generated'
e3.category_label = "You can't tell a computer wrote it."
e3.rights         = 'Same as source.'
e3.updated        = datetime.datetime(2009, 2, 17, 16, 31, 30)
e3.title          = 'Loren Ipsum ...'
e3.content        = 'This is the main content of revision one.'
e3.summary        = 'This is the summary of revision one.'

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

    def testEntrySingleEmpty(self):
        self.testLoadData()
        e = Entry.single('IDONOTEXIST', datetime.date(2009, 2, 13))
        self.assertEqual(e, None)

    def testEntrySinglePresent(self):
        self.testLoadData()
        e = Entry.single('sample', datetime.date(2009, 2, 13))
        self.assertEqual(e, e1)
        e = Entry.single('loren-ipsum', datetime.date(2009, 2, 17))
        self.assertEqual(e, e2)

    def testEntrySingleSlugInvalid(self):
        self.testLoadData()
        self.assertRaises(ValueError,
            Entry.single, 's@mpl3', datetime.date(2009, 2, 13))

    def testEntrySingleNoStrftime(self):
        self.testLoadData()
        # List does not have strftime method
        self.assertRaises(ValueError, Entry.single, 'sample', list())

    def testEntryDayEmpty(self):
        self.testLoadData()
        e = Entry.day('2009', '01', '09')
        self.assertEqual(len(e), 0)

    def testEntryDayPresent(self):
        self.testLoadData()
        e = Entry.day('2009', '02', '13')
        self.assertEqual(1, len(e))
        self.assertEqual(e[0], e1)

    def testEntryDayOrder(self):
        self.testLoadData()
        e = Entry.day('2009', '02', '17')
        self.assertEqual(2, len(e))
        self.assertEqual(e[0], e3)
        self.assertEqual(e[1], e2)

    def testEntryDayInvalidDate(self):
        self.testLoadData()
        self.assertRaises(ValueError, Entry.day, 2009, 0, 0)

    def testEntryDateTrunc(self):
        self.assertRaises(ValueError, Entry._date_trunc, 'foo', 2009, 2, 13)

    def testEntryMonthEmpty(self):
        self.testLoadData()
        e = Entry.month('2009', '01')
        self.assertEqual(len(e), 0)

    def testEntryMonthPresent(self):
        self.testLoadData()
        e = Entry.month('2009', '02')
        self.assertEqual(3, len(e))
        self.assertEqual(e[0], e3)
        self.assertEqual(e[1], e2)
        self.assertEqual(e[2], e1)

    def testEntryYearEmpty(self):
        self.testLoadData()
        e = Entry.year('2008')
        self.assertEqual(len(e), 0)

    def testEntryYearPresent(self):
        self.testLoadData()
        e = Entry.year('2009')
        self.assertEqual(3, len(e))
        self.assertEqual(e[0], e3)
        self.assertEqual(e[1], e2)
        self.assertEqual(e[2], e1)

    def testEntryRecentPresent(self):
        self.testLoadData()
        e = Entry.recent()
        self.assertEqual(3, len(e))
        self.assertEqual(e[0], e3)
        self.assertEqual(e[1], e2)
        self.assertEqual(e[2], e1)

    def testEntryRecentEmpty(self):
        e = Entry.recent()
        self.assertEqual(e, [])

    def testEntryForFeedEmpty(self):
        self.testLoadData()
        self.assertEqual([], Entry.for_feed('Idon_tExist'))

    def testEntryForFeedPresent(self):
        self.testLoadData()
        results = Entry.for_feed('general')
        self.assertEqual([e2, e1], results)


suite = unittest.TestLoader().loadTestsFromTestCase(TestAtomSchema)
