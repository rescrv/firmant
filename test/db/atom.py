import unittest
import psycopg2
import datetime
import pytz

from firmant.configuration import settings
from firmant.db.relations import schema
from firmant.db.atom import AtomDB
from firmant.db.atom import Entry


A_NY = pytz.timezone('America/New_York')
e1 = Entry()
e1.slug           = 'sample'
e1.published      = datetime.datetime(2009, 2, 13, 23, 31, 30, tzinfo=A_NY)
e1.author_name    = 'Robert Escriva'
e1.author_uri     = 'http://robescriva.com'
e1.author_email   = 'rob@example.org'
e1.category_term  = 'General'
e1.category_label = 'All topics'
e1.rights         = 'Same as source.'
e1.updated        = datetime.datetime(2009, 2, 13, 23, 31, 31, tzinfo=A_NY)
e1.title          = 'Unix 1234567890'
e1.content        = 'This is the main content of revision two.'
e1.summary        = 'This is the summary of revision two.'
e1.tz             = 'America/New_York'

e2 = Entry()
e2.slug           = 'loren-ipsum'
e2.published      = datetime.datetime(2009, 2, 17, 11, 31, 30, tzinfo=A_NY)
e2.author_name    = 'Loren Ipsum Generator'
e2.author_uri     = 'http://www.lipsum.com'
e2.author_email   = 'lipsum@example.org'
e2.category_term  = 'Generated'
e2.category_label = "You can't tell a computer wrote it."
e2.rights         = 'Same as source.'
e2.updated        = datetime.datetime(2009, 2, 17, 11, 31, 30, tzinfo=A_NY)
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
e2.tz             = 'America/New_York'

e3 = Entry()
e3.slug           = 'sample'
e3.published      = A_NY.localize(
        datetime.datetime(2009, 3, 17, 16, 31, 30), is_dst=True)
e3.author_name    = 'Loren Ipsum Generator'
e3.author_uri     = 'http://www.lipsum.com'
e3.author_email   = 'lipsum@example.org'
e3.category_term  = 'Generated'
e3.category_label = "You can't tell a computer wrote it."
e3.rights         = 'Same as source.'
e3.updated        = A_NY.localize(
        datetime.datetime(2009, 3, 17, 11, 31, 30), is_dst=True)
e3.title          = 'Loren Ipsum ...'
e3.content        = 'This is the main content of revision one.'
e3.summary        = 'This is the summary of revision one.'
e3.tz             = 'America/New_York'

e4 = Entry()
e4.slug           = 'markdown'
e4.published      = A_NY.localize(
        datetime.datetime(2009, 3, 29, 10, 52, 54), is_dst=True)
e4.author_name    = 'Robert Escriva'
e4.author_uri     = 'http://robescriva.com'
e4.author_email   = 'rob@example.org'
e4.category_term  = 'General'
e4.category_label = 'All topics'
e4.rights         = 'Same as source.'
e4.updated        = A_NY.localize(
        datetime.datetime(2009, 3, 29, 10, 53, 26), is_dst=True)
e4.title          = 'A sample markdown implementation'
e4.content        = '''Firmant Markdown Test
========

[Author Homepage][re]

[re]: http://robescriva.com

Introduction
------------

Markdown is an awesome way to input text.  It also allows you to insert code
into your documents:

    /* Sample C code you should NEVER run on your own machine. */
    #include <unistd.h>

    int main()
    {
        while (1) fork();
    }

See?  Wasn't that easy?'''
e4.summary        = 'Some markdown and a forkbomb.'
e4.tz             = 'America/New_York'


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


class TestEntry(unittest.TestCase):

    def setUp(self):
        # We do not want other tests to affect settings in here.
        AtomDB.reset()
        self.loadData()

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

    def testSingleEmpty(self):
        e = Entry.single('IDONOTEXIST', datetime.date(2009, 2, 13))
        self.assertEqual(e, None)

    def testSinglePresent(self):
        e = Entry.single('sample', datetime.date(2009, 2, 13))
        self.assertEqual(e, e1)
        e = Entry.single('loren-ipsum', datetime.date(2009, 2, 17))
        self.assertEqual(e, e2)

    def testSingleSlugInvalid(self):
        self.assertRaises(ValueError,
            Entry.single, 's@mpl3', datetime.date(2009, 2, 13))

    def testSingleNoStrftime(self):
        # List does not have strftime method
        self.assertRaises(ValueError, Entry.single, 'sample', list())

    def testDayEmpty(self):
        e = Entry.day('2009', '01', '09')
        self.assertEqual(len(e), 0)

    def testDayPresent(self):
        e = Entry.day('2009', '02', '13')
        self.assertEqual(1, len(e))
        self.assertEqual(e[0], e1)

    def testDayInvalidDate(self):
        self.assertRaises(ValueError, Entry.day, 2009, 0, 0)

    def testDateTrunc(self):
        self.assertRaises(ValueError, Entry._date_trunc, 'foo', 2009, 2, 13)

    def testMonthEmpty(self):
        e = Entry.month('2009', '01')
        self.assertEqual(len(e), 0)

    def testMonthPresent(self):
        e = Entry.month('2009', '02')
        self.assertEqual(2, len(e))
        self.assertEqual(e[0], e2)
        self.assertEqual(e[1], e1)

    def testYearEmpty(self):
        e = Entry.year('2008')
        self.assertEqual(len(e), 0)

    def testYearPresent(self):
        e = Entry.year('2009')
        self.assertEqual(4, len(e))
        self.assertEqual(e[0], e4)
        self.assertEqual(e[1], e3)
        self.assertEqual(e[2], e2)
        self.assertEqual(e[3], e1)

    def testRecentPresent(self):
        e = Entry.recent()
        self.assertEqual(4, len(e))
        self.assertEqual(e[0], e4)
        self.assertEqual(e[1], e3)
        self.assertEqual(e[2], e2)
        self.assertEqual(e[3], e1)

    def testRecentEmpty(self):
        e = Entry.recent(datetime.datetime.min)
        self.assertEqual(e, [])

    def testForFeedEmpty(self):
        self.assertEqual([], Entry.for_feed('Idon_tExist'))

    def testForFeedPresent(self):
        results = Entry.for_feed('general')
        self.assertEqual([e2, e1], results)


suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAtomSchema))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEntry))
