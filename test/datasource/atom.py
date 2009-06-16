import unittest
import datetime
import pytz

from firmant.datasource.atom import AtomProvider, \
                                    AtomBase, \
                                    DatetimeFilter, \
                                    AtomObjectFilter, \
                                    Author
from firmant.utils import ProxyObject, \
                          not_implemented


A_NY = pytz.timezone('America/New_York')


# Defined Authors.
authors = {}
authors['Robert Escriva']       = Author()
authors['Robert Escriva'].name  = 'Robert Escriva'
authors['Robert Escriva'].uri   = 'http://robescriva.com'
authors['Robert Escriva'].email = 'rob@example.org'
authors['Loren Ipsum Generator']       = Author()
authors['Loren Ipsum Generator'].name  = 'Loren Ipsum Generator'
authors['Loren Ipsum Generator'].uri   = 'http://www.lipsum.com'
authors['Loren Ipsum Generator'].email = 'lipsum@example.org'


def generate_e1(entry):
    e1 = entry()
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
    return e1


def generate_e2(entry):
    e2 = entry()
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
    return e2


def generate_e3(entry):
    e3 = entry()
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
    return e3


def generate_e4(entry):
    e4 = entry()
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
    return e4


e1 = ProxyObject(lambda: generate_e1(AtomProvider.entry))
e2 = ProxyObject(lambda: generate_e2(AtomProvider.entry))
e3 = ProxyObject(lambda: generate_e3(AtomProvider.entry))
e4 = ProxyObject(lambda: generate_e4(AtomProvider.entry))


class TestAtomBase(unittest.TestCase):

    def setUp(self):
        class TestAtomData(AtomBase):
            fields    = ['foo', 'bar', 'baz', 'quux']
            __slots__ = fields

        self.cls = TestAtomData

    def testEquality1(self):
        """firmant.datasource.atom.AtomBase.__eq__
        This tests the case that all defined fields are present and equivalent,
        thus the two instances are equal"""

        a      = self.cls()
        a.foo  = 'quux'
        a.bar  = 'baz'
        a.baz  = 'bar'
        a.quux = 'foo'

        b      = self.cls()
        b.foo  = 'quux'
        b.bar  = 'baz'
        b.baz  = 'bar'
        b.quux = 'foo'

        self.assertTrue(a == b)

    def testEquality2(self):
        """firmant.datasource.atom.AtomBase.__eq__
        This tests the case that one or more defined fields are absent, but
        those absent are absent in both instances and those present have
        equivalent values, thus the two instances are equal"""

        a      = self.cls()
        a.foo  = 'quux'
        a.bar  = 'baz'
        a.quux = 'foo'

        b      = self.cls()
        b.foo  = 'quux'
        b.bar  = 'baz'
        b.quux = 'foo'

        self.assertTrue(a == b)

    def testEquality3(self):
        """firmant.datasource.atom.AtomBase.__eq__
        This tests the case that all defined fields are absent, thus the two
        instances are equal"""
        a      = self.cls()
        b      = self.cls()
        self.assertTrue(a == b)

    def testEquality4(self):
        """firmant.datasource.atom.AtomBase.__eq__
        This tests the case that that the same fields are present in both
        instances, but have unequal values.  Thus it is the case that the two
        instances are not equal."""

        a      = self.cls()
        a.foo  = 'quux'

        b      = self.cls()
        b.foo  = 'foo'

        self.assertTrue(not (a == b))

    def testEquality5(self):
        """firmant.datasource.atom.AtomBase.__eq__
        This tests the case that that different fields are present in both
        instances, but have equal values where they overlap.  Thus it is the
        case that the two instances are not equal."""

        a      = self.cls()
        a.foo  = 'foo'
        a.bar  = 'bar'
        a.baz  = 'baz'
        a.quux = 'quux'

        b      = self.cls()
        b.foo  = 'foo'
        b.bar  = 'bar'
        b.baz  = 'baz'

        self.assertTrue(not (a == b))
        self.assertTrue(not (b == a))

    def testInequality1(self):
        """firmant.datasource.atom.AtomBase.__ne__
        This tests the __ne__ function with a simple case. where defined fields
        are the same and values of said fields are different."""

        a      = self.cls()
        a.foo  = 'foo'
        a.bar  = 'baz'
        a.baz  = 'bar'
        a.quux = 'foo'

        b      = self.cls()
        b.foo  = 'quux'
        b.bar  = 'baz'
        b.baz  = 'bar'
        b.quux = 'foo'

        self.assertTrue(a != b)

    def testJson1(self):
        """firmant.datasource.atom.AtomBase. to_json, from_json
        Test JSON serialization with all fields present"""

        a      = self.cls()
        a.foo  = 'quux'
        a.bar  = 'baz'
        a.baz  = 'bar'
        a.quux = 'foo'

        j = a.to_json()
        b = self.cls.from_json(j)

        self.assertTrue(a == b)

    def testJson2(self):
        """firmant.datasource.atom.AtomBase. to_json, from_json
        Test JSON serialization with just one field present"""

        a      = self.cls()
        a.foo  = 'quux'

        j = a.to_json()
        b = self.cls.from_json(j)

        self.assertTrue(a == b)

    def testJson3(self):
        """firmant.datasource.atom.AtomBase. to_json, from_json
        Test JSON serialization with no fields present"""

        a      = self.cls()

        j = a.to_json()
        b = self.cls.from_json(j)

        self.assertTrue(a == b)


class TestDatetimeFilter(unittest.TestCase):

    def setUp(self):
        class TestData(AtomBase):
            fields    = ['foo', 'bar', 'baz', 'quux']
            __slots__ = fields
            filters = {}
            filters['quux'] = DatetimeFilter()

        self.cls = TestData

    def testDatetimeFilter1(self):
        """firmant.datasource.atom.DatetimeFilter
        Test serialization to JSON of an AtomBase object with a pytz localized
        datetime object in one field.  The datetime object observes daylight
        savings time."""

        a      = self.cls()
        A_NY   = pytz.timezone('America/New_York')
        a.quux = A_NY.localize(datetime.datetime(2009, 6, 15, 14, 40, 59))

        j = a.to_json()
        b = self.cls.from_json(j)

        self.assertTrue(a == b)

    def testDatetimeFilter2(self):
        """firmant.datasource.atom.DatetimeFilter
        Test serialization to JSON of an AtomBase object with a pytz localized
        datetime object in one field.  The datetime object is outside daylight
        savings time"""

        a      = self.cls()
        A_NY   = pytz.timezone('America/New_York')
        a.quux = A_NY.localize(datetime.datetime(2009, 1, 15, 14, 40, 59))

        j = a.to_json()
        b = self.cls.from_json(j)

        self.assertTrue(a == b)

    def testDatetimeFilter3(self):
        """firmant.datasource.atom.DatetimeFilter
        Test serialization to JSON of an AtomBase object with a naive datetime
        object in one field."""

        a      = self.cls()
        a.quux = datetime.datetime(2009, 6, 15, 14, 40, 59)

        j = a.to_json()
        b = self.cls.from_json(j)

        self.assertTrue(a == b)


class TestAtomObjectFilter(unittest.TestCase):

    def setUp(self):
        class TestData(AtomBase):
            fields    = ['foo', 'bar', 'baz', 'quux']
            __slots__ = fields

        class MoreTestData(TestData):
            filters = {}
            filters['quux'] = AtomObjectFilter(TestData)

        self.filtered   = MoreTestData
        self.unfiltered = TestData

    def testAtomObjectFilter1(self):
        """firmant.datasource.atom.AtomObjectFilter
        Test serialization to JSON of a
        Test serialization to JSON of naive datetime object."""

        a      = self.unfiltered()
        a.foo  = 'quux'
        b      = self.filtered()
        b.quux = a

        j = b.to_json()
        c = self.filtered.from_json(j)

        self.assertTrue(b == c)


class TestAuthor(unittest.TestCase):

    def setUp(self):
        """The setup function should alias the AtomProvider class to
        self.provider so that the test functions can access it.  It also must
        setup whatever data is necessary for the test cases to run."""
        not_implemented()

    def configuration(self, name):
        """This function should return the settings associated with test
        'name'"""
        not_implemented()

    def testByName1(self):
        """firmant.datasource.atom.Author.by_name
        Load a valid atom Author object using the by_name function"""
        settings = self.configuration('ByName1')
        expected = authors['Robert Escriva']

        provider = self.provider(settings)
        author   = provider.author

        self.assertEqual(expected, author.by_name('Robert Escriva'))

    def testByName2(self):
        """firmant.datasource.atom.Author.by_name
        No such Author object using the by_name function"""
        settings = self.configuration('ByName2')
        expected = None

        provider = self.provider(settings)
        author   = provider.author

        self.assertEqual(expected, author.by_name('Jane Doe'))


class TestEntry(unittest.TestCase):

    def setUp(self):
        raise NotImplemented("Implement implement setUp")

    def tearDown(self):
        raise NotImplemented("Implement implement tearDown")

    def loadData(self):
        raise NotImplemented("Implement implement loadData")

    def testSingleEmpty(self):
        e = self.Entry.single('IDONOTEXIST', datetime.date(2009, 2, 13))
        self.assertEqual(e, None)

    def testSinglePresent(self):
        e = self.Entry.single('sample', datetime.date(2009, 2, 13))
        self.assertEqual(e, self.e1)
        e = self.Entry.single('loren-ipsum', datetime.date(2009, 2, 17))
        self.assertEqual(e, self.e2)

    def testSingleSlugInvalid(self):
        self.assertRaises(ValueError,
            self.Entry.single, 's@mpl3', datetime.date(2009, 2, 13))

    def testSingleNoStrftime(self):
        # List does not have strftime method
        self.assertRaises(ValueError, self.Entry.single, 'sample', list())

    def testDayEmpty(self):
        e = self.Entry.day('2009', '01', '09')
        self.assertEqual(e, [])

    def testDayPresent(self):
        e = self.Entry.day('2009', '02', '13')
        self.assertEqual(e, [self.e1])

    def testDayInvalidDate(self):
        self.assertRaises(ValueError, self.Entry.day, 2009, 0, 0)

    def testMonthEmpty(self):
        e = self.Entry.month('2009', '01')
        self.assertEqual(e, [])

    def testMonthPresent(self):
        e = self.Entry.month('2009', '02')
        self.assertEqual(e, [self.e2, self.e1])

    def testYearEmpty(self):
        e = self.Entry.year('2008')
        self.assertEqual(e, [])

    def testYearPresent(self):
        e = self.Entry.year('2009')
        self.assertEqual(e, [self.e4, self.e3, self.e2, self.e1])

    def testRecentPresent(self):
        e = self.Entry.recent()
        self.assertEqual(e, [self.e4, self.e3, self.e2, self.e1])

    def testRecentEmpty(self):
        e = self.Entry.recent(datetime.datetime.min)
        self.assertEqual(e, [])

    def testForFeedEmpty(self):
        self.assertEqual([], self.Entry.for_feed('Idon_tExist'))

    def testForFeedPresent(self):
        results = self.Entry.for_feed('general')
        self.assertEqual([self.e2, self.e1], results)


suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAtomBase))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAtomObjectFilter))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDatetimeFilter))
