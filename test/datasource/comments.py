import unittest
import datetime
import pytz

from firmant.utils import not_implemented
from firmant.datasource.comments import Comment
from firmant.datasource import Storage

from test.datasource import create_testSave1


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

    def testDelete1(self):
        '''firmant.datasource.comments.CommentProvider.delete
        Use a non-existent comment object.  When delete is called, it should
        return ExistenceError.'''
        provider = self.provider
        c        = comments["jsmith'"]

        raised   = Storage.DoesNotExistError
        function = lambda: provider.delete(c)

        self.assertRaises(raised, function)

    def testDelete2(self):
        '''firmant.datasource.comments.CommentProvider.delete
        Delete a comment known to be in the system.  Should throw no errors.'''
        provider = self.provider
        todelete = comments['rescriva2']

        expected = None
        returned = provider.delete(todelete)
        self.assertEqual(expected, returned)

        expected = [comments['rescriva']]
        returned = provider.for_entry('published', 'comments-enabled', 2009, 7, 18)
        self.assertEqual(expected, returned)

    testSave1 = create_testSave1(comments['DNE'],
        '''firmant.datasource.comments.CommentProvider.save
        Save a comment successfully.''',
        [comments['rescriva2'], comments['rescriva'], comments['DNE']],
        'for_entry', 'published', 'comments-enabled', 2009, 7, 18)

    def testSave2(self):
        '''firmant.datasource.comments.CommentProvider.save
        Save a comment object identical to an already saved object.  Should
        throw a UniqueViolationError.'''
        provider = self.provider

        raised   = Storage.UniqueViolationError
        function = lambda: provider.save(comments['rescriva'])

        self.assertRaises(raised, function)
