import unittest
import datetime
import pytz

from firmant.utils import not_implemented
from firmant.datasource.comments import Comment
from firmant.datasource.comments import CommentEmailValidator
from firmant.datasource.comments import CommentURLValidator
from firmant.datasource import Storage

from test.datasource import create_testSave1
from test.datasource import create_testSave2
from test.datasource import create_testDelete1
from test.datasource import create_testDelete2


comments = {}
comments['rescriva']             = Comment()
comments['rescriva'].name        = 'Robert Escriva'
comments['rescriva'].email       = 'rob@example.org'
comments['rescriva'].url         = 'http://robescriva.com/'
comments['rescriva'].ip          = '128.113.151.53'
comments['rescriva'].useragent   = "Mozilla/5.0 (X11; U; Linux i686; " + \
        "en-US; rv:1.9.0.11) Gecko/2009060308 Ubuntu/9.04 (jaunty) " + \
        "Firefox/3.0.11"
comments['rescriva'].created     = \
        datetime.datetime(2009, 7, 19, 11, 25, 6, tzinfo=pytz.utc)
comments['rescriva'].content     = "Sample comment # 1"
comments['rescriva'].status      = "published"
comments['rescriva'].entry_pkey  = \
        (datetime.date(2009, 7, 18), "comments-enabled")

comments['jsmith']             = Comment()
comments['jsmith'].name        = 'John Smith'
comments['jsmith'].email       = 'john@example.org'
comments['jsmith'].url         = 'http://example.org/'
comments['jsmith'].ip          = '127.0.0.1'
comments['jsmith'].useragent   = 'telnet'
comments['jsmith'].created     = \
        datetime.datetime(2009, 7, 19, 11, 32, 30, tzinfo=pytz.utc)
comments['jsmith'].content     = "Sample comment # 2"
comments['jsmith'].status      = "unpublished"
comments['jsmith'].entry_pkey  = \
        (datetime.date(2009, 7, 18), "comments-enabled")

comments["jsmith'"]             = Comment()
comments["jsmith'"].name        = 'John Smith'
comments["jsmith'"].email       = 'john@example.org'
comments["jsmith'"].url         = 'http://example.org/'
comments["jsmith'"].ip          = '127.0.0.1'
comments["jsmith'"].useragent   = 'telnet'
comments["jsmith'"].created     = \
        datetime.datetime(2009, 7, 19, 11, 32, 30, tzinfo=pytz.utc)
comments["jsmith'"].content     = "Sample comment # 2 edited"
comments["jsmith'"].status      = "unpublished"
comments["jsmith'"].entry_pkey  = \
        (datetime.date(2009, 7, 18), "comments-enabled")

comments['spammer']             = Comment()
comments['spammer'].name        = "Spammy Spammer"
comments['spammer'].email       = "spam@mail.ru"
comments['spammer'].url         = "http://mail.ru/"
comments['spammer'].ip          = '217.69.128.41'
comments['spammer'].useragent   = 'Lynx/2.8.7dev.11 ' + \
        'libwww-FM/2.14 SSL-MM/1.4.1'
comments['spammer'].created     = \
        datetime.datetime(2009, 7, 19, 11, 37, 34, tzinfo=pytz.utc)
comments['spammer'].content     = 'Enhance your ...'
comments['spammer'].status      = 'spam'
comments['spammer'].entry_pkey  = \
        (datetime.date(2009, 7, 18), "comments-enabled")

comments['rescriva2']             = Comment()
comments['rescriva2'].name        = 'Robert Escriva'
comments['rescriva2'].email       = 'rob@example.org'
comments['rescriva2'].url         = 'http://robescriva.com/'
comments['rescriva2'].ip          = '128.113.151.53'
comments['rescriva2'].useragent   = "Mozilla/5.0 (X11; U; Linux i686; " + \
        "en-US; rv:1.9.0.11) Gecko/2009060308 Ubuntu/9.04 (jaunty) " + \
        "Firefox/3.0.11"
comments['rescriva2'].created     = \
        datetime.datetime(2009, 7, 18, 11, 25, 6, tzinfo=pytz.utc)
comments['rescriva2'].content     = "Sample comment # 1"
comments['rescriva2'].status      = "published"
comments['rescriva2'].entry_pkey  = \
        (datetime.date(2009, 7, 18), "comments-enabled")

comments['DNE']             = Comment()
comments['DNE'].name        = 'Does Not Exist'
comments['DNE'].email       = ''
comments['DNE'].url         = ''
comments['DNE'].ip          = ''
comments['DNE'].useragent   = ''
comments['DNE'].created     = \
        datetime.datetime(2009, 9, 12, 11, 25, 6, tzinfo=pytz.utc)
comments['DNE'].content     = ''
comments['DNE'].status      = 'published'
comments['DNE'].entry_pkey  = \
        (datetime.date(2009, 7, 18), "comments-enabled")


class TestCommentProvider(unittest.TestCase):

    def testForEntry1(self):
        '''firmant.datasource.comments.CommentProvider.for_entry
        When status is none, and the specified entry has comments, all comments
        for the entry should be returned.'''
        provider = self.provider

        expected = [comments['rescriva2'],
                    comments['rescriva'],
                    comments['jsmith'],
                    comments['spammer']]
        returned = provider.for_entry(None, 'comments-enabled', 2009, 7, 18)

        self.assertEqual(expected, returned)

    def testForEntry2(self):
        '''firmant.datasource.comments.CommentProvider.for_entry
        When status is none, and the specified entry has comments, all comments
        for the entry should be returned.'''
        provider = self.provider

        expected = [comments['rescriva2'],
                    comments['rescriva'],
                    comments['jsmith'],
                    comments['spammer']]
        returned = provider.for_entry(None, 'comments-enabled',
                '2009', '7', '18')

        self.assertEqual(expected, returned)

    def testForEntry3(self):
        '''firmant.datasource.comments.CommentProvider.for_entry
        When status is 'spam', and the specified entry has comments, all comments
        classified as 'spam' should be returned.'''
        provider = self.provider

        expected = [comments['spammer']]
        returned = provider.for_entry('spam', 'comments-enabled', 2009, 7, 18)

        self.assertEqual(expected, returned)

    def testForEntry4(self):
        '''firmant.datasource.comments.CommentProvider.for_entry
        When status is 'published', and the specified entry has comments, all
        comments classified as 'published' should be returned.'''
        provider = self.provider

        expected = [comments['rescriva2'],
                    comments['rescriva']]
        returned = provider.for_entry('published', 'comments-enabled', 2009, 7, 18)

        self.assertEqual(expected, returned)

    def testForEntry5(self):
        '''firmant.datasource.comments.CommentProvider.for_entry
        When status is None, and the specified entry doesn't have comments, the
        result should be [].  Note that the entry need not exist if AtomProvider
        is queried.  That logic is left to the AtomProvider.  If the two just
        happen to have that foreign key condition enforced, all the better.'''
        provider = self.provider

        expected = []
        returned = provider.for_entry(None, 'comments-noexist', 2009, 7, 18)

        self.assertEqual(expected, returned)

    def testForEntry6(self):
        '''firmant.datasource.comments.CommentProvider.for_entry
        When status doesn't exist for the given entry, an empty list should be
        returned.'''
        provider = self.provider

        expected = []
        returned = provider.for_entry('noexist', 'comments-enabled', 2009, 7, 18)

        self.assertEqual(expected, returned)

    def testForEntry7(self):
        '''firmant.datasource.comments.CommentProvider.for_entry
        When status is '', a ValueError should be raised.'''
        provider = self.provider

        raised   = ValueError
        function = lambda: provider.for_entry('', 'comments-enabled', 2009, 7, 18)

        self.assertRaises(raised, function)

    def testForEntry8(self):
        '''firmant.datasource.comments.CommentProvider.for_entry
        When date is invalid, a ValueError should be raised.'''
        provider = self.provider

        raised   = ValueError
        function = lambda: provider.for_entry('spam', 'comments', 2009, 2, 31)

        self.assertRaises(raised, function)

    def testForEntry9(self):
        '''firmant.datasource.comments.CommentProvider.for_entry
        When year is invalid, a ValueError should be raised.'''
        provider = self.provider

        raised   = ValueError
        function = lambda: provider.for_entry('spam', 'comments', '20o9', 2, 18)

        self.assertRaises(raised, function)

    def testForEntry10(self):
        '''firmant.datasource.comments.CommentProvider.for_entry
        When month is invalid, a ValueError should be raised.'''
        provider = self.provider

        raised   = ValueError
        function = lambda: provider.for_entry('spam', 'comments', 2009, 'e', 18)

        self.assertRaises(raised, function)

    def testForEntry11(self):
        '''firmant.datasource.comments.CommentProvider.for_entry
        When day is invalid, a ValueError should be raised.'''
        provider = self.provider

        raised   = ValueError
        function = lambda: provider.for_entry('spam', 'comments', 2009, 2, '1$')

        self.assertRaises(raised, function)

    testDelete1 = create_testDelete1(comments["jsmith'"],
        '''firmant.datasource.comments.CommentProvider.delete
        Use a non-existent comment object.  When delete is called, it should
        return ExistenceError.''')

    testDelete2 = create_testDelete2(comments['rescriva2'],
        '''firmant.datasource.comments.CommentProvider.delete
        Delete a comment known to be in the system.  Should throw no errors.''',
        [comments['rescriva']], 'for_entry', 'published', 'comments-enabled',
        2009, 7, 18)

    testSave1 = create_testSave1(comments['DNE'],
        '''firmant.datasource.comments.CommentProvider.save
        Save a comment successfully.''',
        [comments['rescriva2'], comments['rescriva'], comments['DNE']],
        'for_entry', 'published', 'comments-enabled', 2009, 7, 18)

    testSave2 = create_testSave2(comments['rescriva'],
        '''firmant.datasource.comments.CommentProvider.save
        Save a comment object identical to an already saved object.  Should
        throw a UniqueViolationError.''')


class TestComment(unittest.TestCase):

    def testEqual1(self):
        '''firmant.datasource.comments.Comment.equal
        Test two equal comments.'''

        a = comments['rescriva']
        b = comments['rescriva']

        self.assertTrue(a == b)
        self.assertTrue(not (a != b))

    def testEqual2(self):
        '''firmant.datasource.comments.Comment.equal
        Test two comments with all attrs, but the are unequal.'''
        a             = Comment()
        a.name        = 'Escriva, Robert'
        a.email       = 'rob@example.org'
        a.url         = 'http://robescriva.com/'
        a.ip          = '128.113.151.53'
        a.useragent   = "Mozilla/5.0 (X11; U; Linux i686; " + \
            "en-US; rv:1.9.0.11) Gecko/2009060308 Ubuntu/9.04 (jaunty) " + \
            "Firefox/3.0.11"
        a.created     = \
            datetime.datetime(2009, 7, 19, 11, 25, 6, tzinfo=pytz.utc)
        a.content     = "Sample comment # 1"
        a.status      = "published"
        a.entry_pkey  = \
            (datetime.date(2009, 7, 18), "comments-enabled")

        b = comments['rescriva']

        self.assertTrue(a != b)
        self.assertTrue(not (a == b))

    def testEqual3(self):
        '''firmant.datasource.comments.Comment.equal
        Test two comments with all attrs, but the are unequal.'''
        a             = Comment()
        b = comments['rescriva']

        self.assertTrue(a != b)
        self.assertTrue(not (a == b))

        self.assertTrue(b != a)
        self.assertTrue(not (b == a))


class TestCommentEmailValidator(unittest.TestCase):

    def setUp(self):
        self.validator = CommentEmailValidator(None, None)

    def testValidEmail(self):
        '''firmant.datasource.comments.CommentEmailValidator
        Check comment with valid email.'''
        c = Comment()
        c.email = 'rob@example.org'
        self.assertEqual(True, self.validator.is_valid(c))

    def testInvalidEmail(self):
        '''firmant.datasource.comments.CommentEmailValidator
        Check comment with invalid email.'''
        c = Comment()
        c.email = 'rob@localhost'
        self.assertEqual(True, self.validator.is_valid(c))


class TestCommentURLValidator(unittest.TestCase):

    def setUp(self):
        self.validator = CommentURLValidator(None, None)

    def testValidURL1(self):
        '''firmant.datasource.comments.CommentURLValidator
        Check valid url'''
        c = Comment()
        c.url = 'http://example.org'
        self.assertEqual(True, self.validator.is_valid(c))

    def testValidURL2(self):
        '''firmant.datasource.comments.CommentURLValidator
        Check valid url'''
        c = Comment()
        c.url = 'http://exampledotorg'
        self.assertEqual(True, self.validator.is_valid(c))

    def testInvalidURL(self):
        '''firmant.datasource.comments.CommentURLValidator
        Check ivalid url'''
        c = Comment()
        c.url = 'example.org/foo/bar'
        self.assertEqual(False, self.validator.is_valid(c))


from test import add_test
suite = unittest.TestSuite()
add_test(suite, TestComment)
add_test(suite, TestCommentEmailValidator)
add_test(suite, TestCommentURLValidator)
