import unittest
import datetime
import pytz

from firmant.datasource.atom import AtomProvider, \
                                    AtomBase, \
                                    DatetimeFilter, \
                                    AtomObjectFilter, \
                                    Author, \
                                    Category, \
                                    Entry, \
                                    Feed
from firmant.utils import ProxyObject, \
                          not_implemented


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


# Defined Categories
categories = {}
categories['General']       = Category()
categories['General'].term  = 'General'
categories['General'].label = 'All topics'
categories['Generated']       = Category()
categories['Generated'].term  = 'Generated'
categories['Generated'].label = "You can't tell a computer wrote it."


A_NY = pytz.timezone('America/New_York')


# Defined Entries
entries = {}
entries['2009-02-13-sample'] = Entry()
entries['2009-02-13-sample'].slug      = 'sample'
entries['2009-02-13-sample'].published = \
        A_NY.localize(datetime.datetime(2009, 2, 13, 23, 31, 30))
entries['2009-02-13-sample'].author    = authors['Robert Escriva']
entries['2009-02-13-sample'].category  = categories['General']
entries['2009-02-13-sample'].rights    = 'Same as source.'
entries['2009-02-13-sample'].updated   = \
        A_NY.localize(datetime.datetime(2009, 2, 13, 23, 31, 31))
entries['2009-02-13-sample'].title     = 'Unix 1234567890'
entries['2009-02-13-sample'].content   = \
        'This is the main content of revision two.'
entries['2009-02-13-sample'].summary   = 'This is the summary of revision two.'
entries['2009-02-13-sample'].tz        = 'America/New_York'

entries['2009-02-17-loren-ipsum'] = Entry()
entries['2009-02-17-loren-ipsum'].slug      = 'loren-ipsum'
entries['2009-02-17-loren-ipsum'].published = \
        A_NY.localize(datetime.datetime(2009, 2, 17, 11, 31, 30))
entries['2009-02-17-loren-ipsum'].author    = authors['Loren Ipsum Generator']
entries['2009-02-17-loren-ipsum'].category  = categories['Generated']
entries['2009-02-17-loren-ipsum'].rights    = 'Same as source.'
entries['2009-02-17-loren-ipsum'].updated   = \
        A_NY.localize(datetime.datetime(2009, 2, 17, 11, 31, 30))
entries['2009-02-17-loren-ipsum'].title     = 'Loren Ipsum ...'
entries['2009-02-17-loren-ipsum'].content   = \
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
nunc."""
entries['2009-02-17-loren-ipsum'].summary   = \
        'A generated loren ipsum paragraph.'
entries['2009-02-17-loren-ipsum'].tz        = 'America/New_York'

entries['2009-03-17-sample'] = Entry()
entries['2009-03-17-sample'].slug      = 'sample'
entries['2009-03-17-sample'].published = \
        A_NY.localize(datetime.datetime(2009, 3, 17, 16, 31, 30))
entries['2009-03-17-sample'].author    = authors['Loren Ipsum Generator']
entries['2009-03-17-sample'].category  = categories['Generated']
entries['2009-03-17-sample'].rights    = 'Same as source.'
entries['2009-03-17-sample'].updated   = \
        A_NY.localize(datetime.datetime(2009, 3, 17, 11, 31, 30))
entries['2009-03-17-sample'].title     = 'Loren Ipsum ...'
entries['2009-03-17-sample'].content   = \
        'This is the main content of revision one.'
entries['2009-03-17-sample'].summary   = 'This is the summary of revision one.'
entries['2009-03-17-sample'].tz        = 'America/New_York'

entries['2009-03-29-markdown'] = Entry()
entries['2009-03-29-markdown'].slug      = 'markdown'
entries['2009-03-29-markdown'].published = \
        A_NY.localize(datetime.datetime(2009, 3, 29, 10, 52, 54))
entries['2009-03-29-markdown'].author    = authors['Robert Escriva']
entries['2009-03-29-markdown'].category  = categories['General']
entries['2009-03-29-markdown'].rights    = 'Same as source.'
entries['2009-03-29-markdown'].updated   = \
        A_NY.localize(datetime.datetime(2009, 3, 29, 10, 53, 26))
entries['2009-03-29-markdown'].title     = 'A sample markdown implementation'
entries['2009-03-29-markdown'].content   = \
'''Firmant Markdown Test
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
entries['2009-03-29-markdown'].summary   = 'Some markdown and a forkbomb.'
entries['2009-03-29-markdown'].tz        = 'America/New_York'


e1 = entries['2009-02-13-sample']
e2 = entries['2009-02-17-loren-ipsum']
e3 = entries['2009-03-17-sample']
e4 = entries['2009-03-29-markdown']


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


class TestCategory(unittest.TestCase):

    def setUp(self):
        """The setup function should alias the AtomProvider class to
        self.provider so that the test functions can access it.  It also must
        setup whatever data is necessary for the test cases to run."""
        not_implemented()

    def configuration(self, name):
        """This function should return the settings associated with test
        'name'"""
        not_implemented()

    def testByTerm1(self):
        """firmant.datasource.atom.Category.by_term
        Load a valid atom Category object using the by_term function"""
        settings = self.configuration('ByTerm1')
        expected = categories['General']

        provider = self.provider(settings)
        category = provider.category

        self.assertEqual(expected, category.by_term('General'))

    def testByTerm2(self):
        """firmant.datasource.atom.Category.by_term
        No such Category object using the by_term function"""
        settings = self.configuration('ByTerm2')
        expected = None

        provider = self.provider(settings)
        category = provider.category

        self.assertEqual(expected, category.by_term('NOEXIST'))


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
