import unittest
import datetime
import pytz
import shutil

from firmant.plugins.datasource.flatfile.comments import FlatfileCommentProvider

from test.datasource.comments import TestCommentProvider as BaseTestCommentProvider
from test.datasource.comments import comments


class TestCommentProvider(BaseTestCommentProvider):

    def setUp(self):
        settings = {'FLATFILE_BASE': 'checkout/'}
        self.provider = FlatfileCommentProvider(None, settings)

    def testLoadOne1(self):
        '''firmant.plugins.datasource.flatfile.comments.FlatfileCommentProvider._load_one'''
        status     = 'published'
        entry_pkey = (datetime.date(2009, 7, 18), 'comments-enabled')
        created    = 1248002706
        id         = 'ad9d83756efde485089bdf27119fe37c3cc9da6d'

        expected = comments['rescriva']
        returned = self.provider._load_one(status, entry_pkey, created, id)

        self.assertEqual(expected, returned)

    def testLoadOne2(self):
        '''firmant.plugins.datasource.flatfile.comments.FlatfileCommentProvider._load_one'''
        status     = 'unpublished'
        entry_pkey = (datetime.date(2009, 7, 18), 'comments-enabled')
        created    = 1248003150
        id         = '0279dd3ca037767782fed2e788ab68da40b2a445'

        expected = comments['jsmith']
        returned = self.provider._load_one(status, entry_pkey, created, id)

        self.assertEqual(expected, returned)

    def testLoadOne3(self):
        '''firmant.plugins.datasource.flatfile.comments.FlatfileCommentProvider._load_one'''
        status     = 'spam'
        entry_pkey = (datetime.date(2009, 7, 18), 'comments-enabled')
        created    = 1248003454
        id         = 'e6f4aadf75637bb4649a9a12eee7f32ee9b81a1c'

        expected = comments['spammer']
        returned = self.provider._load_one(status, entry_pkey, created, id)

        self.assertEqual(expected, returned)

    def testLoadOne4(self):
        '''firmant.plugins.datasource.flatfile.comments.FlatfileCommentProvider._load_one'''
        status     = 'published'
        entry_pkey = (datetime.date(2009, 7, 18), 'comments-enabled')
        created    = 1247916306
        id         = 'ad9d83756efde485089bdf27119fe37c3cc9da6d'

        expected = comments['rescriva2']
        returned = self.provider._load_one(status, entry_pkey, created, id)

        self.assertEqual(expected, returned)

    def testList1(self):
        '''firmant.plugins.datasource.flatfile.comments.FlatfileCommentProvider._list'''
        expected = [('published',
                     (datetime.date(2009, 7, 18), 'comments-enabled'),
                     1247916306, 'ad9d83756efde485089bdf27119fe37c3cc9da6d'),
                    ('published',
                     (datetime.date(2009, 7, 18), 'comments-enabled'),
                     1248002706, 'ad9d83756efde485089bdf27119fe37c3cc9da6d'),
                    ('unpublished',
                     (datetime.date(2009, 7, 18), 'comments-enabled'),
                     1248003150, '0279dd3ca037767782fed2e788ab68da40b2a445'),
                    ('spam',
                     (datetime.date(2009, 7, 18), 'comments-enabled'),
                     1248003454, 'e6f4aadf75637bb4649a9a12eee7f32ee9b81a1c')]
        returned = self.provider._list()

        self.assertEqual(expected, returned)


from test import add_test
suite = unittest.TestSuite()
add_test(suite, TestCommentProvider)
