import unittest
from firmant.resolver import RegexURLLink
from test.data.views import bymonth
from test.data.views import emptyargs


class TestRegexURLLink(unittest.TestCase):

    def testinit(self):
        '''
        Tests the case where the URL's matches, the callable's kwargs are all
        blank.
        '''
        RegexURLLink('homepage/', 'test.data.views.emptyargs', {})
        '''
        Tests the case where the URL's matches, and the callable's kwargs are
        blank.  The kwargs dictionary contains arguments.  This should
        throw an exception.
        '''
        self.assertRaises(TypeError, RegexURLLink, 'homepage/',
                'test.data.views.emptyargs', {'this': 'fails'})
        '''
        Test the case where the URL's matches, and the kwargs dictionary are
        both blank.  The callable has arguments.  This should throw an
        exception.
        '''
        self.assertRaises(TypeError, RegexURLLink, 'homepage/',
                'test.data.views.someargs', {})
        '''
        Test the case where the callable's kwargs and the kwargs dictionary are
        both blank.  The URL has extra matches.  This should throw an
        exception.
        '''
        self.assertRaises(TypeError, RegexURLLink, '(?P<where>\w+)/',
                'test.data.views.emptyargs', {})
        '''
        Test the case where the URL matches and kwargs dictionary are not
        equivalent to the callable's kwargs.
        '''
        self.assertRaises(TypeError, RegexURLLink, '(?P<where>\w+)/',
                'test.data.views.bymonth', {'hello': 'world'})
        '''
        Test a valid case without the kwargs dictionary.
        '''
        RegexURLLink('(?P<year>\d{4})/(?P<month>\d{2})/',
                'test.data.views.bymonth')

    def testrlookup(self):
        lookup1, lookup2, lookup3 = self.__cases()
        self.assertRaises(TypeError, lookup1.rlookup, {'foo': 1, 'bar': 1})
        self.assertRaises(TypeError, lookup1.rlookup, {'foo': '1', 'bar': '1'})
        self.assertRaises(TypeError, lookup1.rlookup, {})
        self.assertRaises(TypeError, lookup1.rlookup,
                {'year': '2008', 'month': '11', 'day': '27'})
        self.assertEqual('2008/11/', lookup1.rlookup('test.data.views.bymonth',
                    {'year': '2008', 'month': '11'}))
        self.assertRaises(TypeError, lookup2.rlookup, {'foo': '1', 'bar': '1'})
        self.assertEqual('2008/11/', lookup2.rlookup('test.data.views.bymonth',
                    {'year': '2008', 'month': '11'}))
        self.assertRaises(TypeError, lookup3.rlookup,
                'test.data.views.emptyargs', {'foo': 'bar'})
        self.assertEqual('hello/world/',
                lookup3.rlookup('test.data.views.emptyargs', {}))

    def testlookup(self):
        lookup1, lookup2, lookup3 = self.__cases()
        self.assertRaises(TypeError, lookup1.lookup, '200a/10/')
        self.assertRaises(TypeError, lookup1.lookup, '2008/1a/')
        self.assertRaises(TypeError, lookup1.lookup, 'foobar/')
        self.assertEqual((bymonth, {'year': '2008', 'month': '10'}),
                lookup1.lookup('2008/10/'))
        self.assertRaises(TypeError, lookup2.lookup, 'foobar/')
        self.assertRaises(TypeError, lookup2.lookup, '2008/10/')
        self.assertEqual((bymonth, {'year': '2008', 'month': '11'}),
                lookup2.lookup('foo/bar/'))
        self.assertRaises(TypeError, lookup3.lookup, 'foobar/')
        self.assertEqual((emptyargs, {}), lookup3.lookup('hello/world/'))

    def testadd_prefix(self):
        lookup1 = RegexURLLink('^(?P<year>\d{4})/(?P<month>\d{2})/$',
                'test.data.views.bymonth')
        lookup2 = RegexURLLink('^(?P<year>\d{4})/(?P<month>\d{2})/$',
                'test.data.views.bymonth')
        lookup3 = RegexURLLink('(?P<year>\d{4})/(?P<month>\d{2})/$',
                'test.data.views.bymonth')
        lookup4 = RegexURLLink('(?P<year>\d{4})/(?P<month>\d{2})/$',
                'test.data.views.bymonth')

        lookup1.add_prefix('date')
        self.assertEqual(r'^date(?P<year>\d{4})/(?P<month>\d{2})/$',
                lookup1.matches())
        lookup2.add_prefix('date/')
        self.assertEqual(r'^date/(?P<year>\d{4})/(?P<month>\d{2})/$',
                lookup2.matches())
        lookup3.add_prefix('date')
        self.assertEqual(r'date(?P<year>\d{4})/(?P<month>\d{2})/$',
                lookup3.matches())
        lookup4.add_prefix('date/')
        self.assertEqual(r'date/(?P<year>\d{4})/(?P<month>\d{2})/$',
                lookup4.matches())

    def testparameters(self):
        lookup1, lookup2, lookup3 = self.__cases()
        self.assertEqual(set(['year', 'month']), lookup1.parameters())
        self.assertEqual(set(['year', 'month']), lookup2.parameters())
        self.assertEqual(set([]), lookup3.parameters())

    def __cases(self):
        lookup1 = RegexURLLink('^(?P<year>\d{4})/(?P<month>\d{2})/$',
                'test.data.views.bymonth')
        lookup2 = RegexURLLink('^foo/bar/$', 'test.data.views.bymonth',
                {'year': '2008', 'month': '11'})
        lookup3 = RegexURLLink('^hello/world/$', 'test.data.views.emptyargs',
                {})
        return lookup1, lookup2, lookup3


suite = unittest.TestLoader().loadTestsFromTestCase(TestRegexURLLink)
