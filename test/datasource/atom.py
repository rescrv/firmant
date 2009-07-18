import unittest
import datetime
import os
import pytz

from firmant.datasource.atom import AtomProvider, \
                                    AtomBase, \
                                    DatetimeFilter, \
                                    AtomObjectFilter, \
                                    AtomObjectListFilter, \
                                    Author, \
                                    Category, \
                                    Entry, \
                                    Feed, \
                                    EntryPermalinkProvider, \
                                    FeedPermalinkProvider
from firmant.utils import not_implemented, \
                          xml, \
                          RFC3339


# Defined Authors.
authors = {}
authors['Robert Escriva']       = Author()
authors['Robert Escriva'].name  = u'Robert Escriva'
authors['Robert Escriva'].uri   = u'http://robescriva.com'
authors['Robert Escriva'].email = u'rob@example.org'
authors['Loren Ipsum Generator']       = Author()
authors['Loren Ipsum Generator'].name  = u'Loren Ipsum Generator'
authors['Loren Ipsum Generator'].uri   = u'http://www.lipsum.com'
authors['Loren Ipsum Generator'].email = u'lipsum@example.org'


# Defined Categories
categories = {}
categories['General']       = Category()
categories['General'].term  = u'General'
categories['General'].label = u'All topics'
categories['Generated']       = Category()
categories['Generated'].term  = u'Generated'
categories['Generated'].label = u"You can't tell a computer wrote it."


A_NY = pytz.timezone('America/New_York')


# Defined Entries
entries = {}
entries['2009-02-13-sample'] = Entry()
entries['2009-02-13-sample'].slug      = u'sample'
entries['2009-02-13-sample'].published = \
        A_NY.localize(datetime.datetime(2009, 2, 13, 23, 31, 30))
entries['2009-02-13-sample'].author    = authors['Robert Escriva']
entries['2009-02-13-sample'].category  = categories['General']
entries['2009-02-13-sample'].rights    = u'Same as source.\n'
entries['2009-02-13-sample'].updated   = \
        A_NY.localize(datetime.datetime(2009, 2, 13, 23, 31, 31))
entries['2009-02-13-sample'].title     = u'Unix 1234567890'
entries['2009-02-13-sample'].content   = \
        u'This is the main content of revision two.\n'
entries['2009-02-13-sample'].summary   = u'This is the summary of revision two.\n'
entries['2009-02-13-sample'].tz        = u'America/New_York'

entries['2009-02-17-loren-ipsum'] = Entry()
entries['2009-02-17-loren-ipsum'].slug      = u'loren-ipsum'
entries['2009-02-17-loren-ipsum'].published = \
        A_NY.localize(datetime.datetime(2009, 2, 17, 11, 31, 30))
entries['2009-02-17-loren-ipsum'].author    = authors['Loren Ipsum Generator']
entries['2009-02-17-loren-ipsum'].category  = categories['Generated']
entries['2009-02-17-loren-ipsum'].rights    = u'Same as source.\n'
entries['2009-02-17-loren-ipsum'].updated   = \
        A_NY.localize(datetime.datetime(2009, 2, 17, 11, 31, 30))
entries['2009-02-17-loren-ipsum'].title     = u'Loren Ipsum ...'
entries['2009-02-17-loren-ipsum'].content   = \
u"""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus eget
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
nunc.\n"""
entries['2009-02-17-loren-ipsum'].summary   = \
        u'A generated loren ipsum paragraph.\n'
entries['2009-02-17-loren-ipsum'].tz        = u'America/New_York'

entries['2009-03-17-sample'] = Entry()
entries['2009-03-17-sample'].slug      = u'sample'
entries['2009-03-17-sample'].published = \
        A_NY.localize(datetime.datetime(2009, 3, 17, 16, 31, 30))
entries['2009-03-17-sample'].author    = authors['Loren Ipsum Generator']
entries['2009-03-17-sample'].category  = categories['Generated']
entries['2009-03-17-sample'].rights    = u'Same as source.\n'
entries['2009-03-17-sample'].updated   = \
        A_NY.localize(datetime.datetime(2009, 3, 17, 11, 31, 30))
entries['2009-03-17-sample'].title     = u'Loren Ipsum ...'
entries['2009-03-17-sample'].content   = \
        u'This is the main content of revision one.\n'
entries['2009-03-17-sample'].summary   = u'This is the summary of revision one.\n'
entries['2009-03-17-sample'].tz        = u'America/New_York'

entries['2009-03-29-markdown'] = Entry()
entries['2009-03-29-markdown'].slug      = u'markdown'
entries['2009-03-29-markdown'].published = \
        A_NY.localize(datetime.datetime(2009, 3, 29, 10, 52, 54))
entries['2009-03-29-markdown'].author    = authors['Robert Escriva']
entries['2009-03-29-markdown'].category  = categories['General']
entries['2009-03-29-markdown'].rights    = u'Same as source.\n'
entries['2009-03-29-markdown'].updated   = \
        A_NY.localize(datetime.datetime(2009, 3, 29, 10, 53, 26))
entries['2009-03-29-markdown'].title     = u'A sample markdown implementation'
entries['2009-03-29-markdown'].content   = \
u'''Firmant Markdown Test
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

See?  Wasn't that easy?\n'''
entries['2009-03-29-markdown'].summary   = u'Some markdown and a forkbomb.\n'
entries['2009-03-29-markdown'].tz        = u'America/New_York'


# Defined Feeds

feeds = {}
feeds['general'] = Feed()
feeds['general'].slug     = u"general"
feeds['general'].title    = u"General Content"
feeds['general'].rights   = u"Same as source.\n"
feeds['general'].subtitle = u"This is a feed that holds general content"
feeds['general'].updated  = \
        A_NY.localize(datetime.datetime(2009, 2, 17, 11, 31, 30))
feeds['general'].entries  = [entries['2009-02-17-loren-ipsum'],
                             entries['2009-02-13-sample']]

feeds['empty'] = Feed()
feeds['empty'].slug       = u"empty"
feeds['empty'].title      = u"An Empty Feed"
feeds['empty'].rights     = u"Same as source.\n"
feeds['empty'].subtitle   = u"This feed has no entries."
feeds['empty'].updated    = datetime.datetime.min
feeds['empty'].entries    = []

feeds['default'] = Feed()
feeds['default'].slug     = u""
feeds['default'].title    = u"Firmant Atom Feed"
feeds['default'].rights   = u"Same as source."
feeds['default'].subtitle = u"The default atom feed"
feeds['default'].updated  = \
        A_NY.localize(datetime.datetime(2009, 3, 29, 10, 53, 26))
feeds['default'].entries  = [entries['2009-03-29-markdown'],
                             entries['2009-03-17-sample'],
                             entries['2009-02-17-loren-ipsum'],
                             entries['2009-02-13-sample']]


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


class TestAtomObjectListFilter(unittest.TestCase):

    def setUp(self):
        class TestData(AtomBase):
            fields    = ['foo', 'bar', 'baz', 'quux']
            __slots__ = fields

        class MoreTestData(TestData):
            filters = {}
            filters['quux'] = AtomObjectListFilter(TestData)

        self.filtered   = MoreTestData
        self.unfiltered = TestData

    def testAtomObjectFilter1(self):
        """firmant.datasource.atom.AtomObjectListFilter
        Test serialization to JSON of an object with a list of AtomObjects."""

        a      = self.unfiltered()
        a.foo  = 'quux'
        b      = self.unfiltered()
        b.bar  = 'bar'
        c      = self.filtered()
        c.quux = [a, b]

        j = c.to_json()
        d = self.filtered.from_json(j)

        self.assertTrue(c == d)


class TestAuthor(unittest.TestCase):

    def setUp(self):
        """Setup all data necessary for test case."""
        not_implemented() # pragma: no cover

    def get_provider(self, name):
        """This function should return the AtomProvider for the test."""
        not_implemented() # pragma: no cover

    def testByName1(self):
        """firmant.datasource.atom.Author.by_name
        Load a valid atom Author object using the by_name function"""
        provider = self.get_provider('ByName1')

        expected = authors['Robert Escriva']
        returned = provider.author.by_name('Robert Escriva')

        self.assertEqual(expected, returned)

    def testByName2(self):
        """firmant.datasource.atom.Author.by_name
        No such Author object using the by_name function"""
        provider = self.get_provider('ByName2')

        expected = None
        returned = provider.author.by_name('Jane Doe')

        self.assertEqual(expected, returned)

    def testToXML1(self):
        """firmant.datasource.atom.Author.to_xml
        Convert author 'Robert Escriva' to xml"""
        provider = self.get_provider('ToXML1')

        author   = xml.etree.Element('author')
        xml.add_text_subelement(author, 'name', 'Robert Escriva')
        xml.add_text_subelement(author, 'uri', 'http://robescriva.com')
        xml.add_text_subelement(author, 'email', 'rob@example.org')

        expected = xml.etree.tostring(author)
        returned = xml.etree.tostring(authors['Robert Escriva'].to_xml())

        self.assertEqual(expected, returned)

    def testToXML2(self):
        """firmant.datasource.atom.Author.to_xml
        Convert author 'Loren Ipsum Generator' to xml"""
        provider = self.get_provider('ToXML2')

        author   = xml.etree.Element('author')
        xml.add_text_subelement(author, 'name', 'Loren Ipsum Generator')
        xml.add_text_subelement(author, 'uri', 'http://www.lipsum.com')
        xml.add_text_subelement(author, 'email', 'lipsum@example.org')

        expected = xml.etree.tostring(author)
        returned = xml.etree.tostring(authors['Loren Ipsum Generator'].to_xml())

        self.assertEqual(expected, returned)


class TestCategory(unittest.TestCase):

    def setUp(self):
        """The setup function should alias the AtomProvider class to
        self.provider so that the test functions can access it.  It also must
        setup whatever data is necessary for the test cases to run."""
        not_implemented() # pragma: no cover

    def get_provider(self, name):
        """This function should return the AtomProvider for the test."""
        not_implemented() # pragma: no cover

    def testByTerm1(self):
        """firmant.datasource.atom.Category.by_term
        Load a valid atom Category object using the by_term function"""
        provider = self.get_provider('ByTerm1')

        expected = categories['General']
        returned = provider.category.by_term('General')

        self.assertEqual(expected, returned)

    def testByTerm2(self):
        """firmant.datasource.atom.Category.by_term
        No such Category object using the by_term function"""
        provider = self.get_provider('ByTerm2')

        expected = None
        returned = provider.category.by_term('NOEXIST')

        self.assertEqual(expected, returned)

    def testToXML1(self):
        """firmant.datasource.atom.Category.to_xml
        Convert category 'General' to xml"""
        provider = self.get_provider('ToXML1')

        category = xml.etree.Element('category')
        category.set('term', 'General')
        category.set('label', 'All topics')

        expected = xml.etree.tostring(category)
        returned = xml.etree.tostring(categories['General'].to_xml())

        self.assertEqual(expected, returned)

    def testToXML2(self):
        """firmant.datasource.atom.Category.to_xml
        Convert category 'Generated' to xml"""
        provider = self.get_provider('ToXML2')

        category = xml.etree.Element('category')
        category.set('term', 'Generated')
        category.set('label', 'You can\'t tell a computer wrote it.')

        expected = xml.etree.tostring(category)
        returned = xml.etree.tostring(categories['Generated'].to_xml())

        self.assertEqual(expected, returned)


class TestEntry(unittest.TestCase):

    def setUp(self):
        """The setup function should alias the AtomProvider class to
        self.provider so that the test functions can access it.  It also must
        setup whatever data is necessary for the test cases to run."""
        not_implemented() # pragma: no cover

    def get_provider(self, name):
        """This function should return the AtomProvider for the test."""
        not_implemented() # pragma: no cover

    def testForFeed1(self):
        """firmant.datasource.atom.Entry.for_feed
        The entries associated with a valid feed should be returned."""
        provider = self.get_provider('ForFeed1')
        entry    = provider.entry

        expected = [entries['2009-02-17-loren-ipsum'],
                    entries['2009-02-13-sample']]
        returned = entry.for_feed('general')

        self.assertEqual(expected, returned)

    def testForFeed2(self):
        """firmant.datasource.atom.Entry.for_feed
        None should be returned for an invalid feed."""
        provider = self.get_provider('ForFeed2')
        entry    = provider.entry

        expected = None
        returned = entry.for_feed('noexist')

        self.assertEqual(expected, returned)

    def testForFeed3(self):
        """firmant.datasource.atom.Entry.for_feed
        When pagination parameters provided, we get different results."""
        provider = self.get_provider('ForFeed3')
        entry    = provider.entry

        expected = ([entries['2009-02-17-loren-ipsum']], 1)
        returned = entry.for_feed('general', limit=1, offset=0)

        self.assertEqual(expected, returned)

    def testForFeed4(self):
        """firmant.datasource.atom.Entry.for_feed
        If we overrun the end, there is no results, and none remaining."""
        provider = self.get_provider('ForFeed4')
        entry    = provider.entry

        expected = (None, 0)
        returned = entry.for_feed('general', limit=1, offset=2)

        self.assertEqual(expected, returned)

    def testForFeed5(self):
        """firmant.datasource.atom.Entry.for_feed
        We test the offset for the for_feed method."""
        provider = self.get_provider('ForFeed5')
        entry    = provider.entry

        expected = ([entries['2009-02-13-sample']], 0)
        returned = entry.for_feed('general', limit=1, offset=1)

        self.assertEqual(expected, returned)

    def testForFeed6(self):
        """firmant.datasource.atom.Entry.for_feed
        Test that a limit of 0 returns a list if the offset is not too high."""
        provider = self.get_provider('ForFeed6')
        entry    = provider.entry

        expected = ([], 2)
        returned = entry.for_feed('general', limit=0, offset=0)

        self.assertEqual(expected, returned)

    def testForFeed7(self):
        """firmant.datasource.atom.Entry.for_feed
        Test that limit cannot be negative."""
        provider = self.get_provider('ForFeed7')
        entry    = provider.entry

        raises   = ValueError
        function = lambda: entry.for_feed('general', limit=-1, offset=0)

        self.assertRaises(raises, function)

    def testForFeed8(self):
        """firmant.datasource.atom.Entry.for_feed
        Test that offset cannot be negative."""
        provider = self.get_provider('ForFeed8')
        entry    = provider.entry

        raises   = ValueError
        function = lambda: entry.for_feed('general', limit=0, offset=-1)

        self.assertRaises(raises, function)

    def testForFeed9(self):
        """firmant.datasource.atom.Entry.for_feed
        Test that an unspecified offset is equivalent to 0."""
        provider = self.get_provider('ForFeed9')
        entry    = provider.entry

        expected = ([entries['2009-02-17-loren-ipsum']], 1)
        returned = entry.for_feed('general', limit=1)

        self.assertEqual(expected, returned)

    def testForFeed10(self):
        """firmant.datasource.atom.Entry.for_feed
        Test that an unspecified limit is equivalent to the set value of
        JINJA2_ENTRIES_PER_PAGE."""
        provider = self.get_provider('ForFeed10')
        entry    = provider.entry

        expected = ([entries['2009-02-17-loren-ipsum'],
                     entries['2009-02-13-sample']], 0)
        returned = entry.for_feed('general', offset=0)

        self.assertEqual(expected, returned)

    def testForFeed11(self):
        """firmant.datasource.atom.Entry.single
        A ValueError should be raised for invalid slug."""
        provider = self.get_provider('ForFeed11')
        entry    = provider.entry

        raises   = ValueError
        function = lambda: entry.for_feed('s@mpl3')

        self.assertRaises(raises, function)

    def testSingle1(self):
        """firmant.datasource.atom.Entry.single
        A valid entry should be returned for the given date."""
        provider = self.get_provider('Single1')
        entry    = provider.entry

        expected = entries['2009-02-13-sample']
        returned = entry.single('sample', 2009, 2, 13)

        self.assertEqual(expected, returned)

    def testSingle2(self):
        """firmant.datasource.atom.Entry.single
        A valid entry should be returned for the given date."""
        provider = self.get_provider('Single2')
        entry    = provider.entry

        expected = entries['2009-02-17-loren-ipsum']
        returned = entry.single('loren-ipsum', '2009', '2', '17')

        self.assertEqual(expected, returned)

    def testSingle3(self):
        """firmant.datasource.atom.Entry.single
        None should be returned for a non-existent entry."""
        provider = self.get_provider('Single3')
        entry    = provider.entry

        expected = None
        returned = entry.single('IDONOTEXIST', 2009, 2, 13)

        self.assertEqual(expected, returned)

    def testSingle4(self):
        """firmant.datasource.atom.Entry.single
        A ValueError should be raised for invalid slug."""
        provider = self.get_provider('Single4')
        entry    = provider.entry

        raises   = ValueError
        function = lambda: entry.single('s@mpl3', 2009, 2, 13)

        self.assertRaises(raises, function)

    def testSingle5(self):
        """firmant.datasource.atom.Entry.single
        A ValueError should be raised for invalid datetime."""
        provider = self.get_provider('Single5')
        entry    = provider.entry

        raises   = ValueError
        function = lambda: entry.single('sample', 2009, 'a', 15)

        self.assertRaises(raises, function)

    def testSingle6(self):
        """firmant.datasource.atom.Entry.single
        A ValueError should be raised for invalid datetime."""
        provider = self.get_provider('Single6')
        entry    = provider.entry

        raises   = ValueError
        function = lambda: entry.single('sample', 2009, 13, 15)

        self.assertRaises(raises, function)

    def testDay1(self):
        """firmant.datasource.atom.Entry.day
        A valid list of entries for a given day should be returned."""
        provider = self.get_provider('Day1')
        entry    = provider.entry

        expected = [entries['2009-02-13-sample']]
        returned = entry.day('2009', '02', '13')

        self.assertEqual(expected, returned)

    def testDay2(self):
        """firmant.datasource.atom.Entry.day
        An empty list for a day for which there are no entries."""
        provider = self.get_provider('Day2')
        entry    = provider.entry

        expected = []
        returned = entry.day('2009', '01', '09')

        self.assertEqual(expected, returned)

    def testDay3(self):
        """firmant.datasource.atom.Entry.day
        A ValueError should be raised for an invalid date."""
        provider = self.get_provider('Day3')
        entry    = provider.entry

        raises   = ValueError
        function = lambda: entry.day(2009, 0, 0)

        self.assertRaises(raises, function)

    def testDay4(self):
        """firmant.datasource.atom.Entry.day
        Test valid pagination."""
        provider = self.get_provider('Day4')
        entry    = provider.entry

        expected = ([entries['2009-02-13-sample']], 0)
        returned = entry.day('2009', '02', '13', limit=1, offset=0)

        self.assertEqual(expected, returned)

    def testDay5(self):
        """firmant.datasource.atom.Entry.day
        Test valid pagination."""
        provider = self.get_provider('Day5')
        entry    = provider.entry

        expected = ([], 1)
        returned = entry.day('2009', '02', '13', limit=0, offset=0)

        self.assertEqual(expected, returned)

    def testDay6(self):
        """firmant.datasource.atom.Entry.day
        Test valid termination of pagination."""
        provider = self.get_provider('Day6')
        entry    = provider.entry

        expected = (None, 0)
        returned = entry.day('2009', '02', '13', limit=1, offset=1)

        self.assertEqual(expected, returned)

    def testDay7(self):
        """firmant.datasource.atom.Entry.day
        Test that checks exist for sane values of limit/offset."""
        provider = self.get_provider('Day7')
        entry    = provider.entry

        raises   = ValueError
        function = lambda: entry.day('2009', '02', '13', limit=0, offset=-1)

        self.assertRaises(raises, function)

    def testDay8(self):
        """firmant.datasource.atom.Entry.day
        Test that checks exist for sane values of limit/offset."""
        provider = self.get_provider('Day8')
        entry    = provider.entry

        raises   = ValueError
        function = lambda: entry.day('2009', '02', '13', limit=-1, offset=0)

        self.assertRaises(raises, function)

    def testDay9(self):
        """firmant.datasource.atom.Entry.day
        An unspecified offset is equivalent to 0."""
        provider = self.get_provider('Day9')
        entry    = provider.entry

        expected = ([entries['2009-02-13-sample']], 0)
        returned = entry.day('2009', '02', '13', limit=1)

        self.assertEqual(expected, returned)

    def testDay10(self):
        """firmant.datasource.atom.Entry.day
        An unspecified limit is equivalent to the default."""
        provider = self.get_provider('Day10')
        entry    = provider.entry

        expected = ([entries['2009-02-13-sample']], 0)
        returned = entry.day('2009', '02', '13', offset=0)

        self.assertEqual(expected, returned)

    def testMonth1(self):
        """firmant.datasource.atom.Entry.month
        A list of entries for a month for which there are entries."""
        provider = self.get_provider('Month1')
        entry    = provider.entry

        expected = [entries['2009-02-17-loren-ipsum'],
                    entries['2009-02-13-sample']]
        returned = entry.month('2009', '02')

        self.assertEqual(expected, returned)

    def testMonth2(self):
        """firmant.datasource.atom.Entry.month
        An empty list for a month for which there are no entries."""
        provider = self.get_provider('Month2')
        entry    = provider.entry

        expected = []
        returned = entry.month('2009', '01')

        self.assertEqual(expected, returned)

    def testMonth3(self):
        """firmant.datasource.atom.Entry.month
        A ValueError should be raised for an invalid date."""
        provider = self.get_provider('Month3')
        entry    = provider.entry

        raises   = ValueError
        function = lambda: entry.month(2009, 0)

        self.assertRaises(raises, function)

    def testMonth4(self):
        """firmant.datasource.atom.Entry.month
        Test valid pagination."""
        provider = self.get_provider('Month4')
        entry    = provider.entry

        expected = ([entries['2009-02-17-loren-ipsum']], 1)
        returned = entry.month('2009', '02', limit=1, offset=0)

        self.assertEqual(expected, returned)

    def testMonth5(self):
        """firmant.datasource.atom.Entry.month
        Test valid pagination."""
        provider = self.get_provider('Month5')
        entry    = provider.entry

        expected = ([entries['2009-02-13-sample']], 0)
        returned = entry.month('2009', '02', limit=1, offset=1)

        self.assertEqual(expected, returned)

    def testMonth6(self):
        """firmant.datasource.atom.Entry.month
        Test valid pagination."""
        provider = self.get_provider('Month6')
        entry    = provider.entry

        expected = (None, 0)
        returned = entry.month('2009', '02', limit=1, offset=2)

        self.assertEqual(expected, returned)

    def testMonth7(self):
        """firmant.datasource.atom.Entry.month
        Test that checks exist for sane values of limit/offset."""
        provider = self.get_provider('Month7')
        entry    = provider.entry

        raises   = ValueError
        function = lambda: entry.month('2009', '02', limit=0, offset=-1)

        self.assertRaises(raises, function)

    def testMonth8(self):
        """firmant.datasource.atom.Entry.month
        Test that checks exist for sane values of limit/offset."""
        provider = self.get_provider('Month8')
        entry    = provider.entry

        raises   = ValueError
        function = lambda: entry.month('2009', '02', limit=-1, offset=0)

        self.assertRaises(raises, function)

    def testMonth9(self):
        """firmant.datasource.atom.Entry.month
        An unspecified offset is equivalent to 0."""
        provider = self.get_provider('Month9')
        entry    = provider.entry

        expected = ([entries['2009-02-17-loren-ipsum']], 1)
        returned = entry.month('2009', '02', limit=1)

        self.assertEqual(expected, returned)

    def testMonth10(self):
        """firmant.datasource.atom.Entry.month
        An unspecified limit is equivalent to the default."""
        provider = self.get_provider('Month10')
        entry    = provider.entry

        expected = ([entries['2009-02-17-loren-ipsum'],
                     entries['2009-02-13-sample']], 0)
        returned = entry.month('2009', '02', offset=0)

        self.assertEqual(expected, returned)

    def testYear1(self):
        """firmant.datasource.atom.Entry.year
        A list of entries should be returned for a year for which there are
        entries."""
        provider = self.get_provider('Year1')
        entry    = provider.entry

        expected = [entries['2009-03-29-markdown'],
                    entries['2009-03-17-sample'],
                    entries['2009-02-17-loren-ipsum'],
                    entries['2009-02-13-sample']]
        returned = entry.year('2009')

        self.assertEqual(expected, returned)

    def testYear2(self):
        """firmant.datasource.atom.Entry.year
        An empty list of entries should be returned for a year for which there
        are no entries."""
        provider = self.get_provider('Year2')
        entry    = provider.entry

        expected = []
        returned = entry.year('2008')

        self.assertEqual(expected, returned)

    def testYear3(self):
        """firmant.datasource.atom.Entry.year
        A ValueError should be raised for an invalid date."""
        provider = self.get_provider('Month3')
        entry    = provider.entry

        raises   = ValueError
        function = lambda: entry.year('abcd')

        self.assertRaises(raises, function)

    def testYear4(self):
        """firmant.datasource.atom.Entry.year
        Test valid pagination."""
        provider = self.get_provider('Year4')
        entry    = provider.entry

        expected = ([entries['2009-03-29-markdown'],
                    entries['2009-03-17-sample']], 2)
        returned = entry.year('2009', limit=2, offset=0)

        self.assertEqual(expected, returned)

    def testYear5(self):
        """firmant.datasource.atom.Entry.year
        Test valid pagination."""
        provider = self.get_provider('Year5')
        entry    = provider.entry

        expected = ([entries['2009-02-17-loren-ipsum'],
                    entries['2009-02-13-sample']], 0)
        returned = entry.year('2009', limit=2, offset=2)

        self.assertEqual(expected, returned)

    def testYear6(self):
        """firmant.datasource.atom.Entry.year
        Test valid pagination."""
        provider = self.get_provider('Year6')
        entry    = provider.entry

        expected = (None, 0)
        returned = entry.year('2009', limit=2, offset=4)

        self.assertEqual(expected, returned)

    def testYear7(self):
        """firmant.datasource.atom.Entry.year
        Test for sanity checks on limit."""
        provider = self.get_provider('Year7')
        entry    = provider.entry

        raises   = ValueError
        function = lambda: entry.year('2009', limit=-1, offset=0)

        self.assertRaises(raises, function)

    def testYear8(self):
        """firmant.datasource.atom.Entry.year
        Test for sanity checks on offset."""
        provider = self.get_provider('Year8')
        entry    = provider.entry

        raises   = ValueError
        function = lambda: entry.year('2009', limit=0, offset=-1)

        self.assertRaises(raises, function)

    def testYear9(self):
        """firmant.datasource.atom.Entry.year
        An unspecified offset is equivalent to 0."""
        provider = self.get_provider('Year9')
        entry    = provider.entry

        expected = ([entries['2009-03-29-markdown'],
                    entries['2009-03-17-sample']], 2)
        returned = entry.year('2009', limit=2)

        self.assertEqual(expected, returned)

    def testYear10(self):
        """firmant.datasource.atom.Entry.year
        An unspecified limit is equivalent to the default."""
        provider = self.get_provider('Year10')
        entry    = provider.entry

        expected = ([entries['2009-03-29-markdown'],
                    entries['2009-03-17-sample'],
                    entries['2009-02-17-loren-ipsum'],
                    entries['2009-02-13-sample']], 0)
        returned = entry.year('2009', offset=0)

        self.assertEqual(expected, returned)

    def testRecent1(self):
        """firmant.datasource.atom.Entry.recent
        A list of entries should be returned."""
        provider = self.get_provider('Recent1')
        entry    = provider.entry

        expected = [entries['2009-03-29-markdown'],
                    entries['2009-03-17-sample'],
                    entries['2009-02-17-loren-ipsum'],
                    entries['2009-02-13-sample']]
        returned = entry.recent()

        self.assertEqual(expected, returned)

    def testRecent2(self):
        """firmant.datasource.atom.Entry.recent
        A list of entries should be returned."""
        provider = self.get_provider('Recent2')
        entry    = provider.entry

        expected = ([entries['2009-03-29-markdown'],
                    entries['2009-03-17-sample']], 2)
        returned = entry.recent(limit=2, offset=0)

        self.assertEqual(expected, returned)

    def testRecent3(self):
        """firmant.datasource.atom.Entry.recent
        A list of entries should be returned."""
        provider = self.get_provider('Recent3')
        entry    = provider.entry

        expected = ([entries['2009-02-17-loren-ipsum'],
                    entries['2009-02-13-sample']], 0)
        returned = entry.recent(limit=2, offset=2)

        self.assertEqual(expected, returned)

    def testRecent4(self):
        """firmant.datasource.atom.Entry.recent
        A list of entries should be returned."""
        provider = self.get_provider('Recent4')
        entry    = provider.entry

        expected = (None, 0)
        returned = entry.recent(limit=2, offset=4)

        self.assertEqual(expected, returned)

    def testRecent5(self):
        """firmant.datasource.atom.Entry.recent
        Test for sanity checks on offset."""
        provider = self.get_provider('Recent5')
        entry    = provider.entry

        raises   = ValueError
        function = lambda: entry.recent(limit=0, offset=-1)

        self.assertRaises(raises, function)

    def testRecent6(self):
        """firmant.datasource.atom.Entry.recent
        Test for sanity checks on offset."""
        provider = self.get_provider('Recent6')
        entry    = provider.entry

        raises   = ValueError
        function = lambda: entry.recent(limit=-1, offset=0)

        self.assertRaises(raises, function)

    def testRecent7(self):
        """firmant.datasource.atom.Entry.recent
        An unspecified offset is 0."""
        provider = self.get_provider('Recent7')
        entry    = provider.entry

        expected = ([entries['2009-03-29-markdown'],
                    entries['2009-03-17-sample']], 2)
        returned = entry.recent(limit=2)

        self.assertEqual(expected, returned)

    def testRecent8(self):
        """firmant.datasource.atom.Entry.recent
        An unspecified limit is the default."""
        provider = self.get_provider('Recent8')
        entry    = provider.entry

        expected = ([entries['2009-03-29-markdown'],
                    entries['2009-03-17-sample'],
                    entries['2009-02-17-loren-ipsum'],
                    entries['2009-02-13-sample']], 0)
        returned = entry.recent(offset=0)

        self.assertEqual(expected, returned)

    def testToXML1(self):
        """firmant.datasource.atom.Entry.to_xml
        Convert entry '2009-02-13-sample' to xml"""
        provider = self.get_provider('ToXML1')
        entry    = provider.entry
        e = entry.cast(entries['2009-02-13-sample'])

        xml_entry = xml.etree.Element('entry')
        xml.add_text_subelement(xml_entry, 'title', e.title)
        xml.add_text_subelement(xml_entry, 'updated', RFC3339(e.updated))
        xml.add_text_subelement(xml_entry, 'published', RFC3339(e.published))
        xml_entry.append(e.author.to_xml())
        content = xml.etree.SubElement(xml_entry, 'content')
        content.set('type', 'xhtml')
        div = xml.etree.SubElement(content, 'div')
        div.set('xmlns', 'http://www.w3.org/1999/xhtml')
        div.text = e.content
        link = xml.etree.SubElement(xml_entry, 'link')
        link.set('href', '')
        link.set('rel', 'alternate')
        xml.add_text_subelement(xml_entry, 'id', '')
        xml.add_text_subelement(xml_entry, 'rights', e.rights)
        summary = xml.etree.SubElement(xml_entry, 'summary')
        summary.set('type', 'xhtml')
        div = xml.etree.SubElement(summary, 'div')
        div.set('xmlns', 'http://www.w3.org/1999/xhtml')
        div.text = e.summary
        xml_entry.append(e.category.to_xml())
        expected = xml.etree.tostring(xml_entry)
        returned = xml.etree.tostring(e.to_xml())

        self.assertEqual(expected, returned)

    def testToXML2(self):
        """firmant.datasource.atom.Entry.to_xml
        Convert entry '2009-03-29-markdown' to xml"""
        provider = self.get_provider('ToXML2')
        entry    = provider.entry
        e = entry.cast(entries['2009-03-29-markdown'])

        xml_entry = xml.etree.Element('entry')
        xml.add_text_subelement(xml_entry, 'title', e.title)
        xml.add_text_subelement(xml_entry, 'updated', RFC3339(e.updated))
        xml.add_text_subelement(xml_entry, 'published', RFC3339(e.published))
        xml_entry.append(e.author.to_xml())
        content = xml.etree.SubElement(xml_entry, 'content')
        content.set('type', 'xhtml')
        div = xml.etree.SubElement(content, 'div')
        div.set('xmlns', 'http://www.w3.org/1999/xhtml')
        div.text = e.content
        link = xml.etree.SubElement(xml_entry, 'link')
        link.set('href', '')
        link.set('rel', 'alternate')
        xml.add_text_subelement(xml_entry, 'id', '')
        xml.add_text_subelement(xml_entry, 'rights', e.rights)
        summary = xml.etree.SubElement(xml_entry, 'summary')
        summary.set('type', 'xhtml')
        div = xml.etree.SubElement(summary, 'div')
        div.set('xmlns', 'http://www.w3.org/1999/xhtml')
        div.text = e.summary
        xml_entry.append(e.category.to_xml())
        expected = xml.etree.tostring(xml_entry)
        returned = xml.etree.tostring(e.to_xml())

        self.assertEqual(expected, returned)

    def testList1(self):
        """firmant.datasource.atom.Entry.list
        Get the list of entries published."""
        provider = self.get_provider('List1')
        entry    = provider.entry

        expected = [(datetime.date(2009, 3, 29), 'markdown'),
                    (datetime.date(2009, 3, 17), 'sample'),
                    (datetime.date(2009, 2, 17), 'loren-ipsum'),
                    (datetime.date(2009, 2, 13), 'sample')]
        returned = entry.list()

        self.assertEqual(expected, returned)

    def testListYears1(self):
        """firmant.datasource.atom.Entry.list_years
        Get the list of years for which entries were published."""
        provider = self.get_provider('ListYears1')
        entry    = provider.entry

        expected = [datetime.date(2009, 1, 1)]
        returned = entry.list_years()

        self.assertEqual(expected, returned)

    def testListMonths1(self):
        """firmant.datasource.atom.Entry.list_months
        Get the list of months for which entries were published."""
        provider = self.get_provider('ListMonths1')
        entry    = provider.entry

        expected = [datetime.date(2009, 3, 1),
                    datetime.date(2009, 2, 1)]
        returned = entry.list_months()

        self.assertEqual(expected, returned)

    def testListDays1(self):
        """firmant.datasource.atom.Entry.list_days
        Get the list of days for which entries were published."""
        provider = self.get_provider('Days1')
        entry    = provider.entry

        expected = [datetime.date(2009, 3, 29),
                    datetime.date(2009, 3, 17),
                    datetime.date(2009, 2, 17),
                    datetime.date(2009, 2, 13)]
        returned = entry.list_days()

        self.assertEqual(expected, returned)


class TestFeed(unittest.TestCase):

    def setUp(self):
        """The setup function should alias the AtomProvider class to
        self.provider so that the test functions can access it.  It also must
        setup whatever data is necessary for the test cases to run."""
        not_implemented() # pragma: no cover

    def configuration(self, name):
        """This function should return the settings associated with test
        'name'"""
        not_implemented() # pragma: no cover

    def testBySlug1(self):
        """firmant.datasource.atom.Feed.by_slug
        A feed object should be returned for the given name."""
        provider = self.get_provider('BySlug1')
        feed     = provider.feed

        expected = feeds['general']
        returned = feed.by_slug('general')

        self.assertEqual(expected, returned)

    def testBySlug2(self):
        """firmant.datasource.atom.Feed.by_slug
        A ValueError should be raised for an invalid slug."""
        provider = self.get_provider('BySlug2')
        feed     = provider.feed

        raises   = ValueError
        function = lambda: feed.by_slug('!@#$')

        self.assertRaises(raises, function)

    def testBySlug3(self):
        """firmant.datasource.atom.Feed.by_slug
        Test selecting feed with no entries."""
        provider = self.get_provider('BySlug3')
        feed     = provider.feed

        expected = feeds['empty']
        returned = feed.by_slug('empty')

        self.assertEqual(expected, returned)

    def testDefault(self):
        """firmant.datasource.atom.Feed.default
        The default feed object should be returned."""
        provider = self.get_provider('Default')
        feed     = provider.feed

        expected = feeds['default']
        returned = feed.default()

        self.assertEqual(expected, returned)

    def testToXML1(self):
        """firmant.datasource.atom.Feed.to_xml
        Convert default feed to xml"""
        provider = self.get_provider('ToXML1')
        feed     = provider.feed
        f = feed.cast(feeds['default'])
        f.entries = map(provider.entry.cast, f.entries)

        xml_feed  = xml.etree.Element('feed')
        xml_feed.set('xmlns', 'http://www.w3.org/2005/Atom')
        xml.add_text_subelement(xml_feed, 'generator', 'Firmant')
        xml.add_text_subelement(xml_feed, 'title', f.title)
        xml.add_text_subelement(xml_feed, 'rights', f.rights)
        xml.add_text_subelement(xml_feed, 'updated', RFC3339(f.updated))
        xml.add_text_subelement(xml_feed, 'id', '')
        link = xml.etree.SubElement(xml_feed, 'link')
        link.set('href', '')
        link.set('rel', 'self')
        for entry in f.entries:
            xml_feed.append(entry.to_xml())
        expected = xml.etree.tostring(xml_feed)
        returned = xml.etree.tostring(f.to_xml())

        self.assertEqual(expected, returned)

    def testToXML2(self):
        """firmant.datasource.atom.Feed.to_xml
        Convert feed 'general' to xml"""
        provider = self.get_provider('ToXML2')
        feed     = provider.feed
        f = feed.cast(feeds['general'])
        f.entries = map(provider.entry.cast, f.entries)

        xml_feed  = xml.etree.Element('feed')
        xml_feed.set('xmlns', 'http://www.w3.org/2005/Atom')
        xml.add_text_subelement(xml_feed, 'generator', 'Firmant')
        xml.add_text_subelement(xml_feed, 'title', f.title)
        xml.add_text_subelement(xml_feed, 'rights', f.rights)
        xml.add_text_subelement(xml_feed, 'updated', RFC3339(f.updated))
        xml.add_text_subelement(xml_feed, 'id', '')
        link = xml.etree.SubElement(xml_feed, 'link')
        link.set('href', '')
        link.set('rel', 'self')
        for entry in f.entries:
            xml_feed.append(entry.to_xml())
        expected = xml.etree.tostring(xml_feed)
        returned = xml.etree.tostring(f.to_xml())

        self.assertEqual(expected, returned)


class DummyEntryPermalinkProvider(EntryPermalinkProvider):

    def __init__(self, rc, settings):
        self.rc = rc
        self.settings = settings

    def authoritative(self, entry):
        return ''


class DummyFeedPermalinkProvider(FeedPermalinkProvider):

    def __init__(self, rc, settings):
        self.rc = rc
        self.settings = settings

    def authoritative(self, entry):
        return ''


suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAtomBase))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAtomObjectFilter))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAtomObjectListFilter))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDatetimeFilter))
